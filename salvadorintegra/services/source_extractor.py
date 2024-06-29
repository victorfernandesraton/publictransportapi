import io
import re
from abc import ABC, abstractmethod
from itertools import tee
from typing import Dict, List

import httpx
import pdfplumber


class ServiceDownloader(ABC):
    @abstractmethod
    def execute(self) -> bytes:
        pass


class ServiceDownloaderPDF(ServiceDownloader):
    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"

    def execute(self) -> bytes:
        response = httpx.get(self.url)
        response.raise_for_status()
        return response.content


class SourceExtractor:
    def __init__(self, service_downloader: ServiceDownloader):
        self.service_downloader = service_downloader
        self.routes: Dict[str, List[str]] = {}

    def execute(self):
        pdf_content = self.service_downloader.execute()
        tables = self._extract_tables_from_pdf(io.BytesIO(pdf_content))
        self.routes = self._parse_routes(tables)

    @staticmethod
    def _extract_tables_from_pdf(pdf_content: io.BytesIO) -> List[List[str]]:
        tables = []
        with pdfplumber.open(pdf_content) as pdf:
            for page in pdf.pages:
                inner_table = page.extract_table()
                if inner_table:
                    tables.extend(inner_table)
        return tables

    @staticmethod
    def _parse_routes(table: List[List[str]]) -> Dict[str, List[str]]:
        routes: Dict[str, List[str]] = {}
        regex_step = re.compile(r"(\d+°)")
        route_left = None
        route_right = None

        iter1, iter2 = tee(table)

        valid_rows = filter(lambda row: len(row) == 2, iter1)

        for left, right in valid_rows:
            if not right:
                continue

            if not regex_step.search(left):
                route_left = left
            elif route_left:
                routes.setdefault(route_left, []).append(left)

            if not regex_step.search(right):
                route_right = right
            elif route_right:
                routes.setdefault(route_right, []).append(right)

        return routes
