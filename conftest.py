"""
Фикстуры pytest для тестирования модулей проекта
"""

import pytest
from package.models import Wallpaper, Tile, Laminate, CalculationResult
from package.calculations import MaterialCalculator, RoomCalculator
from package.exporters import DocxExporter, ExcelExporter


@pytest.fixture
def sample_wallpaper():
    """Фикстура для создания тестовых обоев"""
    return Wallpaper("Винил Premium", 1200, roll_width=0.53, roll_length=10.05)


@pytest.fixture
def sample_tile():
    """Фикстура для создания тестовой плитки"""
    return Tile("Керамика Classic", 2500, tiles_per_box=10, tile_width=0.3, tile_height=0.3)


@pytest.fixture
def sample_laminate():
    """Фикстура для создания тестового ламината"""
    return Laminate("Дуб Натуральный", 1800, planks_per_pack=8, plank_width=0.193, plank_length=1.380)


@pytest.fixture
def sample_materials(sample_wallpaper, sample_tile, sample_laminate):
    """Фикстура для списка материалов"""
    return [sample_wallpaper, sample_tile, sample_laminate]


@pytest.fixture
def calculator():
    """Фикстура для создания калькулятора с настройками по умолчанию"""
    return MaterialCalculator(reserve_percent=10, min_area=0.1, max_area=10000)


@pytest.fixture
def calculator_no_auto_save():
    """Фикстура для калькулятора с отключённым автосохранением"""
    return MaterialCalculator(auto_save=False)


@pytest.fixture
def room_calculator():
    """Фикстура для создания калькулятора комнат"""
    return RoomCalculator()


@pytest.fixture
def calculation_result(sample_wallpaper):
    """Фикстура для создания результата расчёта"""
    return CalculationResult(
        material=sample_wallpaper,
        area=25.0,
        units_needed=5,
        total_cost=6000.0,
        reserve_percent=10
    )


@pytest.fixture
def docx_exporter(tmp_path):
    """Фикстура для создания DOCX экспортера с временным файлом"""
    filename = tmp_path / "test_report.docx"
    return DocxExporter(str(filename))


@pytest.fixture
def excel_exporter(tmp_path):
    """Фикстура для создания Excel экспортера с временным файлом"""
    filename = tmp_path / "test_report.xlsx"
    return ExcelExporter(str(filename))


@pytest.fixture
def sample_results(sample_wallpaper, sample_tile, sample_laminate, calculator):
    """Фикстура для создания списка результатов расчётов"""
    results = []
    area = 20.0
    for material in [sample_wallpaper, sample_tile, sample_laminate]:
        result = calculator.calculate(material, area)
        results.append(result)
    return results

