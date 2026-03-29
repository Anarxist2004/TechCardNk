from repositories.Interfaces.i_repository import IRepository
from repositories.Interfaces.i_control_methods_db import IControlMethodsDB
from repositories.Interfaces.i_regulatory_documents_db import IRegulatoryDocumentsDB
from repositories.Interfaces.i_type_of_welded_joint_db import ITypeOfWeldedJointDB
from services.tech_card import TechCardData
from typing import Any, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(
    IRepository[TechCardData],
    IControlMethodsDB,
    IRegulatoryDocumentsDB,
    ITypeOfWeldedJointDB,
):

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
        key = (method_name or "").strip()
        if not key:
            return []
        try:
            self.cursor.execute(
                "SELECT rd.id, rd.control_methods_id, rd.name "
                "FROM public.regulatory_documents rd "
                "INNER JOIN public.control_methods cm ON cm.id = rd.control_methods_id "
                "WHERE lower(btrim(cm.name::text)) = lower(btrim(%s::text)) "
                "ORDER BY rd.id",
                (key,),
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_regulatory_documents_for_method_name:", e)
            return []

    def get_type_of_welded_joints(self) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, regulatory_documents_id, name, image_ref "
                "FROM public.type_of_welded_joint ORDER BY id"
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_type_of_welded_joints:", e)
            return []

    def get_type_of_welded_joints_by_regulatory_document_id(
        self, regulatory_document_id: int
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, regulatory_documents_id, name, image_ref "
                "FROM public.type_of_welded_joint "
                "WHERE regulatory_documents_id = %s ORDER BY id",
                (regulatory_document_id,),
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_type_of_welded_joints_by_regulatory_document_id:", e)
            return []

    def get_type_of_welded_joints_for_regulatory_document_name(
        self, regulatory_document_name: str
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        key = (regulatory_document_name or "").strip()
        if not key:
            return []
        # Строка из цифр — часто приходит id документа с фронта как str
        if key.isdigit():
            return self.get_type_of_welded_joints_by_regulatory_document_id(int(key))
        try:
            self.cursor.execute(
                "SELECT twj.id, twj.regulatory_documents_id, twj.name, twj.image_ref "
                "FROM public.type_of_welded_joint twj "
                "INNER JOIN public.regulatory_documents rd ON rd.id = twj.regulatory_documents_id "
                "WHERE lower(btrim(rd.name::text)) = lower(btrim(%s::text)) "
                "ORDER BY twj.id",
                (key,),
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_type_of_welded_joints_for_regulatory_document_name:", e)
            return []
