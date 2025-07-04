"""Tools for route status queries."""
from langchain_core.tools import tool
import re
import requests
from io import BytesIO
import PyPDF2

@tool
def buscar_estado_rutas(query: str) -> str:
    """
    Descarga el PDF de la DPV Neuquén, extrae el texto y busca información de rutas.
    - Si la consulta menciona un código específico (p.ej., 'P005'), devuelve el bloque correspondiente.
    - Si la consulta contiene términos descriptivos (ej. "neuquén centenario"), intenta identificar el tramo asociado.
    - Si la consulta es "rutas disponibles", devuelve todas las rutas con sus códigos.
    - En caso de ser una consulta general, lista los códigos disponibles.
    Además, se extrae de la cabecera del PDF la información de la última actualización (hora y fecha)
    y se incluye en la respuesta.
    """
    url = "https://w2.dpvneuquen.gov.ar/ParteDiario.pdf"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        return f"Error al descargar la información: {str(e)}"

    f = BytesIO(response.content)
    try:
        reader = PyPDF2.PdfReader(f)
    except Exception as e:
        return f"Error al leer el PDF: {str(e)}"

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    update_match = re.search(
        r"Información Actualizada a las\s+([\d:]+hs\.)\s+del\s+(\d{2}/\d{2}/\d{4})",
        full_text,
        re.IGNORECASE,
    )
    if update_match:
        update_info = f"Última actualización: {update_match.group(1)} {update_match.group(2)}\n\n"
    else:
        update_info = ""

    routes = re.findall(r"([PN]\d{3})", full_text)
    unique_routes = list(dict.fromkeys(routes))

    route_details = {}
    for code in unique_routes:
        pattern = re.compile(
            re.escape(code) + r"(.*?)(?=[PN]\d{3}|$)", re.DOTALL
        )
        m = pattern.search(full_text)
        if m:
            block = code + m.group(1).strip()
            route_details[code] = block

    query_lower = query.lower()
    if query_lower == "rutas disponibles":
        lines = [f"{update_info}Lista de todas las rutas disponibles:"]
        for code in sorted(unique_routes):
            desc = route_details[code]
            short_desc = desc[len(code):].strip()
            if len(short_desc) > 100:
                short_desc = short_desc[:100] + "..."
            lines.append(f"- {code}: {short_desc}")
        return "\n".join(lines)

    for code in unique_routes:
        if code.lower() in query_lower:
            return f"{update_info}Información para la ruta {code}:\n{route_details.get(code, 'No se encontró el detalle correspondiente.')}"

    query_words = query_lower.split()
    matching = []
    for code, block in route_details.items():
        block_lower = block.lower()
        if all(w in block_lower for w in query_words):
            matching.append(code)

    if len(matching) == 1:
        code = matching[0]
        return f"{update_info}Información para la ruta {code}:\n{route_details[code]}"
    elif len(matching) > 1:
        lines = [f"{update_info}Encontré múltiples rutas que podrían corresponder:"]
        for code in matching:
            desc = route_details[code]
            short_desc = desc[len(code):].strip()
            if len(short_desc) > 80:
                short_desc = short_desc[:80] + "..."
            lines.append(f"- {code}: {short_desc}")
        lines.append("¿Podrías especificar cuál te interesa?")
        return "\n".join(lines)
    else:
        lines = [f"{update_info}Estado actual de las rutas en Neuquén:"]
        for code in sorted(unique_routes):
            desc = route_details[code]
            short_desc = desc[len(code):].strip()
            if len(short_desc) > 100:
                short_desc = short_desc[:100] + "..."
            lines.append(f"- {code}: {short_desc}")
        lines.append("\n¿Sobre cuál de estos tramos te gustaría información más detallada?")
        return "\n".join(lines)
