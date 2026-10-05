--[[
docx-comun.lua - piezas compartidas de los filtros de Word del sistema v4
(docx-resumen.lua y docx-material.lua). No es un filtro: lo cargan con dofile.

Word no tiene columna de margen, cajas ni rotulos colgados como el HTML: todo
eso se arma con parrafos de estilo propio (los define construir_docx.py en
reference-*.docx) y con tablas de diseno sin bordes, que construir_docx.py
ajusta despues (ancho, sangria, celdas) segun el estilo de tabla.
]]
local K = {}

function K.esc(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

function K.tiene(el, clase)
  for _, k in ipairs(el.classes) do if k == clase then return true end end
  return false
end

function K.texto(s) return pandoc.Inlines(s) end

-- Corrida con estilo de caracter (los estilos estan en reference-*.docx)
function K.run(estilo, texto)
  return pandoc.RawInline("openxml",
    '<w:r><w:rPr><w:rStyle w:val="' .. estilo .. '"/></w:rPr><w:t xml:space="preserve">'
    .. K.esc(texto) .. '</w:t></w:r>')
end

K.TAB = pandoc.RawInline("openxml", "<w:r><w:tab/></w:r>")

function K.raw(xml) return pandoc.RawBlock("openxml", xml) end

-- Div con estilo de parrafo: todos los parrafos de adentro lo toman
function K.estilo(nombre, bloques)
  -- Pandoc escribe un Plain con el estilo "Compact" sin mirar el Div: todo Plain pasa a Para
  local bl = pandoc.Blocks({})
  for _, b in ipairs(bloques) do
    if b.t == "Plain" then bl:insert(pandoc.Para(b.content)) else bl:insert(b) end
  end
  return pandoc.Div(bl, pandoc.Attr("", {}, {["custom-style"] = nombre}))
end

function K.anteponer(bloques, ins)
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

-- Antepone sin espacio (para rotulos colgados con tabulacion)
function K.anteponer_pegado(bloques, ins)
  local b = bloques[1]
  if b and (b.t == "Para" or b.t == "Plain") then
    local nuevo = pandoc.Inlines({})
    nuevo:extend(ins)
    nuevo:extend(b.content)
    b.content = nuevo
  else
    bloques:insert(1, pandoc.Plain(ins))
  end
  return bloques
end

-- Parrafo vacio con estilo (filete, separador)
function K.separador(estilo)
  return K.raw('<w:p><w:pPr><w:pStyle w:val="' .. estilo .. '"/></w:pPr></w:p>')
end

-- Hoja nueva: parrafo de 1 pt con salto previo (no deja un renglon en blanco)
function K.hoja_nueva()
  return K.raw('<w:p><w:pPr><w:pageBreakBefore/><w:spacing w:before="0" w:after="0" w:line="20" '
    .. 'w:lineRule="exact"/></w:pPr></w:p>')
end

-- Espacio en blanco para responder, sin lineas: un parrafo vacio de alto exacto
function K.espacio(mm)
  local tw = math.floor(tonumber(mm) * 1440 / 25.4 + 0.5)
  return K.raw('<w:p><w:pPr><w:pStyle w:val="EspacioRespuesta"/><w:spacing w:before="0" w:after="0" '
    .. 'w:line="' .. tw .. '" w:lineRule="exact"/></w:pPr></w:p>')
end

-- Tabla de diseno. filas: lista de filas; fila: lista de celdas; celda: lista de
-- bloques, o {bloques = ..., span = n}. anchos: fracciones. cab: fila de cabecera opcional.
function K.tabla(filas, anchos, estilo, cab)
  local cols = {}
  for _, w in ipairs(anchos) do table.insert(cols, {pandoc.AlignDefault, w}) end
  local function fila(f)
    local celdas = pandoc.List()
    for _, c in ipairs(f) do
      local bl, cs = c, 1
      if c.bloques then bl, cs = c.bloques, (c.span or 1) end
      celdas:insert(pandoc.Cell(pandoc.Blocks(bl), pandoc.AlignDefault, 1, cs))
    end
    return pandoc.Row(celdas)
  end
  -- Pandoc nuevo trae el constructor pandoc.TableBody; en versiones anteriores se arma la tabla a mano
  local TableBody = pandoc.TableBody or function(body, head, rhc)
    return {attr = pandoc.Attr(), body = body, head = head or {}, row_head_columns = rhc or 0}
  end
  local rows = pandoc.List()
  for _, f in ipairs(filas) do rows:insert(fila(f)) end
  local head = pandoc.TableHead(cab and {fila(cab)} or {})
  return pandoc.Table(pandoc.Caption({}), cols, head, {TableBody(rows, {}, 0)},
    pandoc.TableFoot({}), pandoc.Attr("", {}, {["custom-style"] = estilo}))
end

-- Rotulo "Figura 3-1." / "Tabla 3-1.": palabra en negrita de tinta, numero en azul
function K.rotulo(palabra, n)
  return {pandoc.Strong({pandoc.Str(palabra), pandoc.Space()}), K.run("NumeroRotulo", tostring(n)),
          pandoc.Strong({pandoc.Str(".")})}
end

-- Numero y unidad nunca se separan de renglon (espacio duro)
local UNIDADES = {N=1, kg=1, g=1, m=1, s=1, cm=1, mm=1, km=1, J=1, W=1, Pa=1, Hz=1, K=1,
                  ["°C"]=1, ["m/s"]=1, ["m/s²"]=1, ["m/s2"]=1, rad=1, h=1, min=1, L=1, ml=1, nm=1}
function K.espacio_duro(inl)
  for i = 1, #inl - 2 do
    local a, b, c = inl[i], inl[i + 1], inl[i + 2]
    if a.t == "Str" and b.t == "Space" and c.t == "Str" and a.text:match("%d$") then
      local u = c.text:gsub("[%.,;:%)]+$", "")
      if UNIDADES[u] then inl[i + 1] = pandoc.Str("\u{00A0}") end
    end
  end
  return inl
end

return K
