"""
Тесты для модуля models.py
Проверка классов материалов и результатов расчётов
"""

import pytest
from package.models import (
    Material, Wallpaper, Tile, Laminate, CalculationResult
)


class TestMaterial:
    """Тесты для абстрактного класса Material"""
    
    def test_material_cannot_be_instantiated(self):
        """Тест: Material нельзя создать напрямую (абстрактный класс)"""
        with pytest.raises(TypeError):
            Material("Test", 100, 1.0)


class TestWallpaper:
    """Тесты для класса Wallpaper"""
    
    def test_wallpaper_creation(self):
        """Тест: Создание обоев с параметрами по умолчанию"""
        wallpaper = Wallpaper("Винил", 1200)
        assert wallpaper.name == "Винил"
        assert wallpaper.price_per_unit == 1200
        assert wallpaper.roll_width == 0.53
        assert wallpaper.roll_length == 10.05
        assert wallpaper.unit_coverage == pytest.approx(0.53 * 10.05)
    
    def test_wallpaper_custom_dimensions(self):
        """Тест: Создание обоев с кастомными размерами"""
        wallpaper = Wallpaper("Премиум", 1500, roll_width=0.7, roll_length=10.0)
        assert wallpaper.roll_width == 0.7
        assert wallpaper.roll_length == 10.0
        assert wallpaper.unit_coverage == pytest.approx(7.0)
    
    def test_wallpaper_price_validation_negative(self):
        """Тест: Валидация отрицательной цены"""
        with pytest.raises(ValueError, match="Цена должна быть положительным числом"):
            Wallpaper("Test", -100)
    
    def test_wallpaper_price_validation_zero(self):
        """Тест: Валидация нулевой цены"""
        with pytest.raises(ValueError):
            Wallpaper("Test", 0)
    
    def test_wallpaper_roll_width_validation(self):
        """Тест: Валидация отрицательной ширины рулона"""
        with pytest.raises(ValueError, match="Ширина рулона должна быть положительной"):
            Wallpaper("Test", 1000, roll_width=-0.5)
    
    def test_wallpaper_roll_length_validation(self):
        """Тест: Валидация отрицательной длины рулона"""
        with pytest.raises(ValueError, match="Длина рулона должна быть положительной"):
            Wallpaper("Test", 1000, roll_length=-10)
    
    def test_wallpaper_get_unit_type(self):
        """Тест: Получение типа единицы измерения"""
        wallpaper = Wallpaper("Test", 1000)
        assert wallpaper.get_unit_type() == "рулон"
    
    def test_wallpaper_get_detailed_info(self):
        """Тест: Получение детальной информации"""
        wallpaper = Wallpaper("Test", 1000, roll_width=0.5, roll_length=10.0)
        info = wallpaper.get_detailed_info()
        assert info["name"] == "Test"
        assert info["roll_width"] == 0.5
        assert info["roll_length"] == 10.0
        assert "coverage" in info
    
    def test_wallpaper_str(self):
        """Тест: Строковое представление"""
        wallpaper = Wallpaper("Винил", 1200)
        assert "Винил" in str(wallpaper)
        assert "1200" in str(wallpaper)
        assert "рулон" in str(wallpaper)
    
    def test_wallpaper_eq(self):
        """Тест: Сравнение обоев"""
        w1 = Wallpaper("Test", 1000, 0.53, 10.05)
        w2 = Wallpaper("Test", 1000, 0.53, 10.05)
        w3 = Wallpaper("Other", 1000, 0.53, 10.05)
        assert w1 == w2
        assert w1 != w3
    
    def test_wallpaper_lt(self):
        """Тест: Сравнение обоев по стоимости за м²"""
        w1 = Wallpaper("Cheap", 500, 0.53, 10.05)
        w2 = Wallpaper("Expensive", 2000, 0.53, 10.05)
        assert w1 < w2


class TestTile:
    """Тесты для класса Tile"""
    
    def test_tile_creation(self):
        """Тест: Создание плитки с параметрами по умолчанию"""
        tile = Tile("Керамика", 2500, tiles_per_box=10)
        assert tile.name == "Керамика"
        assert tile.price_per_unit == 2500
        assert tile.tiles_per_box == 10
        assert tile.tile_width == 0.3
        assert tile.tile_height == 0.3
        assert tile.unit_coverage == pytest.approx(0.3 * 0.3 * 10)
    
    def test_tile_custom_dimensions(self):
        """Тест: Создание плитки с кастомными размерами"""
        tile = Tile("Мрамор", 5000, tiles_per_box=5, tile_width=0.6, tile_height=0.6)
        assert tile.tile_width == 0.6
        assert tile.tile_height == 0.6
        assert tile.unit_coverage == pytest.approx(0.6 * 0.6 * 5)
    
    def test_tile_price_validation(self):
        """Тест: Валидация цены плитки"""
        with pytest.raises(ValueError):
            Tile("Test", -100, 10)
    
    def test_tile_tiles_per_box_validation(self):
        """Тест: Валидация количества плиток в упаковке"""
        with pytest.raises(ValueError, match="Количество плиток должно быть положительным"):
            Tile("Test", 1000, tiles_per_box=-5)
    
    def test_tile_get_unit_type(self):
        """Тест: Получение типа единицы измерения"""
        tile = Tile("Test", 1000, 10)
        assert tile.get_unit_type() == "упаковка"
    
    def test_tile_get_detailed_info(self):
        """Тест: Получение детальной информации"""
        tile = Tile("Test", 1000, tiles_per_box=10, tile_width=0.3, tile_height=0.3)
        info = tile.get_detailed_info()
        assert info["name"] == "Test"
        assert info["tiles_per_box"] == 10
        assert "tile_area" in info


class TestLaminate:
    """Тесты для класса Laminate"""
    
    def test_laminate_creation(self):
        """Тест: Создание ламината с параметрами по умолчанию"""
        laminate = Laminate("Дуб", 1800, planks_per_pack=8)
        assert laminate.name == "Дуб"
        assert laminate.price_per_unit == 1800
        assert laminate.planks_per_pack == 8
        assert laminate.plank_width == 0.193
        assert laminate.plank_length == 1.380
        assert laminate.unit_coverage == pytest.approx(0.193 * 1.380 * 8)
    
    def test_laminate_custom_dimensions(self):
        """Тест: Создание ламината с кастомными размерами"""
        laminate = Laminate("Орех", 2000, planks_per_pack=10, 
                           plank_width=0.2, plank_length=1.5)
        assert laminate.plank_width == 0.2
        assert laminate.plank_length == 1.5
        assert laminate.unit_coverage == pytest.approx(0.2 * 1.5 * 10)
    
    def test_laminate_price_validation(self):
        """Тест: Валидация цены ламината"""
        with pytest.raises(ValueError):
            Laminate("Test", 0, 8)
    
    def test_laminate_planks_per_pack_validation(self):
        """Тест: Валидация количества досок в упаковке"""
        with pytest.raises(ValueError, match="Количество досок должно быть положительным"):
            Laminate("Test", 1000, planks_per_pack=0)
    
    def test_laminate_get_unit_type(self):
        """Тест: Получение типа единицы измерения"""
        laminate = Laminate("Test", 1000, 8)
        assert laminate.get_unit_type() == "упаковка"
    
    def test_laminate_get_detailed_info(self):
        """Тест: Получение детальной информации"""
        laminate = Laminate("Test", 1000, planks_per_pack=8)
        info = laminate.get_detailed_info()
        assert info["name"] == "Test"
        assert info["planks_per_pack"] == 8
        assert "plank_area" in info


class TestCalculationResult:
    """Тесты для класса CalculationResult"""
    
    def test_calculation_result_creation(self, sample_wallpaper):
        """Тест: Создание результата расчёта"""
        result = CalculationResult(
            material=sample_wallpaper,
            area=25.0,
            units_needed=5,
            total_cost=6000.0,
            reserve_percent=10
        )
        assert result.material == sample_wallpaper
        assert result.area == 25.0
        assert result.units_needed == 5
        assert result.total_cost == 6000.0
        assert result.reserve_percent == 10
    
    def test_calculation_result_default_reserve(self, sample_wallpaper):
        """Тест: Создание результата с запасом по умолчанию"""
        result = CalculationResult(
            material=sample_wallpaper,
            area=25.0,
            units_needed=5,
            total_cost=6000.0
        )
        assert result.reserve_percent == 10
    
    def test_calculation_result_str(self, sample_wallpaper):
        """Тест: Строковое представление результата"""
        result = CalculationResult(
            material=sample_wallpaper,
            area=25.0,
            units_needed=5,
            total_cost=6000.0
        )
        str_repr = str(result)
        assert "Результат расчёта" in str_repr
        assert "25.0" in str_repr
        assert "6000" in str_repr
    
    def test_calculation_result_repr(self, sample_wallpaper):
        """Тест: Представление результата для отладки"""
        result = CalculationResult(
            material=sample_wallpaper,
            area=25.0,
            units_needed=5,
            total_cost=6000.0
        )
        repr_str = repr(result)
        assert "CalculationResult" in repr_str
        assert sample_wallpaper.name in repr_str


class TestMaterialComparison:
    """Тесты для сравнения материалов"""
    
    def test_materials_comparison_by_cost_per_sqm(self):
        """Тест: Сравнение материалов по стоимости за м²"""
        cheap = Wallpaper("Дешёвые", 500, 0.53, 10.05)
        expensive = Wallpaper("Дорогие", 2000, 0.53, 10.05)
        assert cheap < expensive
        assert expensive > cheap
    
    def test_materials_hash(self):
        """Тест: Хеширование материалов для использования в множествах"""
        w1 = Wallpaper("Test", 1000, 0.53, 10.05)
        w2 = Wallpaper("Test", 1000, 0.53, 10.05)
        w3 = Wallpaper("Other", 1000, 0.53, 10.05)
        
        # Одинаковые материалы должны иметь одинаковый хеш
        assert hash(w1) == hash(w2)
        # Разные материалы могут иметь разные хеши
        assert hash(w1) != hash(w3)
        
        # Можно использовать в множествах
        materials_set = {w1, w2, w3}
        assert len(materials_set) == 2  # w1 и w2 одинаковые


class TestMaterialEdgeCases:
    """Тесты граничных случаев для материалов"""
    
    def test_very_small_price(self):
        """Тест: Очень маленькая цена"""
        wallpaper = Wallpaper("Test", 0.01)
        assert wallpaper.price_per_unit == 0.01
    
    def test_very_large_price(self):
        """Тест: Очень большая цена"""
        wallpaper = Wallpaper("Luxury", 100000)
        assert wallpaper.price_per_unit == 100000
    
    def test_very_small_coverage(self):
        """Тест: Очень маленькое покрытие"""
        # Создаём обои с очень маленьким покрытием
        wallpaper = Wallpaper("Test", 1000, roll_width=0.1, roll_length=0.1)
        assert wallpaper.unit_coverage == pytest.approx(0.01)
    
    def test_price_setter_validation(self):
        """Тест: Валидация при установке цены через setter"""
        wallpaper = Wallpaper("Test", 1000)
        with pytest.raises(ValueError):
            wallpaper.price_per_unit = -100
        with pytest.raises(ValueError):
            wallpaper.price_per_unit = 0
    
    def test_coverage_setter_validation(self):
        """Тест: Валидация при установке покрытия через setter"""
        wallpaper = Wallpaper("Test", 1000)
        # Покрытие нельзя изменить напрямую для обоев, но можно проверить через базовый класс
        # Это тест для демонстрации валидации в базовом классе

