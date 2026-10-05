--[[ espejo.lua - modulo comun de estudio.lua (Hoja A4), material.lua y tp.lua para el
parametro de margenes ESPEJADOS o IGUALES:

  Margenes espejados (doble faz) solo si se imprime. Si el documento NO se imprime (por
  ejemplo un TP que la catedra recibe por el aula virtual), los margenes son iguales en todas
  las hojas: izquierdo 20 mm, derecho 10 mm, superior 15 mm, inferior 5 mm, y "Hoja n de N"
  siempre del mismo lado (el derecho), con el texto de la cabeza (seccion, trabajo, o materia y
  tema) siempre del izquierdo.

Metadato de Pandoc:   -M espejo=false     (por defecto true: espejado, como siempre)
                      -M imprime=false    (alias: "no se imprime" = sin espejo)
Efecto:  en el <head> se agrega un <style> que rehace la regla @page :left como la :right (los
         margenes y las cajas de la cabeza) y en <html> se pone data-espejo="no" (lo lee
         herramientas/imprimir_a4.py para saber con que se armo el HTML). Un <style> suelto en el
         cuerpo no lo toma Paged.js; un script que lo agrega al <head> mientras se lee la pagina si.
Los valores de margen (20 y 10 mm) son los de --hoja-* de css/tokens.css; la regla 23 de
verificar_reglas.py comprueba que sigan siendo los mismos.
]]
local M = {}

-- valores de css/tokens.css (--hoja-interior, --hoja-exterior): los comprueba la regla 23
M.INTERIOR = "20mm"
M.EXTERIOR = "10mm"

-- true (espejado) salvo que el metadato diga espejo=false o imprime=false
function M.espejado(meta)
  local function falso(v)
    if v == nil then return false end
    if v == false then return true end
    local s = pandoc.utils.stringify(v):lower()
    return s == "false" or s == "no" or s == "0"
  end
  return not (falso(meta.espejo) or falso(meta.imprime))
end

local ESTILO_CAJA = 'font-family: "Estudio Sans", sans-serif; font-size: 8pt; vertical-align: bottom; padding-bottom: 3.5mm;'

-- Caja "Hoja n de N" (la misma en todos los CSS A4)
M.CAJA_HOJA = 'content: "Hoja " counter(page) " de " counter(pages); ' .. ESTILO_CAJA .. ' color: var(--tinta);'

-- Caja de texto de la cabeza del lado interior, con declaraciones completas (Paged.js no fusiona
-- la caja de margen con la de otra regla @page): extra son las declaraciones propias de cada pieza
function M.caja_texto(contenido, color, extra)
  return 'content: ' .. contenido .. '; ' .. ESTILO_CAJA .. ' color: ' .. color .. '; text-align: left; ' .. (extra or "")
end

-- @page :left igual a :right: mismos margenes, "Hoja n de N" a la derecha y el texto a la izquierda
function M.css_sin_espejo(caja_izquierda)
  return '@page :left { margin-left: ' .. M.INTERIOR .. '; margin-right: ' .. M.EXTERIOR .. '; '
    .. '@top-right { ' .. M.CAJA_HOJA .. ' text-align: right; } '
    .. '@top-left { ' .. caja_izquierda .. ' } }'
end

-- Bloque HTML con el script que agrega el <style> al <head> y marca <html data-espejo="no">
function M.script(css, sin_espejo)
  local s = "<script>(function(){"
  if sin_espejo then s = s .. "document.documentElement.setAttribute('data-espejo','no');" end
  s = s .. "var s=document.createElement('style');s.textContent="
    .. '"' .. (css:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("</", "<\\/")) .. '"'
    .. ";document.head.appendChild(s);})();</script>"
  return pandoc.RawBlock("html", s)
end

return M
