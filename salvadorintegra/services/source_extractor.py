import io
import re
from itertools import tee
from typing import Dict, List, Tuple

import httpx
import pdfplumber

TOTAL_COLUMNS = 2


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
                if inner_table is not None:
                    tables.extend(inner_table)
        return tables

    @staticmethod
    def split_tables(table: List[List[str]]) -> Tuple[List[str], list[str]]:
        iter1, _iter2 = tee(table)

        valid_rows = filter(lambda row: len(row) == TOTAL_COLUMNS, iter1)
        valid_rows = filter(
            lambda row: row[0] is not None and row[1] is not None, valid_rows
        )
        left_column = [row[0] for row in table if len(row) == TOTAL_COLUMNS and row[0]]
        right_column = [row[1] for row in table if len(row) == TOTAL_COLUMNS and row[1]]

        return left_column, right_column

    @staticmethod
    def parse_table_to_dict(rows) -> Dict[str, List[str]]:
        result: Dict[str, list[str]] = {}
        route = None
        regex_step = re.compile(r"(\d+°)")
        for row in rows:
            if not regex_step.search(row):
                route = row
            elif route:
                result.setdefault(route, []).append(row)

        return result
