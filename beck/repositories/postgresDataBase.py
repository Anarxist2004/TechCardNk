from repositories.Interfaces.i_repository import IRepository
from services.tech_card import TechCardData
from services.tech_card import TypeObjectControl
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(IRepository[TechCardData]):
    
    def __init__(self, dsn: str):
        self._cards: List[TechCardData] = []
        try:
            self.conn = psycopg2.connect(dsn)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Подключение к базе успешно")
        except psycopg2.Error as e:
            print("Ошибка при подключении к базе:", e)
            self.conn = None
            self.cursor = None
