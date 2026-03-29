from repositories.Interfaces.i_repository import IRepository
from repositories.Interfaces.i_control_methods_db import IControlMethodsDB
from repositories.Interfaces.i_regulatory_documents_db import IRegulatoryDocumentsDB
from services.tech_card import TechCardData
from typing import Any, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(IRepository[TechCardData], IControlMethodsDB, IRegulatoryDocumentsDB):

    def __init__(self, dsn: str):
        IRepository.__init__(self)
        self._cards: List[TechCardData] = []
        try:
            self.conn = psycopg2.connect(dsn)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Подключение к базе успешно")
        except psycopg2.Error as e:
            print("Ошибка при подключении к базе:", e)
            self.conn = None
            self.cursor = None

    def get_control_methods(self) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, name FROM public.control_methods ORDER BY id"
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_control_methods:", e)
            return []

    def get_regulatory_documents(self) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, control_methods_id, name FROM public.regulatory_documents "
                "ORDER BY id"
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_regulatory_documents:", e)
            return []

    def get_regulatory_documents_by_control_method_id(
        self, control_method_id: int
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, control_methods_id, name FROM public.regulatory_documents "
                "WHERE control_methods_id = %s ORDER BY id",
                (control_method_id,),
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_regulatory_documents_by_control_method_id:", e)
            return []

    def get_regulatory_documents_for_method_name(
        self, method_name: str
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT rd.id, rd.control_methods_id, rd.name "
                "FROM public.regulatory_documents rd "
                "INNER JOIN public.control_methods cm ON cm.id = rd.control_methods_id "
                "WHERE cm.name = %s ORDER BY rd.id",
                (method_name,),
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_regulatory_documents_for_method_name:", e)
            return []
