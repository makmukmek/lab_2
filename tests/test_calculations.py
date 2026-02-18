"""
Тесты для модуля calculations.py
Проверка калькуляторов материалов и комнат
"""

import pytest
from package.calculations import MaterialCalculator, RoomCalculator, validate_positive_number
from package.models import Wallpaper, Tile, Laminate


class TestMaterialCalculator:
    """Тесты для класса MaterialCalculator"""
    
    def test_calculator_creation_default(self):
        """Тест: Создание калькулятора с параметрами по умолчанию"""
        calc = MaterialCalculator()
        assert calc.reserve_percent == 10
        assert calc.min_area == 0.1
        assert calc.max_area == 10000
        assert calc.precision == 2
        assert calc.currency == "₽"
        assert calc.auto_save is True
    
    def test_calculator_creation_custom(self):
        """Тест: Создание калькулятора с кастомными параметрами"""
        calc = MaterialCalculator(
            reserve_percent=15,
            min_area=1.0,
            max_area=5000,
            precision=3,
            currency="$",
            auto_save=False
        )
        assert calc.reserve_percent == 15
        assert calc.min_area == 1.0
        assert calc.max_area == 5000
        assert calc.precision == 3
        assert calc.currency == "$"
        assert calc.auto_save is False
    
    def test_calculate_basic(self, calculator, sample_wallpaper):
        """Тест: Базовый расчёт материала"""
        result = calculator.calculate(sample_wallpaper, 25.0)
        assert result.material == sample_wallpaper
        assert result.area == 25.0
        assert result.units_needed > 0
        assert result.total_cost > 0
        assert result.reserve_percent == 10
    
    def test_calculate_with_reserve(self, sample_wallpaper):
        """Тест: Расчёт с учётом запаса"""
        calc = MaterialCalculator(reserve_percent=20)
        result = calc.calculate(sample_wallpaper, 20.0)
        # С запасом 20% площадь должна быть больше
        assert result.area == 20.0  # Исходная площадь
        # Количество единиц должно учитывать запас
        assert result.units_needed >= 1
    
    def test_calculate_area_validation_min(self, calculator, sample_wallpaper):
        """Тест: Валидация минимальной площади"""
        with pytest.raises(ValueError, match="не менее"):
            calculator.calculate(sample_wallpaper, 0.05)  # Меньше min_area
    
    def test_calculate_area_validation_max(self, calculator, sample_wallpaper):
        """Тест: Валидация максимальной площади"""
        with pytest.raises(ValueError, match="не должна превышать"):
            calculator.calculate(sample_wallpaper, 20000)  # Больше max_area
    
    def test_calculate_material_validation(self, calculator):
        """Тест: Валидация типа материала"""
        with pytest.raises(ValueError, match="должен быть экземпляром класса Material"):
            calculator.calculate("not a material", 25.0)
    
    def test_reserve_percent_validation_negative(self, calculator):
        """Тест: Валидация отрицательного процента запаса"""
        with pytest.raises(ValueError, match="от 0 до 100"):
            calculator.reserve_percent = -5
    
    def test_reserve_percent_validation_over_100(self, calculator):
        """Тест: Валидация процента запаса больше 100"""
        with pytest.raises(ValueError, match="от 0 до 100"):
            calculator.reserve_percent = 150
    
    def test_reserve_percent_boundary_values(self, calculator):
        """Тест: Граничные значения процента запаса"""
        calculator.reserve_percent = 0
        assert calculator.reserve_percent == 0
        calculator.reserve_percent = 100
        assert calculator.reserve_percent == 100
    
    def test_min_area_validation_negative(self, calculator):
        """Тест: Валидация отрицательной минимальной площади"""
        with pytest.raises(ValueError, match="не может быть отрицательной"):
            calculator.min_area = -1
    
    def test_min_area_validation_greater_than_max(self, calculator):
        """Тест: Валидация min_area больше max_area"""
        with pytest.raises(ValueError, match="не может быть больше максимальной"):
            calculator.min_area = 20000
    
    def test_max_area_validation_less_than_min(self, calculator):
        """Тест: Валидация max_area меньше min_area"""
        calculator.min_area = 100
        with pytest.raises(ValueError, match="не может быть меньше минимальной"):
            calculator.max_area = 50
    
    def test_precision_validation_negative(self, calculator):
        """Тест: Валидация отрицательной точности"""
        with pytest.raises(ValueError, match="от 0 до 10"):
            calculator.precision = -1
    
    def test_precision_validation_over_10(self, calculator):
        """Тест: Валидация точности больше 10"""
        with pytest.raises(ValueError, match="от 0 до 10"):
            calculator.precision = 11
    
    def test_precision_validation_not_int(self, calculator):
        """Тест: Валидация типа точности"""
        with pytest.raises(ValueError):
            calculator.precision = 2.5
    
    def test_precision_rounding(self, sample_wallpaper):
        """Тест: Округление стоимости с учётом precision"""
        calc = MaterialCalculator(precision=0)
        result = calc.calculate(sample_wallpaper, 10.0)
        # Проверяем, что стоимость округлена до целого
        assert result.total_cost == int(result.total_cost)
    
    def test_currency_validation(self, calculator):
        """Тест: Валидация валюты"""
        calculator.currency = "$"
        assert calculator.currency == "$"
        calculator.currency = "€"
        assert calculator.currency == "€"
        with pytest.raises(ValueError, match="должна быть строкой"):
            calculator.currency = 123
    
    def test_auto_save_validation(self, calculator):
        """Тест: Валидация auto_save"""
        calculator.auto_save = False
        assert calculator.auto_save is False
        with pytest.raises(ValueError, match="булевым значением"):
            calculator.auto_save = "yes"
    
    def test_auto_save_disabled(self, calculator_no_auto_save, sample_wallpaper):
        """Тест: Расчёт без автосохранения"""
        assert len(calculator_no_auto_save) == 0
        result = calculator_no_auto_save.calculate(sample_wallpaper, 25.0)
        # Результат должен быть создан, но не сохранён в историю
        assert len(calculator_no_auto_save) == 0
    
    def test_get_history(self, calculator, sample_wallpaper):
        """Тест: Получение истории расчётов"""
        assert len(calculator.get_history()) == 0
        calculator.calculate(sample_wallpaper, 25.0)
        history = calculator.get_history()
        assert len(history) == 1
        assert history[0].area == 25.0
    
    def test_clear_history(self, calculator, sample_wallpaper):
        """Тест: Очистка истории расчётов"""
        calculator.calculate(sample_wallpaper, 25.0)
        assert len(calculator) > 0
        calculator.clear_history()
        assert len(calculator) == 0
    
    def test_compare_materials(self, calculator, sample_materials):
        """Тест: Сравнение нескольких материалов"""
        area = 20.0
        results = calculator.compare_materials(sample_materials, area)
        assert len(results) == 3
        # Результаты должны быть отсортированы по стоимости
        for i in range(len(results) - 1):
            assert results[i].total_cost <= results[i + 1].total_cost
    
    def test_compare_materials_empty_list(self, calculator):
        """Тест: Сравнение с пустым списком материалов"""
        with pytest.raises(ValueError, match="не может быть пустым"):
            calculator.compare_materials([], 25.0)
    
    def test_history_count_property(self, calculator, sample_wallpaper):
        """Тест: Свойство history_count"""
        assert calculator.history_count == 0
        calculator.calculate(sample_wallpaper, 25.0)
        assert calculator.history_count == 1
        calculator.calculate(sample_wallpaper, 30.0)
        assert calculator.history_count == 2
    
    def test_total_cost_sum_property(self, calculator, sample_wallpaper):
        """Тест: Свойство total_cost_sum"""
        assert calculator.total_cost_sum == 0
        result1 = calculator.calculate(sample_wallpaper, 25.0)
        result2 = calculator.calculate(sample_wallpaper, 30.0)
        expected_sum = result1.total_cost + result2.total_cost
        assert calculator.total_cost_sum == pytest.approx(expected_sum)


class TestMaterialCalculatorDunderMethods:
    """Тесты для dunder-методов MaterialCalculator"""
    
    def test_len(self, calculator, sample_wallpaper):
        """Тест: __len__ возвращает количество расчётов"""
        assert len(calculator) == 0
        calculator.calculate(sample_wallpaper, 25.0)
        assert len(calculator) == 1
        calculator.calculate(sample_wallpaper, 30.0)
        assert len(calculator) == 2
    
    def test_getitem_index(self, calculator, sample_wallpaper):
        """Тест: __getitem__ с индексом"""
        result1 = calculator.calculate(sample_wallpaper, 25.0)
        result2 = calculator.calculate(sample_wallpaper, 30.0)
        assert calculator[0] == result1
        assert calculator[1] == result2
    
    def test_getitem_slice(self, calculator, sample_wallpaper):
        """Тест: __getitem__ со срезом"""
        calculator.calculate(sample_wallpaper, 25.0)
        calculator.calculate(sample_wallpaper, 30.0)
        calculator.calculate(sample_wallpaper, 35.0)
        slice_result = calculator[0:2]
        assert len(slice_result) == 2
    
    def test_getitem_index_error(self, calculator):
        """Тест: __getitem__ с неверным индексом"""
        with pytest.raises(IndexError):
            _ = calculator[0]
    
    def test_contains(self, calculator, sample_wallpaper):
        """Тест: __contains__ проверка наличия расчёта"""
        result = calculator.calculate(sample_wallpaper, 25.0)
        assert result in calculator
        # Создаём новый результат с теми же параметрами, но он не будет в истории
        new_result = calculator.calculate(sample_wallpaper, 30.0)
        assert new_result in calculator
        assert result in calculator  # Старый результат тоже должен быть
    
    def test_iter(self, calculator, sample_wallpaper):
        """Тест: __iter__ итерация по истории"""
        calculator.calculate(sample_wallpaper, 25.0)
        calculator.calculate(sample_wallpaper, 30.0)
        results = list(calculator)
        assert len(results) == 2
    
    def test_bool(self, calculator, sample_wallpaper):
        """Тест: __bool__ проверка наличия расчётов"""
        assert bool(calculator) is False
        calculator.calculate(sample_wallpaper, 25.0)
        assert bool(calculator) is True
    
    def test_eq(self):
        """Тест: __eq__ сравнение калькуляторов"""
        calc1 = MaterialCalculator(reserve_percent=10, min_area=0.1, max_area=10000)
        calc2 = MaterialCalculator(reserve_percent=10, min_area=0.1, max_area=10000)
        calc3 = MaterialCalculator(reserve_percent=15, min_area=0.1, max_area=10000)
        assert calc1 == calc2
        assert calc1 != calc3
        assert calc1 != "not a calculator"
    
    def test_str(self, calculator):
        """Тест: __str__ строковое представление"""
        str_repr = str(calculator)
        assert "MaterialCalculator" in str_repr
        assert "10%" in str_repr
    
    def test_repr(self, calculator):
        """Тест: __repr__ представление для отладки"""
        repr_str = repr(calculator)
        assert "MaterialCalculator" in repr_str
        assert "reserve_percent=10" in repr_str


class TestRoomCalculator:
    """Тесты для класса RoomCalculator"""
    
    def test_room_calculator_creation(self, room_calculator):
        """Тест: Создание калькулятора комнат"""
        assert room_calculator.reserve_percent == 10
    
    def test_reserve_percent_property(self, room_calculator):
        """Тест: Свойство reserve_percent"""
        room_calculator.reserve_percent = 15
        assert room_calculator.reserve_percent == 15
    
    def test_calculate_floor_area(self, room_calculator):
        """Тест: Расчёт площади пола"""
        area = room_calculator.calculate_floor_area(5.0, 4.0)
        assert area == 20.0
    
    def test_calculate_floor_area_validation_negative_length(self, room_calculator):
        """Тест: Валидация отрицательной длины"""
        with pytest.raises(ValueError, match="положительными"):
            room_calculator.calculate_floor_area(-5.0, 4.0)
    
    def test_calculate_floor_area_validation_negative_width(self, room_calculator):
        """Тест: Валидация отрицательной ширины"""
        with pytest.raises(ValueError, match="положительными"):
            room_calculator.calculate_floor_area(5.0, -4.0)
    
    def test_calculate_wall_area(self, room_calculator):
        """Тест: Расчёт площади стен"""
        perimeter = 18.0  # 5м + 4м * 2
        height = 2.5
        area = room_calculator.calculate_wall_area(perimeter, height)
        assert area == 45.0
    
    def test_calculate_wall_area_with_doors_windows(self, room_calculator):
        """Тест: Расчёт площади стен с вычетом дверей и окон"""
        perimeter = 18.0
        height = 2.5
        door_area = 2.0
        window_area = 3.0
        area = room_calculator.calculate_wall_area(perimeter, height, door_area, window_area)
        assert area == 40.0  # 45 - 2 - 3
    
    def test_calculate_wall_area_validation_negative_perimeter(self, room_calculator):
        """Тест: Валидация отрицательного периметра"""
        with pytest.raises(ValueError, match="положительными"):
            room_calculator.calculate_wall_area(-18.0, 2.5)
    
    def test_calculate_wall_area_validation_negative_doors(self, room_calculator):
        """Тест: Валидация отрицательной площади дверей"""
        with pytest.raises(ValueError, match="не могут быть отрицательными"):
            room_calculator.calculate_wall_area(18.0, 2.5, door_area=-1)
    
    def test_calculate_wall_area_validation_too_much_deduction(self, room_calculator):
        """Тест: Валидация слишком большого вычета"""
        with pytest.raises(ValueError, match="должна быть положительной"):
            room_calculator.calculate_wall_area(18.0, 2.5, door_area=50.0)
    
    def test_calculate_materials_for_room_floor(self, room_calculator, sample_laminate):
        """Тест: Расчёт материалов для пола"""
        result = room_calculator.calculate_materials_for_room(
            sample_laminate, 5.0, 4.0, surface_type='floor'
        )
        assert result.area == 20.0
        assert result.material == sample_laminate
    
    def test_calculate_materials_for_room_wall(self, room_calculator, sample_wallpaper):
        """Тест: Расчёт материалов для стен"""
        result = room_calculator.calculate_materials_for_room(
            sample_wallpaper, 5.0, 4.0, height=2.5, surface_type='wall'
        )
        assert result.area > 0
        assert result.material == sample_wallpaper
    
    def test_calculate_materials_for_room_wall_no_height(self, room_calculator, sample_wallpaper):
        """Тест: Расчёт стен без указания высоты"""
        with pytest.raises(ValueError, match="необходимо указать высоту"):
            room_calculator.calculate_materials_for_room(
                sample_wallpaper, 5.0, 4.0, surface_type='wall'
            )
    
    def test_calculate_materials_for_room_invalid_type(self, room_calculator, sample_wallpaper):
        """Тест: Неверный тип поверхности"""
        with pytest.raises(ValueError, match="'floor' или 'wall'"):
            room_calculator.calculate_materials_for_room(
                sample_wallpaper, 5.0, 4.0, surface_type='ceiling'
            )
    
    def test_str(self, room_calculator):
        """Тест: Строковое представление"""
        str_repr = str(room_calculator)
        assert "RoomCalculator" in str_repr


class TestValidatePositiveNumber:
    """Тесты для функции validate_positive_number"""
    
    def test_validate_positive_int(self):
        """Тест: Валидация положительного целого числа"""
        result = validate_positive_number(10, "Тест")
        assert result == 10.0
    
    def test_validate_positive_float(self):
        """Тест: Валидация положительного дробного числа"""
        result = validate_positive_number(10.5, "Тест")
        assert result == 10.5
    
    def test_validate_positive_string(self):
        """Тест: Валидация строки с числом"""
        result = validate_positive_number("10.5", "Тест")
        assert result == 10.5
    
    def test_validate_zero(self):
        """Тест: Валидация нуля"""
        with pytest.raises(ValueError, match="положительным числом"):
            validate_positive_number(0, "Тест")
    
    def test_validate_negative(self):
        """Тест: Валидация отрицательного числа"""
        with pytest.raises(ValueError, match="положительным числом"):
            validate_positive_number(-10, "Тест")
    
    def test_validate_invalid_string(self):
        """Тест: Валидация невалидной строки"""
        with pytest.raises(ValueError, match="должно быть числом"):
            validate_positive_number("not a number", "Тест")
    
    def test_validate_none(self):
        """Тест: Валидация None"""
        with pytest.raises(ValueError):
            validate_positive_number(None, "Тест")


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_calculate_min_area(self, sample_wallpaper):
        """Тест: Расчёт с минимальной площадью"""
        calc = MaterialCalculator(min_area=0.1, max_area=10000)
        result = calc.calculate(sample_wallpaper, 0.1)
        assert result.area == 0.1
    
    def test_calculate_max_area(self, sample_wallpaper):
        """Тест: Расчёт с максимальной площадью"""
        calc = MaterialCalculator(min_area=0.1, max_area=10000)
        result = calc.calculate(sample_wallpaper, 10000)
        assert result.area == 10000
    
    def test_calculate_zero_reserve(self, sample_wallpaper):
        """Тест: Расчёт с нулевым запасом"""
        calc = MaterialCalculator(reserve_percent=0)
        result = calc.calculate(sample_wallpaper, 20.0)
        assert result.reserve_percent == 0
    
    def test_calculate_max_reserve(self, sample_wallpaper):
        """Тест: Расчёт с максимальным запасом"""
        calc = MaterialCalculator(reserve_percent=100)
        result = calc.calculate(sample_wallpaper, 20.0)
        assert result.reserve_percent == 100
        # С запасом 100% площадь должна удвоиться
        assert result.units_needed >= 1

