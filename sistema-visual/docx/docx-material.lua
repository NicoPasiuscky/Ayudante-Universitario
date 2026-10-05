--[[
docx-material.lua - filtro de Pandoc para el material impreso en Word (.docx) del
sistema v4: parcial digitalizado, modelo de practica y hojas de soluciones
(resultados y resolucion). Lo usa construir_docx.py (--tipo parcial|soluciones).

Lee el MISMO Markdown que alimenta el HTML A4 (incluir/material.lua):

  ::: {.cabecera-original titulo="..."}   encabezado fiel del original, SIN los renglones Legajo,
        Apellido y nombre y Curso ni la fecha: titulo a la izquierda,
        filete grueso; si se da fecha="..." va a la derecha; un renglon por parrafo
  ::: consigna                                        consigna general, entre filetes
  ::: {.ejercicio n=1 espacio=46}   tabla de dos columnas: "1)" colgado | enunciado, incisos,
        datos, figura y el espacio en blanco (parrafo vacio de alto exacto, sin lineas). Con
        espacio=, la fila no se parte entre hojas (como break-inside: avoid del HTML)
  ::: {.espacio mm=46}              espacio en blanco suelto
  ::: resultado / supuesto / errata / datos   "Resultado." (verde), "Supuesto." (lapiz),
        "Errata." (rojo), "Datos." en linea
  ::: subtitulo                     bajada de la hoja de soluciones, con filete
  ::: tabla-resultados + tabla      hoja de resultados
  ![epigrafe](figura.png){width=76mm}   figura (construir_docx.py ya paso el SVG a PNG)
El rotulo tipo plano (una sola linea en el margen superior: "materia | tema" del lado interior
y "Hoja n de N" del exterior; sin datos personales ni fecha) lo arma construir_docx.py en la
cabecera de la seccion; no hay pie.
]]
local dir = (PANDOC_SCRIPT_FILE or ""):match("^(.*)[/\\][^/\\]*$") or "."
local K = dofile(dir .. "/docx-comun.lua")
local tiene, texto, run, TAB, estilo = K.tiene, K.texto, K.run, K.TAB, K.estilo

local avisos = {}
local ROTULOS = {resultado = "Resultado.", supuesto = "Supuesto.", errata = "Errata.", datos = "Datos."}

local function rotulo(clase, palabra)
  if clase == "resultado" then return pandoc.Strong({pandoc.Emph(texto(palabra))}) end
  if clase == "datos" then return pandoc.Strong({pandoc.Emph(texto(palabra))}) end
  return pandoc.Strong(texto(palabra))
end

local trabajo = {
  Inlines = K.espacio_duro,

  Div = function(d)
    if tiene(d, "cabecera-original") then
      local titulo = d.attributes.titulo or ""
      local fecha = d.attributes.fecha or ""
      local bl = pandoc.Blocks({estilo("CabOriginal", {pandoc.Para({run("CabTitulo", titulo), TAB, run("CabFecha", fecha)})})})
      bl:insert(estilo("CabOriginalDato", d.content))
      return bl
    end
    if tiene(d, "consigna") then
      return estilo("Consigna", d.content)
    end
    if tiene(d, "ejercicio") then
      local n = d.attributes.n
      if not n then table.insert(avisos, "ejercicio sin n=") end
      local espacio = d.attributes.espacio
      local cuerpo = pandoc.Blocks(d.content)
      if espacio then cuerpo:insert(K.espacio(espacio)) end
      local num = {estilo("EjercicioN", {pandoc.Plain({pandoc.Str((n or "") .. ")")})})}
      return K.tabla({{num, {estilo("EjercicioP", cuerpo)}}}, {0.05, 0.95},
        espacio and "TablaEjercicio" or "TablaEjercicioLibre")
    end
    if tiene(d, "espacio") then
      return K.espacio(d.attributes.mm or "30")
    end
    for clase, palabra in pairs(ROTULOS) do
      if tiene(d, clase) then
        local st = clase:sub(1, 1):upper() .. clase:sub(2)
        d.content = K.anteponer(d.content, {rotulo(clase, palabra)})
        return estilo(st, d.content)
      end
    end
    if tiene(d, "subtitulo") then
      return estilo("Subtitulo", d.content)
    end
    if tiene(d, "tabla-resultados") then
      return d:walk({Table = function(t)
        t.attr = pandoc.Attr("", {}, {["custom-style"] = "TablaResultados"})
        return t
      end})
    end
    if tiene(d, "hoja-aparte") or tiene(d, "salto") then return K.hoja_nueva() end
  end,

  Figure = function(fig)
    -- figura con epigrafe: imagen y epigrafe chico debajo
    local bl = pandoc.Blocks({})
    bl:extend(fig.content)
    local cap = fig.caption.long
    if #cap > 0 then bl:insert(estilo("EpigrafeMaterial", cap)) end
    return pandoc.Div(bl)
  end,
}

function Pandoc(doc)
  doc = doc:walk(trabajo)
  for _, a in ipairs(avisos) do io.stderr:write("[docx-material.lua] " .. a .. "\n") end
  return doc
end
