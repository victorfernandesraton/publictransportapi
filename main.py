import requests
import pdfplumber
import io
import re

def fetch_pdf(url: str) -> io.BytesIO:
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)

def extract_tables_from_pdf(pdf_content: io.BytesIO) -> list:
    tables = []
    with pdfplumber.open(pdf_content) as pdf:
        for index, value in enumerate(pdf.pages):
            print(f"read page {index}")
            table = value.extract_table()
            if table:
                tables.extend(table)
    return tables

def parse_routes(table: list) -> dict:
    routes = {}
    regex_step = re.compile(r"(\d+°)")
    route_left = None
    route_right = None

    for row in table:
        if len(row) != 2:
            continue

        left, right = row

        if not right:
            continue

        if not regex_step.search(left):
            route_left = left
        else:
            routes.setdefault(route_left, []).append(left)

        if not regex_step.search(right):
            route_right = right
        else:
            routes.setdefault(route_right, []).append(right)

    return routes

if __name__ == "__main__":
    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    pdf_content = fetch_pdf(url)
    table = extract_tables_from_pdf(pdf_content)
    print(len(table))
    routes = parse_routes(table)
    print(routes.keys())
