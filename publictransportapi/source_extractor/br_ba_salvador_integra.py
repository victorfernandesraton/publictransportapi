import io
import re
from datetime import datetime
from hashlib import sha256
from itertools import tee
from typing import Dict, List, Tuple

import httpx
import pdfplumber
from sqlalchemy import select
from sqlalchemy.orm import Session

from publictransportapi.domain import Source, Systems, TransportRoutes, TransportStops
from publictransportapi.source_extractor.extractor import SourceExtractorService

TOTAL_COLUMNS = 2


class SourceExtractor(SourceExtractorService):
    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    data = bytes()

    def __init__(self, session: Session, system: Systems):
        self.session = session
        self.system = system

    @staticmethod
    def get_file_content_by_url(
        url: str,
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

    def get_dict(self, data: bytes) -> Dict[str, List[str]]:
        tables = self.get_tables_from_bytes(data)
        left_column, right_column = self.split_tables(tables)
        return {
            **self.parse_table_to_dict(left_column),
            **self.parse_table_to_dict(right_column),
        }

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

    def save_source(self) -> Source:
        self.data = self.get_file_content_by_url(self.url)
        hashData = sha256(self.data).hexdigest()

        source = Source(
            url=self.url,
            system_id=self.system.id,
            hash=hashData,
        )
        has_source = self.session.scalar(
            select(Source).where(
                Source.hash == source.hash and Source.system_id == self.system.id
            )
        )
        if has_source:
            has_source.updated_at = datetime.utcnow()
            self.session.commit()
            return has_source

        self.session.add(source)
        self.session.commit()
        return source

    def save_transport_routes(self, source: Source):
        dict_data = self.get_dict(self.data)
        for route, stops in dict_data.items():
            result = re.search(r"(\d+)\s(-\s)?(.*)", route)
            if not result:
                raise Exception(f"Invalid route: {route}")
            transport_routes = TransportRoutes(
                code=int(result.group(1)), label=route, source_id=source.id
            )
            self.session.add(transport_routes)
            self.session.commit()

            self.session.begin()
            for idx, stop in enumerate(stops):
                transport_stops = TransportStops(
                    label=stop,
                    order=idx,
                    route_id=transport_routes.id,
                )
                self.session.add(transport_stops)
            self.session.commit()
