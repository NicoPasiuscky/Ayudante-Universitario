--[[ tp.lua - filtro de Pandoc del Trabajo Practico en HTML A4 (sistema v4).
Mismo Markdown y mismo JSON que el .docx (docx/construir_docx.py), asi que un TP puede
salir en HTML, en PDF (imprimiendo ese HTML con herramientas/imprimir_a4.py) o en Word
sin escribirlo dos veces. Es el equivalente de docx/docx.lua.

Uso:  pandoc tp.md --metadata-file=tp.json --lua-filter=incluir/tp.lua ... (la cadena
      completa esta en construir.py, funcion tp(), y en flujos/tp.md)

Metadatos (el JSON del .docx sirve tal cual con --metadata-file):
  caratula:  encabezado, numero, titulo, materia, anio, curso, integrantes[], institucion[], extra (lista de pares etiqueta y valor)
             Modelo habitual: "Trabajo Practico de laboratorio N° __", titulo
             con filete grueso, y los campos Materia, Año y Curso con renglon, mas una tabla de
             integrantes (columnas "Apellido y nombre" y "Legajo", una fila por integrante, sin
             limite fijo) cargada desde integrantes: [{"nombre": "...", "legajo": "..."}]; sin la
             lista, la tabla sale con dos filas vacias para completar. Los datos de integrantes
             los pasa la persona en cada TP: no se guardan en ningun archivo del proyecto.
             Campo vacio = renglon para completar (nunca se inventan datos).
  cabecera:  trabajo  texto del lado interior de la cabeza de hoja (el exterior lleva "Hoja n de N")
  espejo: false (o imprime: false)   si no se imprime: margenes IGUALES en todas las hojas y "Hoja n de N" siempre del
             mismo lado (ver incluir/espejo.lua); por defecto, espejado a doble faz
  materia    metadato comun del Markdown (se usa como titulo de la pagina si falta pagetitle)

Que entiende del Markdown (igual que docx.lua):
  # y ##     se numeran (1, 1.1) con el numero en azul, colgado a la izquierda; {-} sin numero
  Figuras y tablas con epigrafe: "Figura 1." / "Tabla 1." con el numero en azul;
             identificadores #fig:x, #tbl:x (en la tabla o en un div que la envuelve), #sec:x
  [](#fig:x) "figura 1", [](#tbl:x) "tabla 1", [](#sec:x) "seccion 2" (azul)
  ::: resultado ("Resultado."), ::: supuesto ("Supuesto."), ::: enunciado (texto fiel, con
  sangria), ::: salto (salto de hoja)
La caratula es la hoja 1 y no lleva cabeza de hoja; el cuerpo arranca en la hoja 2 (igual que el .docx).
El color nunca va en titulos ni fondos: solo en numeros y referencias.
]]

local script_dir = (PANDOC_SCRIPT_FILE or ""):match("^(.*)[/\\][^/\\]*$") or "."
local espejo = dofile(script_dir .. "/espejo.lua")   -- margenes espejados o iguales (-M espejo=false)
local numeros = {}          -- id -> {tipo, numero}
local h1, h2, nfig, ntab = 0, 0, 0, 0

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function css_str(s)
  return (tostring(s):gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("[\r\n]+", " "))
end

local function raw(s) return pandoc.RawBlock("html", s) end

local function num(n) return pandoc.Span({pandoc.Str(tostring(n))}, pandoc.Attr("", {"num"})) end

local function rotulo(palabra, n)
  -- "Figura 1." : palabra en negrita de tinta, numero en azul
  return {pandoc.Strong({pandoc.Str(palabra), pandoc.Space(), num(n), pandoc.Str(".")}), pandoc.Space()}
end

local function anteponer(bloques, inlines)
  if #bloques == 0 then return {pandoc.Plain(inlines)} end
  local b = bloques[1]
  if b.t == "Plain" or b.t == "Para" then
    local nuevo = {}
    for _, x in ipairs(inlines) do table.insert(nuevo, x) end
    for _, x in ipairs(b.content) do table.insert(nuevo, x) end
    b.content = nuevo
  else
    table.insert(bloques, 1, pandoc.Plain(inlines))
  end
  return bloques
end

-- Primera pasada: numerar titulos, figuras y tablas (en orden de aparicion)
local function numerar(doc)
  local function tabla(t, id_div)
    local cap = t.caption and t.caption.long or {}
    if #cap == 0 then return t end
    ntab = ntab + 1
    local id = (t.identifier ~= "" and t.identifier) or id_div
    if id and id ~= "" then numeros[id] = {"tabla", tostring(ntab)} end
    t.caption.long = anteponer(cap, rotulo("Tabla", ntab))
    return t
  end
  local function procesar(lista)
    local out = pandoc.List()
    for _, b in ipairs(lista) do
      if b.t == "Header" and b.level <= 2 then
        if not b.classes:includes("unnumbered") then
          local n
          if b.level == 1 then h1 = h1 + 1; h2 = 0; n = tostring(h1)
          else h2 = h2 + 1; n = h1 .. "." .. h2 end
          if b.identifier ~= "" then numeros[b.identifier] = {"sección", n} end
          local c = {num(n), pandoc.Space()}
          for _, x in ipairs(b.content) do table.insert(c, x) end
          b.content = c
        end
        out:insert(b)
      elseif b.t == "Figure" then
        nfig = nfig + 1
        if b.identifier ~= "" then numeros[b.identifier] = {"figura", tostring(nfig)} end
        b.caption.long = anteponer(b.caption.long, rotulo("Figura", nfig))
        out:insert(b)
      elseif b.t == "Table" then
        out:insert(tabla(b, nil))
      elseif b.t == "Div" then
        local id = b.identifier
        if id:match("^tbl:") then
          for i, x in ipairs(b.content) do
            if x.t == "Table" then b.content[i] = tabla(x, id) end
          end
        else
          b.content = procesar(b.content)
        end
        out:insert(b)
      else
        out:insert(b)
      end
    end
    return out
  end
  doc.blocks = procesar(doc.blocks)
  return doc
end

-- Numero y unidad nunca se separan de renglon: espacio duro entre "3,1" y "N"
local UNIDADES = {N=1, kg=1, g=1, m=1, s=1, cm=1, mm=1, km=1, J=1, W=1, Pa=1, Hz=1, K=1,
                  ["°C"]=1, ["m/s"]=1, ["m/s²"]=1, ["m/s2"]=1, rad=1, h=1, min=1, L=1, ml=1, nm=1}
local function espacio_duro(inl)
  for i = 1, #inl - 2 do
    local a, b, c = inl[i], inl[i + 1], inl[i + 2]
    if a.t == "Str" and b.t == "Space" and c.t == "Str" and a.text:match("%d$") then
      local u = c.text:gsub("[%.,;:%)]+$", "")
      if UNIDADES[u] then inl[i + 1] = pandoc.Str("\u{00A0}") end
    end
  end
  return inl
end

-- Segunda pasada: referencias cruzadas y bloques con nombre
local function referencias(doc)
  return doc:walk({
    Inlines = espacio_duro,
    Link = function(l)
      local id = l.target:match("^#(.+)$")
      if id and numeros[id] and #l.content == 0 then
        local tipo, n = numeros[id][1], numeros[id][2]
        return pandoc.Span({pandoc.Str(tipo .. " " .. n)}, pandoc.Attr("", {"ref"}))
      end
    end,
    Div = function(d)
      if d.classes:includes("resultado") then
        d.content = anteponer(d.content, {pandoc.Span({pandoc.Str("Resultado.")}, pandoc.Attr("", {"rotulo"})), pandoc.Space()})
        return d
      elseif d.classes:includes("supuesto") then
        d.content = anteponer(d.content, {pandoc.Span({pandoc.Str("Supuesto.")}, pandoc.Attr("", {"rotulo"})), pandoc.Space()})
        return d
      elseif d.classes:includes("salto") then
        return raw('<div class="salto" aria-hidden="true"></div>')
      end
    end,
  })
end

-- Caratula (modelo habitual de carátula; editable)
local function texto(v) return v and pandoc.utils.stringify(v) or "" end

local function caratula(c, logo, logo_alto)
  local function campo(etq, valor)
    local v = (valor ~= "") and esc(valor) or ""
    return '<p class="campo"><span class="etq">' .. esc(etq) .. '</span><span class="valor">' .. v .. "</span></p>"
  end
  local h = {'<section class="caratula' .. ((logo ~= "") and " con-logo" or "") .. '">'}
  -- Logo opcional (caratula.logo del JSON, ver herramientas/logo.py): arriba de la hoja 1, proporcion intacta
  if logo ~= "" then
    h[#h + 1] = '<img class="logo" src="' .. logo .. '" alt="Logo de la institución" style="height: ' .. logo_alto .. 'mm; --logo-alto: ' .. logo_alto .. 'mm">'
  end
  if c.institucion then
    for _, l in ipairs(c.institucion) do h[#h + 1] = '<p class="marco">' .. esc(texto(l)) .. "</p>" end
  end
  local enc = texto(c.encabezado)
  if enc == "" then enc = "Trabajo Práctico de laboratorio" end
  local numero = texto(c.numero)
  h[#h + 1] = '<p class="tp-enc">' .. esc(enc) .. " N° " .. '<span class="numero">' .. esc(numero) .. "</span></p>"
  h[#h + 1] = '<p class="tp-titulo">' .. esc(texto(c.titulo)) .. "</p>"
  h[#h + 1] = '<div class="campos">'
  h[#h + 1] = campo("Materia:", texto(c.materia))
  h[#h + 1] = campo("Año:", texto(c.anio))
  h[#h + 1] = campo("Curso:", texto(c.curso))
  if c.extra then
    for _, par in ipairs(c.extra) do h[#h + 1] = campo(texto(par[1]) .. ":", texto(par[2])) end
  end
  h[#h + 1] = "</div>"
  -- tabla de integrantes: una fila por integrante; sin lista, dos filas vacias
  local filas = {}
  if c.integrantes then
    for _, i in ipairs(c.integrantes) do
      local n, l = texto(i.nombre), texto(i.legajo)
      if n:match("%S") or l:match("%S") then filas[#filas + 1] = {n, l} end
    end
  end
  if #filas == 0 then filas = {{"", ""}, {"", ""}} end
  local rid = texto(c.rotulo_id)
  if rid == "" then rid = "Legajo" end
  h[#h + 1] = '<table class="integrantes"><thead><tr><th>Apellido y nombre</th><th>' .. esc(rid) .. '</th></tr></thead><tbody>'
  for _, f in ipairs(filas) do
    h[#h + 1] = "<tr><td>" .. esc(f[1]) .. "</td><td>" .. esc(f[2]) .. "</td></tr>"
  end
  h[#h + 1] = "</tbody></table></section>"
  return table.concat(h, "\n")
end

function Pandoc(doc)
  doc = numerar(doc)
  doc = referencias(doc)
  local m = doc.meta
  local car = m.caratula
  local trabajo = (m.cabecera and texto(m.cabecera.trabajo)) or ""
  if trabajo == "" then trabajo = "Trabajo Práctico" end
  -- Declaraciones completas: Paged.js no fusiona la caja de margen con la de otra regla @page
  local estilo = 'font-family: "Estudio Sans", sans-serif; font-size: 8pt; color: var(--lapiz); vertical-align: bottom; padding-bottom: 3.5mm;'
  local sin_espejo = not espejo.espejado(m)
  local css
  if sin_espejo then
    -- sin espejo (no se imprime): todas las hojas como la derecha; el trabajo siempre a la izquierda
    css = string.format('@page :right { @top-left { content: "%s"; %s text-align: left; } } ', css_str(trabajo), estilo)
      .. espejo.css_sin_espejo(string.format('content: "%s"; %s text-align: left;', css_str(trabajo), estilo))
  else
    css = string.format(
      '@page :right { @top-left { content: "%s"; %s text-align: left; } } @page :left { @top-right { content: "%s"; %s text-align: right; } }',
      css_str(trabajo), estilo, css_str(trabajo), estilo)
  end
  -- Un <style> suelto en el cuerpo no lo toma Paged.js; un script que lo agrega al <head> mientras
  -- se lee la pagina si (corre antes de que Paged.js arme las hojas).
  local cab = espejo.script(css, sin_espejo)
  local todo = pandoc.Blocks({})
  if car then todo:insert(raw(caratula(car, texto(m.logo_ruta), texto(m.logo_alto_mm)))) end
  todo:insert(cab)
  todo:insert(raw('<div class="tp">'))
  todo:extend(doc.blocks)
  todo:insert(raw("</div>"))
  doc.blocks = todo
  if not m.pagetitle then
    local t = car and texto(car.titulo) or ""
    local mat = texto(m.materia)
    m.pagetitle = pandoc.MetaString((mat ~= "" and (mat .. ", ") or "") .. (t ~= "" and t or trabajo))
  end
  doc.meta = m
  return doc
end
