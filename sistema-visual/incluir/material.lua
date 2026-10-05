--[[ material.lua - filtro de Pandoc del material impreso en HTML A4 (sistema v4):
parciales digitalizados, modelos de practica y hojas de soluciones.

Uso:  pandoc x.md --lua-filter=incluir/material.lua ... (la cadena completa esta en
      construir.py, funcion material(), y en apoyo/material-a4.md)

Metadatos del Markdown:
  materia       linea superior de cada hoja (rotulo tipo plano): "Materia de ejemplo" (obligatorio)
  tema          linea superior de cada hoja: "Primer parcial, practico" (obligatorio)
  espejo: false (o imprime: false)   si no se imprime: margenes IGUALES en todas las hojas y "Hoja n de N" siempre del
                mismo lado (ver incluir/espejo.lua); por defecto, espejado a doble faz
  El rotulo tipo plano es UNA SOLA LINEA en el margen superior: del lado
  interior "materia | tema" y del exterior "Hoja n de N"; sin datos personales ni fecha. No hay
  rotulo al pie: el area de texto ocupa toda la hoja. (El pie del original de la institucion ya no
  se imprime.)

Que entiende (clases de Pandoc):
  ::: {.cabecera-original titulo="..."}     encabezado fiel del original, SIN los renglones Legajo,
      Apellido y nombre y Curso ni la fecha; cada parrafo del cuerpo, si
      hubiera otros renglones del original, es un renglon de datos
  ::: consigna                              consigna general del original, entre filetes
  ::: {.ejercicio n=1 espacio=46}           ejercicio con el numero "1)" colgado a la izquierda y,
                                            si se da espacio=mm, el espacio en blanco para responder
                                            dentro del mismo bloque (no se parte entre hojas)
      a. incisos                            lista con letras: "a." en negrita, colgada
      ::: datos                             "Datos." en linea
      ![epigrafe](figura.svg){width=76mm}   figura SVG en linea (letra y colores de la pagina)
  ::: {.espacio mm=46}                      espacio en blanco para responder, sin lineas
  ::: resultado / ::: supuesto / ::: errata   "Resultado." (verde), "Supuesto." (lapiz), "Errata." (rojo)
  ::: subtitulo                             bajada de la hoja de soluciones, con filete
  ::: tabla-resultados + tabla              hoja de resultados
  tablas comunes                            tablas de Pandoc (por ejemplo la de resultados)
]]

local avisos = {}
local script_dir = (PANDOC_SCRIPT_FILE or ""):match("^(.*)[/\\][^/\\]*$") or "."
local espejo = dofile(script_dir .. "/espejo.lua")   -- margenes espejados o iguales (-M espejo=false)

local function tiene(el, clase)
  for _, k in ipairs(el.classes) do if k == clase then return true end end
  return false
end

local function texto(s) return pandoc.Inlines(s) end
local function raw(s) return pandoc.RawBlock("html", s) end

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

local function esc(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function js(s)
  return '"' .. s:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("</", "<\\/") .. '"'
end

local function css_str(s)
  return (tostring(s):gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("[\r\n]+", " "))
end

local function svg_en_linea(src)
  local f = io.open(src, "rb")
  if not f then return nil end
  local s = f:read("a"); f:close()
  s = s:gsub("<%?xml.-%?>", ""):gsub("<!DOCTYPE.->", ""):gsub("<!%-%-.-%-%->", "")
  return s
end

local function figura(img, epigrafe)
  local s = svg_en_linea(img.src)
  if not s then
    table.insert(avisos, "figura sin archivo: " .. img.src)
    return nil
  end
  local ancho = img.attributes.width
  local estilo = ancho and (' style="width:' .. ancho .. '"') or ""
  local bl = pandoc.Blocks({raw('<div class="fig"' .. estilo .. ">"), raw(s)})
  if epigrafe and #epigrafe > 0 then
    bl:insert(pandoc.Div({pandoc.Plain(epigrafe)}, {class = "epigrafe"}))
  end
  bl:insert(raw("</div>"))
  return bl
end

local ROTULOS = {resultado = "Resultado.", supuesto = "Supuesto.", errata = "Errata.", datos = "Datos."}

local trabajo = {
  Para = function(p)
    -- una figura suelta en su parrafo (imagen sin texto alternativo)
    if #p.content == 1 and p.content[1].t == "Image" and p.content[1].src:match("%.svg$") then
      return figura(p.content[1], p.content[1].caption)
    end
  end,

  Figure = function(fig)
    local img
    fig:walk({Image = function(i) img = img or i end})
    if img and img.src:match("%.svg$") then
      return figura(img, pandoc.utils.blocks_to_inlines(fig.caption.long))
    end
  end,

  Div = function(d)
    if tiene(d, "cabecera-original") then
      local titulo = d.attributes.titulo or ""
      local fecha = d.attributes.fecha or ""
      local bl = pandoc.Blocks({
        raw('<div class="cab"><span class="cab-titulo">' .. esc(titulo) .. '</span>'
          .. (fecha ~= "" and ('<span class="cab-fecha">' .. esc(fecha) .. "</span>") or "") .. "</div>")})
      bl:extend(d.content)
      d.content = bl
      d.attributes.titulo = nil
      d.attributes.fecha = nil
      return d
    end
    if tiene(d, "ejercicio") then
      local n = d.attributes.n
      if not n then table.insert(avisos, "ejercicio sin n=") end
      d.attributes.n = nil
      d.content:insert(1, raw('<span class="n">' .. esc(n or "") .. ")</span>"))
      if d.attributes.espacio then
        -- espacio para responder, dentro del ejercicio para que viajen juntos
        d.content:insert(raw('<div class="espacio" style="height:' .. d.attributes.espacio .. 'mm" aria-hidden="true"></div>'))
        d.attributes.espacio = nil
      end
      return d
    end
    if tiene(d, "espacio") then
      local mm = d.attributes.mm or "30"
      return raw('<div class="espacio" style="height:' .. mm .. 'mm" aria-hidden="true"></div>')
    end
    for clase, rotulo in pairs(ROTULOS) do
      if tiene(d, clase) then
        d.content = anteponer(d.content, {pandoc.Span(texto(rotulo), {class = "rotulo"})})
        return d
      end
    end
  end,
}

function Pandoc(doc)
  local m = doc.meta
  local function s(k) return m[k] and pandoc.utils.stringify(m[k]) or "" end
  if s("materia") == "" then table.insert(avisos, "falta el metadato materia") end
  if s("tema") == "" then table.insert(avisos, "falta el metadato tema") end
  doc = doc:walk(trabajo)
  -- Linea superior: "materia | tema" del lado interior (el numero de hoja, del exterior, lo
  -- escribe material-a4.css). Un <style> suelto en el cuerpo no lo toma Paged.js; un script que
  -- lo agrega al <head> mientras se lee la pagina si. Declaraciones completas: Paged.js no
  -- fusiona la caja de margen con la de otra regla @page.
  local linea = s("materia") .. " | " .. s("tema")
  local estilo = 'font-family: "Estudio Sans", sans-serif; font-size: 8pt; color: var(--tinta); vertical-align: bottom; padding-bottom: 3.5mm; white-space: nowrap;'
  local sin_espejo = not espejo.espejado(doc.meta)
  local css
  if sin_espejo then
    -- sin espejo (no se imprime): todas las hojas como la derecha; materia y tema siempre a la izquierda
    css = '@page :right { @top-left { content: "' .. css_str(linea) .. '"; ' .. estilo .. ' text-align: left; } } '
      .. espejo.css_sin_espejo('content: "' .. css_str(linea) .. '"; ' .. estilo .. ' text-align: left;')
  else
    css = string.format(
      '@page :right { @top-left { content: "%s"; %s text-align: left; } } @page :left { @top-right { content: "%s"; %s text-align: right; } }',
      css_str(linea), estilo, css_str(linea), estilo)
  end
  local todo = pandoc.Blocks({
    espejo.script(css, sin_espejo),
    raw('<div class="material">'),
  })
  todo:extend(doc.blocks)
  todo:insert(raw("</div>"))
  doc.blocks = todo
  for _, a in ipairs(avisos) do io.stderr:write("[material.lua] " .. a .. "\n") end
  return doc
end
