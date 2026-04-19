from abc import ABC, abstractmethod


class IVoltageTubeDB(ABC):
    """Напряжение на трубке по материалу (type_metall) и радиационной толщине (voltage_tube)."""

    @abstractmethod
    def get_max_voltage_kv_for_material_and_thickness(
        self, material_label: str, radiation_thickness_mm: float
    ) -> float:
        """
        Максимально допустимое напряжение, кВ, из public.voltage_tube.
        material_label сопоставляется с type_metall.material (без учёта регистра, trim).

        Если материал не найден, нет строк voltage_tube или толщина не задана — 0.0.
        """
        pass
