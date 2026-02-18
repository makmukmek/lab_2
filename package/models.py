"""
Модуль models.py
Содержит классы для представления отделочных материалов
Уровень: MEDIUM (с ABC, managed-атрибутами, расширенными dunder-методами)
"""

from abc import ABC, abstractmethod


class Material(ABC):
    """Абстрактный базовый класс для отделочного материала"""
    
    def __init__(self, name, price_per_unit, unit_coverage):
        """
        Инициализация материала
        
        Args:
            name (str): Название материала
            price_per_unit (float): Цена за единицу (рулон/упаковку/м²)
            unit_coverage (float): Покрытие одной единицы в м²
        """
        self.name = name
        self._price_per_unit = None
        self._unit_coverage = None
        
        # Используем setter для валидации
        self.price_per_unit = price_per_unit
        self.unit_coverage = unit_coverage
    
    @property
    def price_per_unit(self):
        """Получить цену за единицу"""
        return self._price_per_unit
    
    @price_per_unit.setter
    def price_per_unit(self, value):
        """
        Установить цену за единицу с валидацией
        
        Args:
            value (float): Цена за единицу
        
        Raises:
            ValueError: Если цена отрицательная или нулевая
        """
        if value <= 0:
            raise ValueError(f"Цена должна быть положительным числом, получено: {value}")
        self._price_per_unit = float(value)
    
    @property
    def unit_coverage(self):
        """Получить покрытие одной единицы"""
        return self._unit_coverage
    
    @unit_coverage.setter
    def unit_coverage(self, value):
        """
        Установить покрытие с валидацией
        
        Args:
            value (float): Покрытие в м²
        
        Raises:
            ValueError: Если покрытие отрицательное или нулевое
        """
        if value <= 0:
            raise ValueError(f"Покрытие должно быть положительным числом, получено: {value}")
        self._unit_coverage = float(value)
    
    @abstractmethod
    def get_unit_type(self):
        """
        Получить тип единицы измерения материала
        
        Returns:
            str: Тип единицы (например, "рулон", "упаковка")
        """
        pass
    
    @abstractmethod
    def get_detailed_info(self):
        """
        Получить детальную информацию о материале
        
        Returns:
            dict: Словарь с детальной информацией
        """
        pass
    
    def calculate_cost_per_sqm(self):
        """
        Рассчитать стоимость за квадратный метр
        
        Returns:
            float: Стоимость за м²
        """
        return self._price_per_unit / self._unit_coverage
    
    def __str__(self):
        return f"{self.name} - {self.price_per_unit}₽ за {self.get_unit_type()} (покрытие: {self.unit_coverage:.2f}м²)"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', {self.price_per_unit}, {self.unit_coverage})"
    
    def __eq__(self, other):
        """Сравнение материалов по всем атрибутам"""
        if not isinstance(other, Material):
            return False
        return (self.name == other.name and 
                self.price_per_unit == other.price_per_unit and
                self.unit_coverage == other.unit_coverage)
    
    def __lt__(self, other):
        """Сравнение материалов по стоимости за м²"""
        if not isinstance(other, Material):
            return NotImplemented
        return self.calculate_cost_per_sqm() < other.calculate_cost_per_sqm()
    
    def __hash__(self):
        """Хеш для использования в множествах и словарях"""
        return hash((self.name, self._price_per_unit, self._unit_coverage))


class Wallpaper(Material):
    """Класс для обоев"""
    
    def __init__(self, name, price_per_roll, roll_width=0.53, roll_length=10.05):
        """
        Инициализация обоев
        
        Args:
            name (str): Название обоев
            price_per_roll (float): Цена за рулон
            roll_width (float): Ширина рулона в метрах (стандарт 0.53м)
            roll_length (float): Длина рулона в метрах (стандарт 10.05м)
        """
        self._roll_width = None
        self._roll_length = None
        
        # Устанавливаем размеры с валидацией
        self.roll_width = roll_width
        self.roll_length = roll_length
        
        coverage = self._roll_width * self._roll_length
        super().__init__(name, price_per_roll, coverage)
    
    @property
    def roll_width(self):
        """Получить ширину рулона"""
        return self._roll_width
    
    @roll_width.setter
    def roll_width(self, value):
        """Установить ширину рулона с валидацией"""
        if value <= 0:
            raise ValueError(f"Ширина рулона должна быть положительной, получено: {value}")
        if value > 5:  # Разумное ограничение
            raise ValueError(f"Ширина рулона не может быть больше 5м, получено: {value}")
        self._roll_width = float(value)
    
    @property
    def roll_length(self):
        """Получить длину рулона"""
        return self._roll_length
    
    @roll_length.setter
    def roll_length(self, value):
        """Установить длину рулона с валидацией"""
        if value <= 0:
            raise ValueError(f"Длина рулона должна быть положительной, получено: {value}")
        if value > 50:  # Разумное ограничение
            raise ValueError(f"Длина рулона не может быть больше 50м, получено: {value}")
        self._roll_length = float(value)
    
    def get_unit_type(self):
        """Тип единицы измерения"""
        return "рулон"
    
    def get_detailed_info(self):
        """Детальная информация об обоях"""
        return {
            'type': 'Обои',
            'name': self.name,
            'price': self.price_per_unit,
            'unit': self.get_unit_type(),
            'roll_width': self._roll_width,
            'roll_length': self._roll_length,
            'coverage': self.unit_coverage,
            'cost_per_sqm': self.calculate_cost_per_sqm()
        }
    
    def __str__(self):
        return f"Обои '{self.name}' - {self.price_per_unit}₽/рулон ({self._roll_width}×{self._roll_length}м)"
    
    def __repr__(self):
        return f"Wallpaper('{self.name}', {self.price_per_unit}, {self._roll_width}, {self._roll_length})"


class Tile(Material):
    """Класс для плитки"""
    
    def __init__(self, name, price_per_box, tiles_per_box, tile_width=0.3, tile_height=0.3):
        """
        Инициализация плитки
        
        Args:
            name (str): Название плитки
            price_per_box (float): Цена за упаковку
            tiles_per_box (int): Количество плиток в упаковке
            tile_width (float): Ширина плитки в метрах
            tile_height (float): Высота плитки в метрах
        """
        self._tiles_per_box = None
        self._tile_width = None
        self._tile_height = None
        
        # Устанавливаем параметры с валидацией
        self.tiles_per_box = tiles_per_box
        self.tile_width = tile_width
        self.tile_height = tile_height
        
        tile_area = self._tile_width * self._tile_height
        coverage = tile_area * self._tiles_per_box
        super().__init__(name, price_per_box, coverage)
    
    @property
    def tiles_per_box(self):
        """Получить количество плиток в упаковке"""
        return self._tiles_per_box
    
    @tiles_per_box.setter
    def tiles_per_box(self, value):
        """Установить количество плиток с валидацией"""
        if value <= 0:
            raise ValueError(f"Количество плиток должно быть положительным, получено: {value}")
        if value > 1000:  # Разумное ограничение
            raise ValueError(f"Количество плиток не может быть больше 1000, получено: {value}")
        self._tiles_per_box = int(value)
    
    @property
    def tile_width(self):
        """Получить ширину плитки"""
        return self._tile_width
    
    @tile_width.setter
    def tile_width(self, value):
        """Установить ширину плитки с валидацией"""
        if value <= 0:
            raise ValueError(f"Ширина плитки должна быть положительной, получено: {value}")
        if value > 2:  # Разумное ограничение
            raise ValueError(f"Ширина плитки не может быть больше 2м, получено: {value}")
        self._tile_width = float(value)
    
    @property
    def tile_height(self):
        """Получить высоту плитки"""
        return self._tile_height
    
    @tile_height.setter
    def tile_height(self, value):
        """Установить высоту плитки с валидацией"""
        if value <= 0:
            raise ValueError(f"Высота плитки должна быть положительной, получено: {value}")
        if value > 2:  # Разумное ограничение
            raise ValueError(f"Высота плитки не может быть больше 2м, получено: {value}")
        self._tile_height = float(value)
    
    def get_unit_type(self):
        """Тип единицы измерения"""
        return "упаковка"
    
    def get_detailed_info(self):
        """Детальная информация о плитке"""
        return {
            'type': 'Плитка',
            'name': self.name,
            'price': self.price_per_unit,
            'unit': self.get_unit_type(),
            'tiles_per_box': self._tiles_per_box,
            'tile_width': self._tile_width,
            'tile_height': self._tile_height,
            'tile_area': self._tile_width * self._tile_height,
            'coverage': self.unit_coverage,
            'cost_per_sqm': self.calculate_cost_per_sqm()
        }
    
    def __str__(self):
        return f"Плитка '{self.name}' - {self.price_per_unit}₽/упаковка ({self._tiles_per_box}шт, {self._tile_width}×{self._tile_height}м)"
    
    def __repr__(self):
        return f"Tile('{self.name}', {self.price_per_unit}, {self._tiles_per_box}, {self._tile_width}, {self._tile_height})"


class Laminate(Material):
    """Класс для ламината"""
    
    def __init__(self, name, price_per_pack, planks_per_pack, plank_width=0.193, plank_length=1.380):
        """
        Инициализация ламината
        
        Args:
            name (str): Название ламината
            price_per_pack (float): Цена за упаковку
            planks_per_pack (int): Количество досок в упаковке
            plank_width (float): Ширина доски в метрах
            plank_length (float): Длина доски в метрах
        """
        self._planks_per_pack = None
        self._plank_width = None
        self._plank_length = None
        
        # Устанавливаем параметры с валидацией
        self.planks_per_pack = planks_per_pack
        self.plank_width = plank_width
        self.plank_length = plank_length
        
        plank_area = self._plank_width * self._plank_length
        coverage = plank_area * self._planks_per_pack
        super().__init__(name, price_per_pack, coverage)
    
    @property
    def planks_per_pack(self):
        """Получить количество досок в упаковке"""
        return self._planks_per_pack
    
    @planks_per_pack.setter
    def planks_per_pack(self, value):
        """Установить количество досок с валидацией"""
        if value <= 0:
            raise ValueError(f"Количество досок должно быть положительным, получено: {value}")
        if value > 100:  # Разумное ограничение
            raise ValueError(f"Количество досок не может быть больше 100, получено: {value}")
        self._planks_per_pack = int(value)
    
    @property
    def plank_width(self):
        """Получить ширину доски"""
        return self._plank_width
    
    @plank_width.setter
    def plank_width(self, value):
        """Установить ширину доски с валидацией"""
        if value <= 0:
            raise ValueError(f"Ширина доски должна быть положительной, получено: {value}")
        if value > 1:  # Разумное ограничение
            raise ValueError(f"Ширина доски не может быть больше 1м, получено: {value}")
        self._plank_width = float(value)
    
    @property
    def plank_length(self):
        """Получить длину доски"""
        return self._plank_length
    
    @plank_length.setter
    def plank_length(self, value):
        """Установить длину доски с валидацией"""
        if value <= 0:
            raise ValueError(f"Длина доски должна быть положительной, получено: {value}")
        if value > 3:  # Разумное ограничение
            raise ValueError(f"Длина доски не может быть больше 3м, получено: {value}")
        self._plank_length = float(value)
    
    def get_unit_type(self):
        """Тип единицы измерения"""
        return "упаковка"
    
    def get_detailed_info(self):
        """Детальная информация о ламинате"""
        return {
            'type': 'Ламинат',
            'name': self.name,
            'price': self.price_per_unit,
            'unit': self.get_unit_type(),
            'planks_per_pack': self._planks_per_pack,
            'plank_width': self._plank_width,
            'plank_length': self._plank_length,
            'plank_area': self._plank_width * self._plank_length,
            'coverage': self.unit_coverage,
            'cost_per_sqm': self.calculate_cost_per_sqm()
        }
    
    def __str__(self):
        return f"Ламинат '{self.name}' - {self.price_per_unit}₽/упаковка ({self._planks_per_pack}шт, {self._plank_width}×{self._plank_length}м)"
    
    def __repr__(self):
        return f"Laminate('{self.name}', {self.price_per_unit}, {self._planks_per_pack}, {self._plank_width}, {self._plank_length})"


class CalculationResult:
    """Класс для хранения результатов расчёта"""
    
    def __init__(self, material, area, units_needed, total_cost, reserve_percent=10):
        """
        Инициализация результата расчёта
        
        Args:
            material (Material): Материал
            area (float): Площадь для покрытия (м²)
            units_needed (int): Необходимое количество единиц
            total_cost (float): Общая стоимость
            reserve_percent (float): Процент запаса
        """
        self.material = material
        self._area = None
        self._units_needed = None
        self._total_cost = None
        self._reserve_percent = None
        
        # Используем setter для валидации
        self.area = area
        self.units_needed = units_needed
        self.total_cost = total_cost
        self.reserve_percent = reserve_percent
    
    @property
    def area(self):
        """Получить площадь"""
        return self._area
    
    @area.setter
    def area(self, value):
        """Установить площадь с валидацией"""
        if value <= 0:
            raise ValueError(f"Площадь должна быть положительной, получено: {value}")
        self._area = float(value)
    
    @property
    def units_needed(self):
        """Получить количество единиц"""
        return self._units_needed
    
    @units_needed.setter
    def units_needed(self, value):
        """Установить количество единиц с валидацией"""
        if value <= 0:
            raise ValueError(f"Количество единиц должно быть положительным, получено: {value}")
        self._units_needed = int(value)
    
    @property
    def total_cost(self):
        """Получить общую стоимость"""
        return self._total_cost
    
    @total_cost.setter
    def total_cost(self, value):
        """Установить стоимость с валидацией"""
        if value < 0:
            raise ValueError(f"Стоимость не может быть отрицательной, получено: {value}")
        self._total_cost = float(value)
    
    @property
    def reserve_percent(self):
        """Получить процент запаса"""
        return self._reserve_percent
    
    @reserve_percent.setter
    def reserve_percent(self, value):
        """Установить процент запаса с валидацией"""
        if value < 0 or value > 100:
            raise ValueError(f"Процент запаса должен быть от 0 до 100, получено: {value}")
        self._reserve_percent = float(value)
    
    def __str__(self):
        return (f"Результат расчёта:\n"
                f"Материал: {self.material.name}\n"
                f"Площадь: {self._area}м²\n"
                f"Необходимо единиц: {self._units_needed}\n"
                f"Общая стоимость: {self._total_cost:.2f}₽\n"
                f"Запас: {self._reserve_percent}%")
    
    def __repr__(self):
        return f"CalculationResult({self.material.name}, {self._area}, {self._units_needed}, {self._total_cost})"
    
    def __eq__(self, other):
        """Сравнение результатов"""
        if not isinstance(other, CalculationResult):
            return False
        return (self.material == other.material and 
                self._area == other._area and
                self._units_needed == other._units_needed)
    
    def __lt__(self, other):
        """Сравнение результатов по стоимости"""
        if not isinstance(other, CalculationResult):
            return NotImplemented
        return self._total_cost < other._total_cost