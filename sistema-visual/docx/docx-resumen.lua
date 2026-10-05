--[[
docx-resumen.lua - filtro de Pandoc para el resumen en Word (.docx) del sistema v4.
Lo usa construir_docx.py (--tipo resumen); recibe -M modo=extenso|corto.

Lee el MISMO Markdown que alimenta el HTML (incluir/estudio.lua) y traduce cada
componente a parrafos de estilo propio y tablas de diseno (los estilos estan en
reference-resumen.docx, que arma construir_docx.py):

  metadatos materia, unidad    encabezado "Materia | Unidad N" (solo en la primera hoja)
  # Titulo {unidad=3}          apertura: numeral grande azul colgado + titulo + filete grueso
  ## Seccion {#sec:id}         numerada 3.1, numero azul colgado; {-} sin numero
  ### Subtitulo                sin numero
  ::: definicion / ejemplo / propiedad / demostracion   rotulo en linea "Definicion 3.1 (...)."
  ::: resolucion               abierta, con el rotulo "Resolucion." (como la hoja A4)
  ::: clave (+ ::: ecuacion)   el unico recuadro
  ::: {.ecuacion #ec:id}       ecuacion nativa centrada y numero "(3.1)" a la derecha
  ::: sintesis                 filete + rotulo "Sintesis" colgado
  ::: errores                  aspa roja colgada en cada error
  ::: ojo                      aspa roja colgada y "Ojo."
  ::: margen, ^[nota]          tabla de dos columnas: cuerpo a la izquierda, nota a la derecha
  ![epigrafe](x.png){#fig:id}  tabla de dos columnas: figura a la izquierda, epigrafe a la derecha
  ::: {#tbl:id} + tabla        "Tabla 3-1." sobre la tabla
  ::: glosario                 tabla de dos columnas: termino | definicion
  ::: previas / proba / respuestas-practica    solo con practica: true, marcados como material de practica
  ::: hoja-aparte              salto de hoja
  [](#id)                      referencia cruzada en azul
El modo corto quita sintesis, glosario y demostraciones y no lleva indice.
]]
local dir = (PANDOC_SCRIPT_FILE or ""):match("^(.*)[/\\][^/\\]*$") or "."
local K = dofile(dir .. "/docx-comun.lua")
local tiene, texto, run, TAB, raw, estilo = K.tiene, K.texto, K.run, K.TAB, K.raw, K.estilo

local modo = "extenso"
local unidad = "1"
local practica = false
local con_indice = false
local con_sintesis = true
local c = {}
local refs = {}
local avisos = {}
local indice_items = {}
local h1_vistos = 0

local function reiniciar() c = {sec = 0, enun = 0, fig = 0, tbl = 0, ec = 0, nota = 0} end
reiniciar()

local ENUN = {definicion = "Definición", ejemplo = "Ejemplo", propiedad = "Propiedad",
              demostracion = "Demostración"}
local PRACTICA = {previas = "Antes de leer", proba = "Probá sin mirar",
                  ["respuestas-practica"] = "Respuestas de la práctica"}
local ANCHO_FIGURA = "11.4cm"

local function strong(s) return pandoc.Strong(pandoc.Inlines(s)) end

------------------------------------------------------------------------
-- Pasada 1: numeracion y traduccion de los componentes con numero
------------------------------------------------------------------------
local function mk_ecuacion(d, clave)
  c.ec = c.ec + 1
  local n = unidad .. "." .. c.ec
  if d.identifier ~= "" then refs[d.identifier] = "ecuación (" .. n .. ")" end
  return K.tabla({{ {estilo("EcuacionP", d.content)},
                    {estilo("EcNum", {pandoc.Plain({pandoc.Str("(" .. n .. ")")})})} }},
    {0.92, 0.08}, clave and "TablaClave" or "TablaEcuacion")
end

local function mk_figura(fig)
  c.fig = c.fig + 1
  local n = unidad .. "-" .. c.fig
  if fig.identifier ~= "" then refs[fig.identifier] = "figura " .. n end
  local cap = fig.caption.long
  local rot = K.rotulo("Figura", n)
  if #cap == 0 then cap = pandoc.Blocks({pandoc.Plain(rot)}) else K.anteponer(cap, rot) end
  local cuerpo = fig.content:walk({Image = function(img)
    if not img.attributes.width then img.attributes.width = ANCHO_FIGURA end
    return img
  end})
  return K.tabla({{ {estilo("FiguraP", cuerpo)}, {estilo("EpigrafeFigura", cap)} }},
    {0.71, 0.29}, "TablaFigura")
end

local numerar = {
  traverse = "topdown",

  Header = function(h)
    if h.level == 1 then
      if h.attributes.unidad then unidad = h.attributes.unidad end
      reiniciar()
      h1_vistos = h1_vistos + 1
      local titulo = pandoc.Span(h.content, pandoc.Attr("", {}, {["custom-style"] = "TituloSec"}))
      local ins = pandoc.Inlines({})
      if not tiene(h, "unnumbered") then
        ins:insert(run("Numeral", unidad)); ins:insert(TAB)
        table.insert(indice_items, {nivel = 1, num = unidad, txt = pandoc.utils.stringify(h.content)})
      else
        table.insert(indice_items, {nivel = 1, num = "", txt = pandoc.utils.stringify(h.content)})
      end
      ins:insert(titulo)
      return estilo(h1_vistos > 1 and "AperturaNueva" or "Apertura", {pandoc.Para(ins)})
    end
    if h.level == 2 then
      local titulo = pandoc.Span(h.content, pandoc.Attr("", {}, {["custom-style"] = "TituloSec"}))
      if tiene(h, "unnumbered") then
        h.content = pandoc.Inlines({TAB, titulo})
        table.insert(indice_items, {nivel = 2, num = "", txt = pandoc.utils.stringify(titulo)})
      else
        c.sec = c.sec + 1
        local n = unidad .. "." .. c.sec
        if h.identifier ~= "" then refs[h.identifier] = "sección " .. n end
        table.insert(indice_items, {nivel = 2, num = n, txt = pandoc.utils.stringify(titulo)})
        h.content = pandoc.Inlines({run("Numero", n), TAB, titulo})
      end
      return h
    end
  end,

  Div = function(d)
    for clase, nombre in pairs(ENUN) do
      if tiene(d, clase) then
        c.enun = c.enun + 1
        local n = unidad .. "." .. c.enun
        local ins = pandoc.Inlines({strong(nombre .. " "), run("NumeroRotulo", n)})
        local t = d.attributes.titulo
        if t then
          ins:insert(pandoc.Space())
          ins:insert(pandoc.Str("(" .. t .. ")."))
        else
          ins:insert(strong("."))
        end
        d.content = K.anteponer(d.content, ins)
        d.classes:insert("enunciado")
        d.attributes.titulo = nil
        d.attributes["custom-style"] = "Enunciado"
        if d.identifier ~= "" then refs[d.identifier] = string.lower(nombre) .. " " .. n end
        return d
      end
    end
    if tiene(d, "clave") then
      local nuevo = pandoc.Blocks({})
      for _, b in ipairs(d.content) do
        if b.t == "Div" and tiene(b, "ecuacion") then nuevo:insert(mk_ecuacion(b, true)) else nuevo:insert(b) end
      end
      d.content = nuevo
      return d
    end
    if d.identifier:match("^tbl:") then
      c.tbl = c.tbl + 1
      local n = unidad .. "-" .. c.tbl
      refs[d.identifier] = "tabla " .. n
      d = d:walk({Table = function(t)
        local rot = K.rotulo("Tabla", n)
        if #t.caption.long == 0 then
          t.caption.long = pandoc.Blocks({pandoc.Plain(rot)})
        else
          K.anteponer(t.caption.long, rot)
        end
        return t
      end})
      return d
    end
    if tiene(d, "ecuacion") then
      return mk_ecuacion(d, false)
    end
  end,

  Figure = function(fig) return mk_figura(fig) end,

  Note = function(nt)
    c.nota = c.nota + 1
    local n = tostring(c.nota)
    local cuerpo = pandoc.Inlines({run("NotaNum", n), pandoc.Space()})
    cuerpo:extend(pandoc.utils.blocks_to_inlines(nt.content))
    return {run("NotaRef", n), pandoc.Span(cuerpo, {class = "nota-margen"})}
  end,
}

------------------------------------------------------------------------
-- Pasada 2: cada nota al margen viaja pegada a su bloque: tabla de dos
-- columnas (cuerpo | nota) cuya fila no se parte entre hojas.
------------------------------------------------------------------------
local function par(bloque, notas)
  local cuerpo = {estilo("CuerpoCelda", {bloque})}
  local nota = {estilo("NotaMargen", notas)}
  return K.tabla({{cuerpo, nota}}, {0.71, 0.29}, "TablaNota")
end

local function sacar_notas(b)
  if b.t ~= "Para" and b.t ~= "Plain" then return nil end
  local notas = pandoc.Blocks({})
  local resto = pandoc.Inlines({})
  for _, il in ipairs(b.content) do
    if il.t == "Span" and tiene(il, "nota-margen") then
      notas:insert(pandoc.Plain(il.content))
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
    local pendiente = nil
    for _, b in ipairs(bl) do
      if b.t == "Div" and tiene(b, "margen") then
        pendiente = pendiente or pandoc.Blocks({})
        pendiente:extend(b.content)
      else
        local propias = sacar_notas(b)
        local notas = pandoc.Blocks({})
        if pendiente and b.t ~= "Header" then notas:extend(pendiente); pendiente = nil end
        if propias then notas:extend(propias) end
        if pendiente and b.t == "Header" then
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
-- Pasada 3: referencias, rotulos colgados, practica, glosario
------------------------------------------------------------------------
-- Primer parrafo con el rotulo colgado (tabulacion, rotulo, tabulacion) y el
-- resto con la sangria de texto
local function colgar(contenido, st1, st2, prefijo)
  local bl = pandoc.Blocks({})
  local primero = true
  local cont = pandoc.Blocks(contenido)
  if not (cont[1] and (cont[1].t == "Para" or cont[1].t == "Plain")) then
    cont:insert(1, pandoc.Plain({}))
  end
  K.anteponer_pegado(cont, prefijo)
  for _, b in ipairs(cont) do
    bl:insert(estilo(primero and st1 or st2, {b}))
    primero = false
  end
  return bl
end

local function aspa() return run("Aspa", "✗") end

local resolver = {
  Inlines = K.espacio_duro,
  Link = function(l)
    local id = l.target:match("^#(.+)$")
    if id and #l.content == 0 then
      if refs[id] then return run("Referencia", refs[id]) end
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
        local pref = pandoc.Inlines({TAB, run("Colgado", "Práctica"), TAB,
          pandoc.Emph(texto(nombre .. ".")), pandoc.Space(),
          run("AvisoPractica", "Material de práctica, no proviene de la fuente.")})
        local bl = pandoc.Blocks({})
        if clase == "respuestas-practica" then bl:insert(K.hoja_nueva()) end
        bl:insert(K.separador("PracticaFilete"))
        bl:insert(estilo("PracticaP", {pandoc.Para(pref)}))
        bl:extend(d.content)
        bl:insert(K.separador("PracticaFilete"))
        return bl
      end
    end
    if tiene(d, "sintesis") then
      if not con_sintesis then return {} end
      local bl = pandoc.Blocks({K.separador("SintesisFilete")})
      bl:extend(colgar(d.content, "Sintesis", "SintesisCont", {TAB, run("Colgado", "Síntesis"), TAB}))
      return bl
    end
    if tiene(d, "ojo") then
      return colgar(d.content, "Ojo", "OjoCont", {TAB, aspa(), TAB, strong("Ojo."), pandoc.Space()})
    end
    if tiene(d, "errores") then
      local bl = pandoc.Blocks({estilo("RotuloBloque", {pandoc.Plain({pandoc.Emph({strong("Errores frecuentes")})})})})
      for _, b in ipairs(d.content) do
        if b.t == "BulletList" then
          for _, item in ipairs(b.content) do
            bl:extend(colgar(item, "ErrorItem", "ErrorItemCont", {TAB, aspa(), TAB}))
          end
        else
          bl:insert(b)
        end
      end
      return bl
    end
    if tiene(d, "resolucion") then
      d.content = K.anteponer(d.content, {pandoc.Emph(texto("Resolución."))})
      d.attributes["custom-style"] = nil
      return d
    end
    if tiene(d, "demostracion") then
      -- el rotulo ya se puso en la pasada 1 (clase enunciado)
      return d
    end
    if tiene(d, "glosario") then
      local filas = {}
      for _, b in ipairs(d.content) do
        if b.t == "DefinitionList" then
          for _, item in ipairs(b.content) do
            local def = pandoc.Blocks({})
            for _, bs in ipairs(item[2]) do def:extend(bs) end
            table.insert(filas, { {estilo("GlosarioT", {pandoc.Plain({pandoc.Strong(item[1])})})},
                                  {estilo("GlosarioD", def)} })
          end
        end
      end
      if #filas == 0 then return d end
      return K.tabla(filas, {0.27, 0.73}, "TablaGlosario")
    end
    if tiene(d, "hoja-aparte") then
      return K.hoja_nueva()
    end
  end,
}

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

local function es_corte(b)
  return b.t == "HorizontalRule" or (b.t == "Div" and tiene(b, "corte"))
end

-- Indice simple (sin enlaces ni numeros de pagina), como el de la hoja A4
local function indice()
  local bl = pandoc.Blocks({estilo("RotuloBloque", {pandoc.Plain({pandoc.Emph({strong("Índice")})})})})
  for _, it in ipairs(indice_items) do
    local ins = pandoc.Inlines({})
    if it.num ~= "" then ins:insert(run("Numero", it.num)); ins:insert(TAB) else ins:insert(TAB) end
    ins:extend(texto(it.txt))
    bl:insert(estilo(it.nivel == 1 and "IndiceUnidad" or "IndiceSeccion", {pandoc.Plain(ins)}))
  end
  return bl
end

function Pandoc(doc)
  local m = doc.meta
  if m.modo then modo = pandoc.utils.stringify(m.modo) end
  if m.unidad then unidad = pandoc.utils.stringify(m.unidad) end
  if modo ~= "extenso" and modo ~= "corto" then
    io.stderr:write("[docx-resumen.lua] modo desconocido: " .. modo .. " (extenso o corto)\n")
    modo = "extenso"
  end
  if modo == "corto" then con_sintesis = false end
  if m.practica ~= nil then practica = (m.practica == true or pandoc.utils.stringify(m.practica) == "true") end
  if m.indice ~= nil then con_indice = (m.indice == true or pandoc.utils.stringify(m.indice) == "true") end
  if m.sintesis ~= nil then con_sintesis = not (m.sintesis == false or pandoc.utils.stringify(m.sintesis) == "false") end
  if con_indice and modo == "corto" then
    table.insert(avisos, "el índice solo va en modo extenso: se omite")
    con_indice = false
  end
  local u0 = unidad
  if modo == "corto" then
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
  -- el corte de diapositiva no significa nada en Word
  local sin = pandoc.Blocks({})
  for _, b in ipairs(doc.blocks) do if not es_corte(b) then sin:insert(b) end end
  doc.blocks = sin
  doc = doc:walk(numerar)
  doc = doc:walk(emparejar)
  doc = doc:walk(resolver)

  local todo = pandoc.Blocks({})
  if m.materia then
    local ins = pandoc.Inlines({run("EncMateria", pandoc.utils.stringify(m.materia))})
    if m.unidad then
      ins:insert(pandoc.Space())
      ins:insert(run("EncSep", "|"))
      ins:insert(pandoc.Space())
      ins:insert(run("EncUnidad", "Unidad " .. u0))
    end
    todo:insert(estilo("Encabezado", {pandoc.Para(ins)}))
  end
  if con_indice then todo:extend(indice()) end
  todo:extend(doc.blocks)
  doc.blocks = todo
  for _, a in ipairs(avisos) do io.stderr:write("[docx-resumen.lua] " .. a .. "\n") end
  return doc
end
