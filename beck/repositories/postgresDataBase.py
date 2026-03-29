from repositories.Interfaces.i_repository import IRepository
from repositories.Interfaces.i_control_methods_db import IControlMethodsDB
from services.tech_card import TechCardData
from typing import Any, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(IRepository[TechCardData], IControlMethodsDB):

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
