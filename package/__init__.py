"""
Пакет для расчёта количества и стоимости отделочных материалов

Модули:
    - models: Классы для представления отделочных материалов
    - calculations: Логика расчётов количества и стоимости
    - exporters: Экспорт результатов в форматы .doc и .xls

Основные классы:
    Материалы:
        - Material: Базовый класс материала
        - Wallpaper: Обои
        - Tile: Плитка
        - Laminate: Ламинат
    
    Расчёты:
        - MaterialCalculator: Калькулятор материалов
        - RoomCalculator: Калькулятор для комнат
        - CalculationResult: Результат расчёта
    
    Экспорт:
        - DocxExporter: Экспорт в .docx
        - ExcelExporter: Экспорт в .xlsx

Пример использования:
    >>> from materials_package import Wallpaper, MaterialCalculator, DocxExporter
    >>> wallpaper = Wallpaper("Винил Premium", 1200)
    >>> calculator = MaterialCalculator(reserve_percent=10)
    >>> result = calculator.calculate(wallpaper, area=25)
    >>> exporter = DocxExporter("отчёт.docx")
    >>> exporter.export(result)

Версия: Rare
Автор: Mattt147
"""

__version__ = "Rare"
__author__ = "Mattt147"

# Импорт классов из модулей для удобного доступа
from .models import (
    Material,
    Wallpaper,
    Tile,
    Laminate,
    CalculationResult
)

from .calculations import (
    MaterialCalculator,
    RoomCalculator,
    validate_positive_number
)

from .exporters import (
    BaseExporter,
    DocxExporter,
    ExcelExporter
)

from .database import (
    DatabaseManager
)

# Определяем, что будет доступно при импорте через "from package import *"
__all__ = [
    # Модели
    'Material',
    'Wallpaper',
    'Tile',
    'Laminate',
    'CalculationResult',
    
    # Калькуляторы
    'MaterialCalculator',
    'RoomCalculator',
    'validate_positive_number',
    
    # Экспортеры
    'BaseExporter',
    'DocxExporter',
    'ExcelExporter',
    
    # База данных
    'DatabaseManager',
    
    # Метаданные
    '__version__',
    '__author__'
]


def get_version():
    """
    Получить версию пакета
    
    Returns:
        str: Версия пакета
    """
    return __version__


def get_available_materials():
    """
    Получить список доступных типов материалов
    
    Returns:
        list: Список названий классов материалов
    """
    return ['Wallpaper', 'Tile', 'Laminate']


def create_material(material_type, *args, **kwargs):
    """
    Фабричная функция для создания материалов
    
    Args:
        material_type (str): Тип материала ('wallpaper', 'tile', 'laminate')
        *args: Позиционные аргументы для конструктора
        **kwargs: Именованные аргументы для конструктора
    
    Returns:
        Material: Экземпляр соответствующего класса материала
    
    Raises:
        ValueError: Если тип материала неизвестен
    
    Example:
        >>> material = create_material('wallpaper', 'Винил', 1200)
        >>> material = create_material('tile', 'Керамика', 2500, 10, tile_width=0.3, tile_height=0.6)
    """
    material_type = material_type.lower()
    
    if material_type == 'wallpaper':
        return Wallpaper(*args, **kwargs)
    elif material_type == 'tile':
        return Tile(*args, **kwargs)
    elif material_type == 'laminate':
        return Laminate(*args, **kwargs)
    else:
        raise ValueError(f"Неизвестный тип материала: {material_type}. "
                        f"Доступные типы: {', '.join(get_available_materials())}")