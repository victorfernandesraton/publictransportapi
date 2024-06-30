import io
import re
from itertools import tee
from typing import Dict, List

import httpx
import pdfplumber


class SourceExtractor:
    @staticmethod
    def get_file_content_by_url(
        url: str = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf",
    ) -> bytes:
        response = httpx.get(url)
        response.raise_for_status()
        return response.content

    @staticmethod
    def get_tables_from_bytes(data: bytes) -> List[List[str]]:
        tables = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                inner_table = page.extract_table()
                if inner_table:
                    tables.extend(inner_table)
        return tables

    @staticmethod
    def parse_tables_to_dict(table: List[List[str]]) -> Dict[str, List[str]]:
        routes: Dict[str, List[str]] = {}
        regex_step = re.compile(r"(\d+°)")
        route_left = None
        route_right = None

        iter1, iter2 = tee(table)

        valid_rows = filter(lambda row: len(row) == 2, iter1)
        valid_rows = filter(
            lambda row: row[0] is not None and row[1] is not None, valid_rows
        )

        for left, right in valid_rows:
            if not regex_step.search(left):
                route_left = left
            elif route_left:
                routes.setdefault(route_left, []).append(left)

            if not regex_step.search(right):
                route_right = right
            elif route_right:
                routes.setdefault(route_right, []).append(right)

        return routes

    def execute(self) -> Dict[str, List[str]]:
        content = self.get_file_content_by_url()
        table = self.get_tables_from_bytes(content)
        return self.parse_tables_to_dict(table)
