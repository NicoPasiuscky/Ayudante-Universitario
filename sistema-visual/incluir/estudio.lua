--[[ estudio.lua - filtro de Pandoc del sistema visual v4 (3 formatos y 2 modos de resumen).

Uso:  pandoc ... --lua-filter=incluir/estudio.lua -M formato=completo|a4|diapositivas -M modo=extenso|corto
  formato  completo (HTML para pantalla, movil y escritorio), a4 (hoja para imprimir, Paged.js),
           diapositivas (una idea por diapositiva, con navegacion propia)
  modo     extenso (explicativo, para empezar a estudiar; por defecto) o
           corto (para repasar: definicion en una linea, formula clave, ojo, mini ejemplo)

Metadatos del Markdown:
  materia, unidad              encabezado "Materia | Unidad N" (la cabeza de hoja del A4 ya no lleva sigla; sigla queda solo como data-sigla)
  indice: true                 indice despues del encabezado (con enlaces; en A4, lista simple sin enlaces).
                               Solo formato completo o a4 y modo extenso; en los demas se ignora y se avisa
  modo: corto                  sin sintesis por seccion, sin glosario ni demostraciones; agrega ::: ojo
  practica: true               activa los componentes de practica (apagados por defecto)
  sintesis: false              oculta los resumenes breves al pie de seccion (activados por defecto en modo extenso)
  espejo: false                (o imprime: false) solo formato a4: si no se imprime, margenes IGUALES en todas las hojas
                               (izquierdo 20, derecho 10 mm) y "Hoja n de N" siempre del mismo lado; por defecto,
                               espejado a doble faz (ver incluir/espejo.lua)

Que entiende, en orden de documento:
  # Titulo {unidad=3}                 apertura de unidad: numeral grande en azul y titulo
  ## Seccion {#sec:id}                numerada "3.1", el numero cuelga a la izquierda
  ## Seccion {-}                      sin numero (Glosario)
  ### Subtitulo                       segundo nivel, sin numero
  ::: {.definicion titulo="..."}      "Definicion 3.1 (...)." en linea, sin caja
      tambien .ejemplo .propiedad (misma numeracion)
  ::: resolucion  (dentro de un ejemplo)   plegable "Ver la resolucion"; en A4, abierto
  ::: {.demostracion titulo="..."}    toda plegable; en A4, abierta
  ::: clave                           recuadro de formula clave (el unico recuadro)
  ::: {.ecuacion #ec:id}  $$...$$     numero "(3.1)" a la derecha
  ::: sintesis                        resumen breve al pie de la seccion, rotulo colgado
  ::: errores                         errores frecuentes (modo extenso): SOLO los que son reales, nunca inventados
  ::: ojo                             error tipico en una o dos lineas, con aspa roja (modo corto)
  ---  o  ::: corte  (vacio)          solo en diapositivas: corta la diapositiva ahi; en los otros formatos se ignora
  ### Subtitulo                       en diapositivas abre una diapositiva nueva dentro de la seccion
  ::: glosario  + lista de definicion glosario de la unidad
  ::: margen                          nota al margen sin numero, junto al bloque siguiente
  ^[texto]                            nota al margen numerada, junto a su parrafo
  ![epigrafe](x.svg){#fig:id}         "Figura 3-1."; el SVG va en linea (usa letra y colores)
  ::: {#tbl:id} + tabla "Table: ..."  "Tabla 3-1."
  [](#sec:id) [](#fig:id) [](#tbl:id) [](#ec:id) [](#def:id)   referencia cruzada
  Solo con practica: true (si no, se quitan y se avisa por la consola):
  ::: previas / ::: proba / ::: respuestas-practica
]]

local script_dir = (PANDOC_SCRIPT_FILE or ""):match("^(.*)[/\\][^/\\]*$") or "."
local espejo = dofile(script_dir .. "/espejo.lua")   -- margenes espejados o iguales (-M espejo=false)
local formato = "completo"
local modo = "extenso"
local unidad = "1"
local practica = false
local con_indice = false
local con_sintesis = true
local c = {}
local refs = {}
local avisos = {}

local function reiniciar()
  c = {sec = 0, enun = 0, fig = 0, tbl = 0, ec = 0, nota = 0}
end
reiniciar()

local ENUN = {definicion = "Definición", ejemplo = "Ejemplo", propiedad = "Propiedad",
              demostracion = "Demostración"}
local PRACTICA = {previas = "Antes de leer", proba = "Probá sin mirar",
                  ["respuestas-practica"] = "Respuestas de la práctica"}

local function tiene(el, clase)
  for _, k in ipairs(el.classes) do if k == clase then return true end end
  return false
end

local function texto(s) return pandoc.Inlines(s) end

local function anteponer(bloques, ins)
  local b = bloques[1]
  if b and (b.t == "Para" or b.t == "Plain") then
    local nuevo = pandoc.Inlines({})
    nuevo:extend(ins)
    nuevo:insert(pandoc.Space())
    nuevo:extend(b.content)
    b.content = nuevo
  else
    bloques:insert(1, pandoc.Plain(ins))
  end
  return bloques
end

local function svg_en_linea(src)
  local f = io.open(src, "rb")
  if not f then return nil end
  local s = f:read("a"); f:close()
  s = s:gsub("<%?xml.-%?>", ""):gsub("<!DOCTYPE.->", ""):gsub("<!%-%-.-%-%->", "")
  return s
end

local function raw(s) return pandoc.RawBlock("html", s) end

-- Rotulo colgado en la sangria izquierda (sintesis, practica): no es un
-- encabezado de caja, es texto al costado del bloque (regla 10).
local function colgado(t)
  return pandoc.Span(texto(t), {class = "colgado"})
end

------------------------------------------------------------------------
-- Pasada 1: numeracion
------------------------------------------------------------------------
local numerar = {
  traverse = "topdown",

  Header = function(h)
    if h.level == 1 then
      if h.attributes.unidad then unidad = h.attributes.unidad end
      reiniciar()
      if not tiene(h, "unnumbered") then
        h.content:insert(1, pandoc.Span({pandoc.Str(unidad)}, {class = "numeral"}))
      end
      h.classes:insert("apertura")
      h.attributes.unidad = nil
      return h
    end
    if h.level == 2 and not tiene(h, "unnumbered") then
      c.sec = c.sec + 1
      local n = unidad .. "." .. c.sec
      h.content:insert(1, pandoc.Space())
      h.content:insert(1, pandoc.Span({pandoc.Str(n)}, {class = "num"}))
      if h.identifier ~= "" then refs[h.identifier] = "sección " .. n end
      return h
    end
  end,

  Div = function(d)
    for clase, nombre in pairs(ENUN) do
      if tiene(d, clase) then
        c.enun = c.enun + 1
        local n = unidad .. "." .. c.enun
        local ins = pandoc.Inlines({pandoc.Span(texto(nombre .. " " .. n), {class = "rotulo"})})
        local t = d.attributes.titulo
        if t then
          ins:insert(pandoc.Space())
          ins:extend(texto("(" .. t .. ")."))
        else
          ins[1].content:insert(pandoc.Str("."))
        end
        if clase == "demostracion" then
          d.attributes.resumen = pandoc.utils.stringify(ins)
        else
          d.content = anteponer(d.content, ins)
        end
        d.classes:insert("enunciado")
        d.attributes.titulo = nil
        if d.identifier ~= "" then refs[d.identifier] = string.lower(nombre) .. " " .. n end
        return d
      end
    end
    if d.identifier:match("^tbl:") then
      c.tbl = c.tbl + 1
      local n = unidad .. "-" .. c.tbl
      refs[d.identifier] = "tabla " .. n
      d.classes:insert("tabla")
      d = d:walk({Table = function(t)
        local rot = pandoc.Span(texto("Tabla " .. n .. "."), {class = "rotulo"})
        if #t.caption.long == 0 then
          t.caption.long = pandoc.Blocks({pandoc.Plain({rot})})
        else
          anteponer(t.caption.long, {rot})
        end
        return t
      end})
      return d
    end
    if tiene(d, "ecuacion") then
      c.ec = c.ec + 1
      local n = unidad .. "." .. c.ec
      if d.identifier ~= "" then refs[d.identifier] = "ecuación (" .. n .. ")" end
      local puesto = false
      d = d:walk({Para = function(p)
        if puesto then return nil end
        puesto = true
        p.content:insert(pandoc.Span({pandoc.Str("(" .. n .. ")")}, {class = "ec-num"}))
        return p
      end})
      return d
    end
  end,

  Figure = function(fig)
    c.fig = c.fig + 1
    local n = unidad .. "-" .. c.fig
    if fig.identifier ~= "" then refs[fig.identifier] = "figura " .. n end
    local rot = pandoc.Span(texto("Figura " .. n .. "."), {class = "rotulo"})
    if #fig.caption.long == 0 then
      fig.caption.long = pandoc.Blocks({pandoc.Plain({rot})})
    else
      anteponer(fig.caption.long, {rot})
    end
    fig.content = fig.content:walk({Image = function(img)
      if img.src:match("%.svg$") then
        local s = svg_en_linea(img.src)
        if s then return pandoc.RawInline("html", s) end
      end
    end})
    return fig
  end,

  Note = function(nt)
    c.nota = c.nota + 1
    local n = tostring(c.nota)
    local cuerpo = pandoc.Inlines({pandoc.Span({pandoc.Str(n)}, {class = "nota-num"}), pandoc.Space()})
    cuerpo:extend(pandoc.utils.blocks_to_inlines(nt.content))
    return {pandoc.Span({pandoc.Str(n)}, {class = "nota-ref"}),
            pandoc.Span(cuerpo, {class = "nota-margen"})}
  end,
}

------------------------------------------------------------------------
-- Pasada 2: cada nota al margen viaja pegada a su bloque. Se arma un par
-- (texto | notas) que en A4 no se parte entre hojas: asi la nota nunca
-- queda en otra hoja que su parrafo (problema de la direccion A).
------------------------------------------------------------------------
local function par(bloque, notas)
  local d = pandoc.Div({pandoc.Div({bloque}, {class = "par-texto"}),
                        pandoc.Div(notas, {class = "par-notas", role = "note"})}, {class = "con-nota"})
  return d
end

local function sacar_notas(b)
  if b.t ~= "Para" and b.t ~= "Plain" then return nil end
  local notas = pandoc.Blocks({})
  local resto = pandoc.Inlines({})
  for _, il in ipairs(b.content) do
    if il.t == "Span" and tiene(il, "nota-margen") then
      notas:insert(pandoc.Div({pandoc.Plain(il.content)}, {class = "nota"}))
    else
      resto:insert(il)
    end
  end
  if #notas == 0 then return nil end
  b.content = resto
  return notas
end

local emparejar = {
  Blocks = function(bl)
    local out = pandoc.Blocks({})
    local pendiente = nil   -- notas de un ::: margen esperando su bloque
    for _, b in ipairs(bl) do
      if b.t == "Div" and tiene(b, "margen") then
        pendiente = pendiente or pandoc.Blocks({})
        pendiente:insert(pandoc.Div(b.content, {class = "nota"}))
      else
        local propias = sacar_notas(b)
        local notas = pandoc.Blocks({})
        if pendiente and b.t ~= "Header" then notas:extend(pendiente); pendiente = nil end
        if propias then notas:extend(propias) end
        if pendiente and b.t == "Header" then
          -- una nota suelta antes de un titulo: se queda con el bloque anterior
          local prev = out[#out]
          if prev then out[#out] = par(prev, pendiente) end
          pendiente = nil
        end
        if #notas > 0 then out:insert(par(b, notas)) else out:insert(b) end
      end
    end
    if pendiente then
      local prev = out[#out]
      if prev then out[#out] = par(prev, pendiente) else out:extend(pendiente) end
    end
    return out
  end,
}

------------------------------------------------------------------------
-- Pasada 3: referencias cruzadas, plegables, practica y sintesis
------------------------------------------------------------------------
-- En pantalla, <details> plegado (al imprimir desde el navegador,
-- incluir/tema.html los abre). En la hoja A4 no hay nada que desplegar:
-- el contenido va abierto, con su rotulo en linea.
local function plegable(resumen, contenido, clase, rotulo_impreso)
  if formato == "a4" then
    local d = pandoc.Div(contenido, {class = clase .. " resolucion-impresa"})
    if rotulo_impreso then
      d.content = anteponer(d.content, {pandoc.Span(texto(rotulo_impreso), {class = "rotulo-res"})})
    end
    return pandoc.Blocks({d})
  end
  local bl = pandoc.Blocks({raw('<details class="plegable ' .. clase .. '">'),
                            raw("<summary>" .. resumen .. "</summary>")})
  bl:extend(contenido)
  bl:insert(raw("</details>"))
  return bl
end

local resolver = {
  Link = function(l)
    local id = l.target:match("^#(.+)$")
    if id and #l.content == 0 then
      if refs[id] then
        l.content = texto(refs[id])
        l.classes:insert("ref")
        return l
      end
      table.insert(avisos, "referencia sin destino: #" .. id)
    end
  end,
  Div = function(d)
    for clase, nombre in pairs(PRACTICA) do
      if tiene(d, clase) then
        if not practica then
          table.insert(avisos, "componente de práctica omitido (activar con practica: true): " .. clase)
          return {}
        end
        d.classes:insert("practica")
        local aviso = pandoc.Para({colgado("Práctica"), pandoc.Emph(texto(nombre .. ".")), pandoc.Space(),
                                   pandoc.Span(texto("Material de práctica, no proviene de la fuente."), {class = "aviso-practica"})})
        d.content:insert(1, aviso)
        if clase == "respuestas-practica" and formato ~= "a4" then
          return plegable("Ver las respuestas de la práctica", {d}, "practica-plegable")
        end
        if clase == "respuestas-practica" then d.classes:insert("hoja-aparte") end
        return d
      end
    end
    if tiene(d, "sintesis") then
      if not con_sintesis then return {} end
      d.content = anteponer(d.content, {colgado("Síntesis")})
      return d
    end
    if tiene(d, "ojo") then
      -- modo corto: el error tipico, en una o dos lineas, con aspa roja y la palabra
      d.content = anteponer(d.content, {pandoc.Span(texto("Ojo."), {class = "rotulo"})})
      return d
    end
    if tiene(d, "errores") then
      d.content:insert(1, pandoc.Para({pandoc.Span(texto("Errores frecuentes"), {class = "rotulo-bloque"})}))
      d.attributes["aria-label"] = "Errores frecuentes"
      return d
    end
    if tiene(d, "resolucion") then
      return plegable("Ver la resolución", d.content, "resolucion", "Resolución.")
    end
    if tiene(d, "demostracion") then
      local r = d.attributes.resumen or "Demostración"
      d.attributes.resumen = nil
      if formato == "a4" then
        d.content = anteponer(d.content, {pandoc.Span(texto(r), {class = "rotulo"})})
        return d
      end
      return plegable(r, {d}, "demostracion")
    end
  end,
}

-- Aviso si una seccion numerada no tiene su sintesis (activada por defecto)
local function revisar_sintesis(blocks)
  local actual, tiene_s = nil, true
  local function cerrar()
    if actual and not tiene_s then table.insert(avisos, "la sección «" .. actual .. "» no tiene ::: sintesis") end
  end
  for _, b in ipairs(blocks) do
    if b.t == "Header" and b.level <= 2 then
      cerrar()
      actual, tiene_s = nil, true
      if b.level == 2 and not tiene(b, "unnumbered") then actual, tiene_s = pandoc.utils.stringify(b), false end
    elseif b.t == "Div" and tiene(b, "sintesis") then
      tiene_s = true
    end
  end
  cerrar()
end

-- Indice propio (-M indice=true), en lugar de --toc: va despues del
-- encabezado y, en la hoja A4, sin enlaces (lista simple de titulos, regla
-- de DESIGN-SYSTEM.md; un enlace no sirve en papel).
function indice(blocks)
  local items = {}
  for _, b in ipairs(blocks) do
    if b.t == "Header" and b.level <= 2 then
      local nivel = b.level == 1 and "i-unidad" or "i-seccion"
      local ins = b.content:clone()
      if formato ~= "a4" and b.identifier ~= "" then
        ins = pandoc.Inlines({pandoc.Link(ins, "#" .. b.identifier)})
      end
      table.insert(items, pandoc.Div({pandoc.Plain(ins)}, {class = nivel}))
    end
  end
  if #items == 0 then return {} end
  local cab = pandoc.Para({pandoc.Span(texto("Índice"), {class = "rotulo-bloque"})})
  local cuerpo = pandoc.Blocks({cab})
  cuerpo:extend(items)
  return pandoc.Blocks({raw('<nav class="indice" aria-label="Índice">'), pandoc.Div(cuerpo), raw("</nav>")})
end

------------------------------------------------------------------------
-- Diapositivas: cada # abre la portada, cada ## una diapositiva, cada ###
-- y cada corte (--- o ::: corte) una nueva dentro de la seccion. Las que
-- siguen a la primera de una seccion llevan arriba el rotulo de la seccion.
------------------------------------------------------------------------
local function esc(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function es_corte(b)
  return b.t == "HorizontalRule" or (b.t == "Div" and tiene(b, "corte"))
end

local function titulo_sin_numeral(h)
  local ins = pandoc.Inlines({})
  for _, il in ipairs(h.content) do
    if not (il.t == "Span" and tiene(il, "numeral")) then ins:insert(il) end
  end
  return pandoc.utils.stringify(ins)
end

-- Primeras palabras de un bloque, para nombrar en la vista general una
-- diapositiva que no abre con titulo: hasta el primer punto o dos puntos
-- seguido de espacio, y como mucho unos 46 caracteres.
local function fragmento(b)
  local s
  if b.t == "Div" and tiene(b, "tabla") then
    s = ""
    b:walk({Table = function(t) if s == "" then s = pandoc.utils.stringify(t.caption.long) end end})
  elseif b.t == "Div" and tiene(b, "errores") then
    s = "Errores frecuentes"
  elseif b.t == "Div" then
    -- sin formulas: el escritor "plain" no sabe dibujarlas y avisaria por la consola
    s = pandoc.write(pandoc.Pandoc({b:walk({Math = function() return pandoc.Str("") end})}), "plain")
  else
    s = pandoc.utils.stringify(b)
  end
  s = s:gsub("%s+", " ")
  s = s:gsub("^%s+", "")
  local desde = 1
  while true do
    local ini, fin = s:find("[%.:]%s", desde)
    if not ini then break end
    if ini >= 12 then s = s:sub(1, ini); break end
    desde = fin + 1
  end
  if (utf8.len(s) or 0) > 46 then
    s = s:sub(1, utf8.offset(s, 47) - 1)
    s = s:gsub("%s+%S*$", "")
  end
  return s
end

local function armar_diapositivas(blocks, enc)
  local slides, actual, rotulo_sec, titulo_unidad = {}, nil, nil, ""
  local function nueva(clase, titulo)
    actual = {clase = clase, titulo = titulo, blocks = pandoc.Blocks({}), n = 0}
    table.insert(slides, actual)
  end
  local function con_rotulo()
    if rotulo_sec then
      actual.blocks:insert(pandoc.Para({pandoc.Span(texto(rotulo_sec), {class = "serie-rotulo"})}))
    end
  end
  for _, b in ipairs(blocks) do
    if b.t == "Header" and b.level == 1 then
      titulo_unidad = titulo_sin_numeral(b)
      nueva("portada", titulo_unidad)
      actual.blocks:extend(enc)
      actual.blocks:insert(b)
      rotulo_sec = nil
    elseif b.t == "Header" and b.level == 2 then
      rotulo_sec = pandoc.utils.stringify(b)
      nueva("seccion", rotulo_sec)
      actual.blocks:insert(b); actual.n = actual.n + 1
    elseif b.t == "Header" and b.level == 3 then
      nueva("continuacion", (rotulo_sec and (rotulo_sec .. ": ") or "") .. pandoc.utils.stringify(b))
      con_rotulo()
      actual.blocks:insert(b); actual.n = actual.n + 1
    elseif es_corte(b) then
      if actual then
        nueva("continuacion", nil)
        actual.base = rotulo_sec or titulo_unidad
        con_rotulo()
      end
    else
      if actual == nil or actual.clase == "portada" then nueva("intro", "Introducción") end
      actual.blocks:insert(b); actual.n = actual.n + 1
      if actual.titulo == nil then
        local f = fragmento(b)
        if f ~= "" then actual.titulo = actual.base .. ": " .. f end
      end
    end
  end
  local utiles = {}
  for _, s in ipairs(slides) do
    if s.n > 0 or s.clase == "portada" then table.insert(utiles, s) end
  end
  local out, total = pandoc.Blocks({}), #utiles
  for i, s in ipairs(utiles) do
    out:insert(raw('<section class="diapositiva ' .. s.clase .. '" id="d' .. i .. '" role="group" ' ..
      'aria-roledescription="diapositiva" aria-label="Diapositiva ' .. i .. " de " .. total ..
      '" data-titulo="' .. esc(s.titulo or ((s.base or titulo_unidad) .. ", continuación")) .. '">'))
    out:extend(s.blocks)
    out:insert(raw("</section>"))
  end
  return out, total
end

function Pandoc(doc)
  local m = doc.meta
  if m.formato then formato = pandoc.utils.stringify(m.formato) end
  if m.modo then modo = pandoc.utils.stringify(m.modo) end
  if m.unidad then unidad = pandoc.utils.stringify(m.unidad) end
  if formato ~= "completo" and formato ~= "a4" and formato ~= "diapositivas" then
    io.stderr:write("[estudio.lua] formato desconocido: " .. formato .. " (completo, a4 o diapositivas)\n")
    formato = "completo"
  end
  if modo ~= "extenso" and modo ~= "corto" then
    io.stderr:write("[estudio.lua] modo desconocido: " .. modo .. " (extenso o corto)\n")
    modo = "extenso"
  end
  if modo == "corto" then con_sintesis = false end
  if m.practica ~= nil then practica = (m.practica == true or pandoc.utils.stringify(m.practica) == "true") end
  if m.indice ~= nil then con_indice = (m.indice == true or pandoc.utils.stringify(m.indice) == "true") end
  if m.sintesis ~= nil then con_sintesis = not (m.sintesis == false or pandoc.utils.stringify(m.sintesis) == "false") end
  if con_indice and (formato == "diapositivas" or modo == "corto") then
    table.insert(avisos, "el índice solo va en formato completo o a4 y modo extenso: se omite")
    con_indice = false
  end
  local u0 = unidad
  if modo == "corto" then
    -- el modo corto no lleva glosario ni demostraciones
    local nuevos, i = pandoc.Blocks({}), 1
    while i <= #doc.blocks do
      local b, sig = doc.blocks[i], doc.blocks[i + 1]
      if b.t == "Header" and b.level == 2 and sig and sig.t == "Div" and tiene(sig, "glosario") then
        table.insert(avisos, "modo corto: se omite el glosario")
        i = i + 2
      elseif b.t == "Div" and (tiene(b, "glosario") or tiene(b, "demostracion")) then
        table.insert(avisos, "modo corto: se omite un bloque de glosario o demostración")
        i = i + 1
      else
        nuevos:insert(b)
        i = i + 1
      end
    end
    doc.blocks = nuevos
  end
  if con_sintesis then revisar_sintesis(doc.blocks) end
  doc = doc:walk(numerar)
  doc = doc:walk(emparejar)
  doc = doc:walk(resolver)

  -- Encabezado: solo materia y unidad
  local enc = pandoc.Blocks({})
  if m.materia then
    local linea = pandoc.Inlines({pandoc.Span(texto(pandoc.utils.stringify(m.materia)), {class = "enc-materia"})})
    if m.unidad then
      -- "Materia | Unidad N", juntas del lado izquierdo
      linea:insert(pandoc.Space())
      linea:insert(pandoc.Span(texto("|"), {class = "enc-sep"}))
      linea:insert(pandoc.Space())
      linea:insert(pandoc.Span(texto("Unidad " .. u0), {class = "enc-unidad"}))
    end
    enc:insert(pandoc.Para(linea))
  end
  local abre = raw('<div class="libro formato-' .. formato .. ' modo-' .. modo .. '"' ..
        (m.sigla and (' data-sigla="' .. pandoc.utils.stringify(m.sigla) .. '"') or "") .. '>')
  local todo
  if formato == "diapositivas" then
    local diap, total = armar_diapositivas(doc.blocks, pandoc.Blocks({pandoc.Div(enc, {class = "encabezado"})}))
    -- la clase "deck" se pone en <html> antes de pintar el resto (sin JavaScript queda una pagina comun)
    todo = pandoc.Blocks({raw('<script>document.documentElement.className += " deck";</script>'), abre})
    todo:extend(diap)
  else
    -- el corte de diapositiva no significa nada fuera de las diapositivas
    local sin = pandoc.Blocks({})
    for _, b in ipairs(doc.blocks) do
      if not es_corte(b) then sin:insert(b) end
    end
    doc.blocks = sin
    todo = pandoc.Blocks({abre, pandoc.Div(enc, {class = "encabezado"})})
    if formato == "a4" and not espejo.espejado(m) then
      -- Hoja A4 que no se imprime: margenes iguales en todas las hojas, "Hoja n de N" siempre a la derecha
      -- y la seccion vigente siempre a la izquierda (la hoja 1, como siempre, sin seccion)
      local caja = espejo.caja_texto("string(seccion)", "var(--lapiz)", "font-style: italic;")
      todo:insert(1, espejo.script(espejo.css_sin_espejo(caja), true))
    end
    if con_indice then todo:extend(indice(doc.blocks)) end
    -- A4: cada unidad desde la segunda arranca hoja nueva. Se hace con un bloque
    -- vacio y no con break-before en el h1: en Firefox el h1 con salto propio
    -- deja en blanco la primera hoja de cada unidad al imprimir.
    local h1_vistos = 0
    for _, b in ipairs(doc.blocks) do
      if formato == "a4" and b.t == "Header" and b.level == 1 then
        h1_vistos = h1_vistos + 1
        if h1_vistos > 1 then todo:insert(pandoc.Div({}, pandoc.Attr("", {"hoja-aparte"}))) end
      end
      todo:insert(b)
    end
  end
  todo:insert(raw("</div>"))
  doc.blocks = todo
  for _, a in ipairs(avisos) do io.stderr:write("[estudio.lua] " .. a .. "\n") end
  return doc
end
