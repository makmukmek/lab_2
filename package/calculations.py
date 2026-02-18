"""
Модуль calculations.py
Содержит логику расчёта количества и стоимости отделочных материалов
"""

import math
from .models import Material, CalculationResult
from .database import DatabaseManager


class MaterialCalculator:
    """Класс для расчёта количества и стоимости материалов"""
    
    def __init__(self, reserve_percent=10, min_area=0.1, max_area=10000, 
                 precision=2, currency="₽", auto_save=True, db_manager=None):
        """
        Инициализация калькулятора
        
        Args:
            reserve_percent (float): Процент запаса материала (по умолчанию 10%)
            min_area (float): Минимальная площадь для расчёта в м² (по умолчанию 0.1)
            max_area (float): Максимальная площадь для расчёта в м² (по умолчанию 10000)
            precision (int): Точность округления стоимости (по умолчанию 2)
            currency (str): Валюта для отображения (по умолчанию "₽")
            auto_save (bool): Автоматически сохранять расчёты в историю (по умолчанию True)
            db_manager (DatabaseManager): Менеджер БД для сохранения результатов (опционально)
        """
        self._reserve_percent = reserve_percent
        self._min_area = min_area
        self._max_area = max_area
        self._precision = precision
        self._currency = currency
        self._auto_save = auto_save
        self._calculations_history = []
        self._db_manager = db_manager
    
    @property
    def reserve_percent(self):
        """Получить процент запаса"""
        return self._reserve_percent
    
    @reserve_percent.setter
    def reserve_percent(self, value):
        """
        Установить процент запаса
        
        Args:
            value (float): Новый процент запаса
        
        Raises:
            ValueError: Если процент отрицательный или больше 100
        """
        if value < 0 or value > 100:
            raise ValueError("Процент запаса должен быть от 0 до 100")
        self._reserve_percent = value
    
    @property
    def min_area(self):
        """Получить минимальную площадь для расчёта"""
        return self._min_area
    
    @min_area.setter
    def min_area(self, value):
        """
        Установить минимальную площадь для расчёта
        
        Args:
            value (float): Минимальная площадь в м²
        
        Raises:
            ValueError: Если значение отрицательное или больше max_area
        """
        if value < 0:
            raise ValueError("Минимальная площадь не может быть отрицательной")
        if value > self._max_area:
            raise ValueError("Минимальная площадь не может быть больше максимальной")
        self._min_area = value
    
    @property
    def max_area(self):
        """Получить максимальную площадь для расчёта"""
        return self._max_area
    
    @max_area.setter
    def max_area(self, value):
        """
        Установить максимальную площадь для расчёта
        
        Args:
            value (float): Максимальная площадь в м²
        
        Raises:
            ValueError: Если значение меньше min_area
        """
        if value < self._min_area:
            raise ValueError("Максимальная площадь не может быть меньше минимальной")
        self._max_area = value
    
    @property
    def precision(self):
        """Получить точность округления стоимости"""
        return self._precision
    
    @precision.setter
    def precision(self, value):
        """
        Установить точность округления стоимости
        
        Args:
            value (int): Количество знаков после запятой (0-10)
        
        Raises:
            ValueError: Если значение вне допустимого диапазона
        """
        if not isinstance(value, int) or value < 0 or value > 10:
            raise ValueError("Точность должна быть целым числом от 0 до 10")
        self._precision = value
    
    @property
    def currency(self):
        """Получить валюту для отображения"""
        return self._currency
    
    @currency.setter
    def currency(self, value):
        """
        Установить валюту для отображения
        
        Args:
            value (str): Символ валюты
        
        Raises:
            ValueError: Если значение не является строкой
        """
        if not isinstance(value, str):
            raise ValueError("Валюта должна быть строкой")
        self._currency = value
    
    @property
    def auto_save(self):
        """Получить статус автоматического сохранения"""
        return self._auto_save
    
    @auto_save.setter
    def auto_save(self, value):
        """
        Установить статус автоматического сохранения
        
        Args:
            value (bool): Включить/выключить автосохранение
        """
        if not isinstance(value, bool):
            raise ValueError("auto_save должен быть булевым значением")
        self._auto_save = value
    
    @property
    def history_count(self):
        """Получить количество расчётов в истории"""
        return len(self._calculations_history)
    
    @property
    def total_cost_sum(self):
        """Получить сумму всех расчётов"""
        return sum(result.total_cost for result in self._calculations_history)
    
    def calculate(self, material, area):
        """
        Рассчитать количество материала и стоимость
        
        Args:
            material (Material): Объект материала
            area (float): Площадь для покрытия в м²
        
        Returns:
            CalculationResult: Результат расчёта
        
        Raises:
            ValueError: Если площадь вне допустимого диапазона или материал некорректен
        """
        if area < self._min_area:
            raise ValueError(f"Площадь должна быть не менее {self._min_area} м²")
        if area > self._max_area:
            raise ValueError(f"Площадь не должна превышать {self._max_area} м²")
        
        if not isinstance(material, Material):
            raise ValueError("Параметр material должен быть экземпляром класса Material")
        
        # Учитываем запас
        area_with_reserve = area * (1 + self._reserve_percent / 100)
        
        # Рассчитываем количество единиц (округляем вверх)
        units_needed = math.ceil(area_with_reserve / material.unit_coverage)
        
        # Рассчитываем общую стоимость с округлением
        total_cost = round(units_needed * material.price_per_unit, self._precision)
        
        # Создаём результат
        result = CalculationResult(
            material=material,
            area=area,
            units_needed=units_needed,
            total_cost=total_cost,
            reserve_percent=self._reserve_percent
        )
        
        # Сохраняем в историю, если включено автосохранение
        if self._auto_save:
            self._calculations_history.append(result)
            # Сохраняем в БД, если менеджер БД настроен
            if self._db_manager:
                try:
                    self._db_manager.save_calculation(result, calculation_type='simple')
                except Exception as e:
                    # Не прерываем выполнение, только логируем ошибку
                    print(f"⚠️  Предупреждение: не удалось сохранить в БД: {e}")
        
        return result
    
    def get_history(self):
        """
        Получить историю всех расчётов
        
        Returns:
            list: Список объектов CalculationResult
        """
        return self._calculations_history.copy()
    
    def clear_history(self):
        """Очистить историю расчётов"""
        self._calculations_history.clear()
    
    def compare_materials(self, materials, area):
        """
        Сравнить несколько материалов для одной площади
        
        Args:
            materials (list): Список объектов Material
            area (float): Площадь для покрытия
        
        Returns:
            list: Список результатов расчётов, отсортированных по стоимости
        """
        if not materials:
            raise ValueError("Список материалов не может быть пустым")
        
        results = []
        for material in materials:
            result = self.calculate(material, area)
            results.append(result)
        
        # Сортируем по стоимости (от меньшей к большей)
        results.sort(key=lambda r: r.total_cost)
        
        return results
    
    def __len__(self):
        """
        Возвращает количество расчётов в истории
        
        Returns:
            int: Количество расчётов
        """
        return len(self._calculations_history)
    
    def __getitem__(self, index):
        """
        Доступ к расчётам по индексу или срезу
        
        Args:
            index (int | slice): Индекс или срез
        
        Returns:
            CalculationResult | list: Результат расчёта или список результатов
        
        Raises:
            IndexError: Если индекс вне диапазона
        """
        return self._calculations_history[index]
    
    def __contains__(self, item):
        """
        Проверка наличия расчёта в истории
        
        Args:
            item: Объект CalculationResult для проверки
        
        Returns:
            bool: True если расчёт найден в истории
        """
        return item in self._calculations_history
    
    def __iter__(self):
        """
        Итератор по истории расчётов
        
        Returns:
            iterator: Итератор по расчётам
        """
        return iter(self._calculations_history)
    
    def __bool__(self):
        """
        Проверка наличия расчётов в истории
        
        Returns:
            bool: True если есть расчёты в истории
        """
        return len(self._calculations_history) > 0
    
    def __eq__(self, other):
        """
        Сравнение калькуляторов
        
        Args:
            other: Другой объект MaterialCalculator
        
        Returns:
            bool: True если калькуляторы эквивалентны
        """
        if not isinstance(other, MaterialCalculator):
            return False
        return (self._reserve_percent == other._reserve_percent and
                self._min_area == other._min_area and
                self._max_area == other._max_area and
                self._precision == other._precision and
                self._currency == other._currency and
                self._auto_save == other._auto_save)
    
    def __str__(self):
        return (f"MaterialCalculator(запас: {self._reserve_percent}%, "
                f"расчётов: {len(self._calculations_history)}, "
                f"площадь: {self._min_area}-{self._max_area}м²)")
    
    def __repr__(self):
        return (f"MaterialCalculator(reserve_percent={self._reserve_percent}, "
                f"min_area={self._min_area}, max_area={self._max_area}, "
                f"precision={self._precision}, currency='{self._currency}', "
                f"auto_save={self._auto_save})")


class RoomCalculator:
    """Класс для расчёта материалов для комнат со сложной геометрией"""
    
    def __init__(self):
        """Инициализация калькулятора комнат"""
        self._material_calculator = MaterialCalculator()
    
    @property
    def reserve_percent(self):
        """Получить процент запаса"""
        return self._material_calculator.reserve_percent
    
    @reserve_percent.setter
    def reserve_percent(self, value):
        """Установить процент запаса"""
        self._material_calculator.reserve_percent = value
    
    def calculate_floor_area(self, length, width):
        """
        Рассчитать площадь пола
        
        Args:
            length (float): Длина комнаты в метрах
            width (float): Ширина комнаты в метрах
        
        Returns:
            float: Площадь в м²
        """
        if length <= 0 or width <= 0:
            raise ValueError("Длина и ширина должны быть положительными")
        return length * width
    
    def calculate_wall_area(self, perimeter, height, door_area=0, window_area=0):
        """
        Рассчитать площадь стен с вычетом дверей и окон
        
        Args:
            perimeter (float): Периметр комнаты в метрах
            height (float): Высота потолка в метрах
            door_area (float): Площадь дверей в м²
            window_area (float): Площадь окон в м²
        
        Returns:
            float: Площадь стен в м²
        """
        if perimeter <= 0 or height <= 0:
            raise ValueError("Периметр и высота должны быть положительными")
        if door_area < 0 or window_area < 0:
            raise ValueError("Площади дверей и окон не могут быть отрицательными")
        
        total_wall_area = perimeter * height
        result_area = total_wall_area - door_area - window_area
        
        if result_area <= 0:
            raise ValueError("Площадь стен после вычета дверей и окон должна быть положительной")
        
        return result_area
    
    def calculate_materials_for_room(self, material, length, width, height=None, 
                                     door_area=0, window_area=0, surface_type='floor'):
        """
        Рассчитать материалы для комнаты
        
        Args:
            material (Material): Материал
            length (float): Длина комнаты
            width (float): Ширина комнаты
            height (float): Высота потолка (для стен)
            door_area (float): Площадь дверей
            window_area (float): Площадь окон
            surface_type (str): Тип поверхности ('floor' или 'wall')
        
        Returns:
            CalculationResult: Результат расчёта
        """
        if surface_type == 'floor':
            area = self.calculate_floor_area(length, width)
        elif surface_type == 'wall':
            if height is None:
                raise ValueError("Для расчёта стен необходимо указать высоту")
            perimeter = 2 * (length + width)
            area = self.calculate_wall_area(perimeter, height, door_area, window_area)
        else:
            raise ValueError("surface_type должен быть 'floor' или 'wall'")
        
        return self._material_calculator.calculate(material, area)
    
    def __str__(self):
        return f"RoomCalculator(запас: {self.reserve_percent}%)"
    
    def __repr__(self):
        return f"RoomCalculator()"


def validate_positive_number(value, name="Значение"):
    """
    Валидация положительного числа
    
    Args:
        value: Проверяемое значение
        name (str): Название параметра для сообщения об ошибке
    
    Returns:
        float: Валидированное значение
    
    Raises:
        ValueError: Если значение не является положительным числом
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} должно быть числом")
    
    if num <= 0:
        raise ValueError(f"{name} должно быть положительным числом")
    
    return num