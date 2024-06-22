import io
import re
from abc import ABC, abstractmethod

import pdfplumber
import requests


class ServiceDownloader(ABC):
    @abstractmethod
    def execute(self) -> bytes:
        pass


class ServiceDownloaderPDF:
    def __init__(self, url: str):
        self.url = url

    def execute(self) -> bytes:
        response = requests.get(self.url)
        response.raise_for_status()
        return response.content


class SourceExtractor:
    def __init__(self, service_downloader: ServiceDownloader):
        self.service_downloader = service_downloader
        self.routes: dict[str, list[str]] = {}

    def execute(self):
        pdf_content = self.service_downloader.execute()
        table = self.__extract_tables_from_pdf(io.BytesIO(pdf_content))
        self.routes = self.__parse_routes(table)

    @staticmethod
    def __extract_tables_from_pdf(pdf_content: io.BytesIO) -> list:
        tables = []
        with pdfplumber.open(pdf_content) as pdf:
            for _index, value in enumerate(pdf.pages):
                inner_table = value.extract_table()
                if inner_table:
                    tables.extend(inner_table)
        return tables

    @staticmethod
    def __parse_routes(table: list) -> dict:
        routes: dict[str, list] = {}
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
            elif route_left:
                routes.setdefault(route_left, []).append(left)

            if not regex_step.search(right):
                route_right = right
            elif route_right:
                routes.setdefault(route_right, []).append(right)

        return routes
