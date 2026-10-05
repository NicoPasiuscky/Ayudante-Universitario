--[[
docx.lua - filtro de Pandoc para Word (.docx) del sistema v4.
Lo usa construir_docx.py; no correrlo suelto con otra plantilla.

  - Caratula: si el metadato `caratula_xml` trae la ruta de un archivo con
    OpenXML (lo arma construir_docx.py desde el JSON), lo inserta al principio.
  - Titulos: `#` y `##` se numeran (1, 1.1) con el numero en azul, colgado a la
    izquierda (estilo de caracter "Numero" + tabulacion). `{-}` sin numero.
  - Figuras y tablas con epigrafe: "Figura 1." / "Tabla 1." con el numero en
    azul. Identificadores `#fig:x`, `#tbl:x` (en la tabla o en un div que la
    envuelve), `#sec:x`.
  - Referencias cruzadas: `[](#fig:x)` -> "figura 1", `[](#tbl:x)` -> "tabla 1",
    `[](#sec:x)` -> "sección 2" (estilo de caracter "Referencia", azul).
  - Bloques: `::: resultado` (rotulo "Resultado."), `::: supuesto` (rotulo
    "Supuesto.", en lapiz), `::: enunciado` (texto fiel de la consigna, con
    sangria), `::: salto` (salto de hoja).
El color nunca va en titulos ni fondos: solo en numeros y referencias.
]]

local numeros = {}          -- id -> {tipo, numero}
local h1, h2, nfig, ntab = 0, 0, 0, 0

local function xml_escape(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

local function run_estilo(estilo, texto)
  return pandoc.RawInline("openxml",
    '<w:r><w:rPr><w:rStyle w:val="' .. estilo .. '"/></w:rPr><w:t xml:space="preserve">'
    .. xml_escape(texto) .. '</w:t></w:r>')
end

local TAB = pandoc.RawInline("openxml", "<w:r><w:tab/></w:r>")

local function rotulo(palabra, n)
  -- "Figura 1." : palabra en negrita de tinta, numero en azul
  return {pandoc.Strong({pandoc.Str(palabra), pandoc.Space()}), run_estilo("NumeroRotulo", tostring(n)),
          pandoc.Strong({pandoc.Str(".")}), pandoc.Space()}
end

local function anteponer(bloques, inlines)
  if #bloques == 0 then
    return {pandoc.Plain(inlines)}
  end
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
  local tbl_div = nil
  local function tabla(t, id_div)
    local cap = t.caption and t.caption.long or {}
    if #cap == 0 then return t end
    ntab = ntab + 1
    local id = (t.identifier ~= "" and t.identifier) or id_div
    if id and id ~= "" then numeros[id] = {"tabla", tostring(ntab)} end
    t.caption.long = anteponer(cap, rotulo("Tabla", ntab))
    return t
  end
  local blocks = pandoc.List()
  local function procesar(lista)
    local out = pandoc.List()
    for _, b in ipairs(lista) do
      if b.t == "Header" and b.level <= 2 then
        if not b.classes:includes("unnumbered") then
          local n
          if b.level == 1 then h1 = h1 + 1; h2 = 0; n = tostring(h1)
          else h2 = h2 + 1; n = h1 .. "." .. h2 end
          if b.identifier ~= "" then numeros[b.identifier] = {"sección", n} end
          local c = {run_estilo("Numero", n), TAB}
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
        return run_estilo("Referencia", tipo .. " " .. n)
      end
    end,
    Div = function(d)
      if d.classes:includes("resultado") then
        d.attributes["custom-style"] = "Resultado"
        d.content = anteponer(d.content, {pandoc.Strong({pandoc.Str("Resultado.")}), pandoc.Space()})
        return d
      elseif d.classes:includes("supuesto") then
        d.attributes["custom-style"] = "Supuesto"
        d.content = anteponer(d.content, {pandoc.Strong({pandoc.Str("Supuesto.")}), pandoc.Space()})
        return d
      elseif d.classes:includes("enunciado") then
        d.attributes["custom-style"] = "Enunciado"
        return d
      elseif d.classes:includes("salto") then
        return pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
      end
    end,
  })
end

function Pandoc(doc)
  doc = numerar(doc)
  doc = referencias(doc)
  local ruta = doc.meta.caratula_xml
  if ruta then
    ruta = pandoc.utils.stringify(ruta)
    local f = io.open(ruta, "rb")
    if f then
      local xml = f:read("a")
      f:close()
      doc.blocks:insert(1, pandoc.RawBlock("openxml", xml))
      -- Logo opcional (caratula.logo del JSON): primer parrafo de la hoja 1, antes del encabezado
      local logo = doc.meta.caratula_logo
      if logo then
        local ancho = pandoc.utils.stringify(doc.meta.caratula_logo_ancho or "")
        local img = pandoc.Image({pandoc.Str("Logo de la institución")},
                                 pandoc.utils.stringify(logo), "", pandoc.Attr("", {}, {width = ancho}))
        doc.blocks:insert(1, pandoc.Div({pandoc.Para({img})}, pandoc.Attr("", {}, {["custom-style"] = "Caratula Logo"})))
      end
    else
      io.stderr:write("docx.lua: no se encontro la caratula " .. ruta .. "\n")
    end
  end
  return doc
end
