from repositories.Interfaces.i_repository import IRepository
from repositories.Interfaces.i_control_methods_db import IControlMethodsDB
from repositories.Interfaces.i_regulatory_documents_db import IRegulatoryDocumentsDB
from repositories.Interfaces.i_type_of_welded_joint_db import ITypeOfWeldedJointDB
from repositories.Interfaces.i_params_by_type_welding_joint_db import (
    IParamsByTypeWeldingJointDB,
)
from repositories.Interfaces.i_cheme_control_db import IChemeControlDB
from repositories.Interfaces.i_materials_db import IMaterialsDB
from repositories.Interfaces.i_material_standard_db import IMaterialStandardDB
from services.tech_card import TechCardData
from typing import Any, Dict, List, Optional, Union
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDataBase(
    IRepository[TechCardData],
    IControlMethodsDB,
    IRegulatoryDocumentsDB,
    ITypeOfWeldedJointDB,
    IParamsByTypeWeldingJointDB,
    IChemeControlDB,
    IMaterialsDB,
    IMaterialStandardDB,
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

    def get_welded_joint_image_ref(
        self, joint_name_or_id: Union[str, int]
    ) -> Optional[str]:
        if not self.cursor:
            return None
        try:
            if isinstance(joint_name_or_id, int):
                self.cursor.execute(
                    "SELECT image_ref FROM public.type_of_welded_joint WHERE id = %s",
                    (joint_name_or_id,),
                )
            else:
                key = str(joint_name_or_id).strip()
                if not key:
                    return None
                if key.isdigit():
                    self.cursor.execute(
                        "SELECT image_ref FROM public.type_of_welded_joint WHERE id = %s",
                        (int(key),),
                    )
                else:
                    self.cursor.execute(
                        "SELECT image_ref FROM public.type_of_welded_joint "
                        "WHERE lower(btrim(name::text)) = lower(btrim(%s::text)) "
                        "LIMIT 1",
                        (key,),
                    )
            row = self.cursor.fetchone()
            if not row:
                return None
            ref = row.get("image_ref") if isinstance(row, dict) else row["image_ref"]
            if ref is None or (isinstance(ref, str) and not ref.strip()):
                return None
            return str(ref).strip()
        except psycopg2.Error as e:
            print("get_welded_joint_image_ref:", e)
            return None

    def get_params_by_welded_joint_type(
        self, joint_name_or_id: Union[str, int]
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            if isinstance(joint_name_or_id, int):
                cond = "twj.id = %s"
                param = (joint_name_or_id,)
            else:
                key = str(joint_name_or_id).strip()
                if not key:
                    return []
                if key.isdigit():
                    cond = "twj.id = %s"
                    param = (int(key),)
                else:
                    cond = "lower(btrim(twj.name::text)) = lower(btrim(%s::text))"
                    param = (key,)
            self.cursor.execute(
                "SELECT p.id, p.name, p.subtitle FROM public.params_by_type_welding_joint p "
                "INNER JOIN public.type_of_welded_joint twj ON twj.id = p.type_of_welded_joint_id "
                f"WHERE {cond} ORDER BY p.id",
                param,
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_params_by_welded_joint_type:", e)
            return []

    def get_control_schemes_for_welded_joint(
        self, joint_name_or_id: Union[str, int]
    ) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            if isinstance(joint_name_or_id, int):
                cond = "twj.id = %s"
                param = (joint_name_or_id,)
            else:
                key = str(joint_name_or_id).strip()
                if not key:
                    return []
                if key.isdigit():
                    cond = "twj.id = %s"
                    param = (int(key),)
                else:
                    cond = "lower(btrim(twj.name::text)) = lower(btrim(%s::text))"
                    param = (key,)
            self.cursor.execute(
                "SELECT cc.id, cc.name, cc.image_ref "
                "FROM public.cheme_control cc "
                "INNER JOIN public.weld_type_to_scheme wts ON wts.cheme_control_id = cc.id "
                "INNER JOIN public.type_of_welded_joint twj ON twj.id = wts.type_of_welded_joint_id "
                f"WHERE {cond} ORDER BY cc.id",
                param,
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_control_schemes_for_welded_joint:", e)
            return []

    def get_materials(self) -> List[Dict[str, Any]]:
        if not self.cursor:
            return []
        try:
            self.cursor.execute(
                "SELECT id, material FROM public.type_metall ORDER BY id"
            )
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.Error as e:
            print("get_materials:", e)
            return []

    def get_material_standard_id(
        self, material_name_or_id: Union[str, int]
    ) -> Optional[int]:
        if not self.cursor:
            return None
        try:
            if isinstance(material_name_or_id, int):
                self.cursor.execute(
                    "SELECT id_standard FROM public.type_metall WHERE id = %s",
                    (material_name_or_id,),
                )
            else:
                key = str(material_name_or_id).strip()
                if not key:
                    return None
                if key.isdigit():
                    self.cursor.execute(
                        "SELECT id_standard FROM public.type_metall WHERE id = %s",
                        (int(key),),
                    )
                else:
                    self.cursor.execute(
                        "SELECT id_standard FROM public.type_metall "
                        "WHERE lower(btrim(material::text)) = lower(btrim(%s::text)) "
                        "LIMIT 1",
                        (key,),
                    )

            row = self.cursor.fetchone()
            if not row:
                return None

            value = row.get("id_standard") if isinstance(row, dict) else row["id_standard"]
            if value is None:
                return None
            return int(value)
        except (psycopg2.Error, TypeError, ValueError) as e:
            print("get_material_standard_id:", e)
            return None
