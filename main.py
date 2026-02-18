"""
Основная программа для расчёта отделочных материалов
Предоставляет консольный интерфейс для работы с калькулятором материалов
"""

import sys
import os
from pathlib import Path
from package import (
    Wallpaper, Tile, Laminate,
    MaterialCalculator, RoomCalculator,
    DocxExporter, ExcelExporter,
    DatabaseManager,
    validate_positive_number
)


class MaterialCalculatorApp:
    """Основное приложение для расчёта материалов"""
    
    def __init__(self, db_path='data/materials_calculator.db'):
        """
        Инициализация приложения
        
        Args:
            db_path (str): Путь к файлу базы данных
        """
        # Создаём директорию для БД, если её нет
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем менеджер БД
        self.db_manager = DatabaseManager(db_path=db_path)
        
        # Создаём калькуляторы с поддержкой БД
        self.calculator = MaterialCalculator(reserve_percent=10, db_manager=self.db_manager)
        self.room_calculator = RoomCalculator()
        self.materials = []
        self.results = []
    
    def __str__(self):
        return f"MaterialCalculatorApp(материалов: {len(self.materials)}, расчётов: {len(self.results)})"
    
    def __repr__(self):
        return f"MaterialCalculatorApp()"
    
    def clear_screen(self):
        """Очистка экрана (условная)"""
        print("\n" * 2)
    
    def print_header(self, text):
        """Печать заголовка"""
        print("=" * 60)
        print(f"  {text.upper()}")
        print("=" * 60)
    
    def print_separator(self):
        """Печать разделителя"""
        print("-" * 60)
    
    def input_positive_number(self, prompt):
        """
        Ввод положительного числа с валидацией
        
        Args:
            prompt (str): Текст запроса
        
        Returns:
            float: Введённое число
        """
        while True:
            try:
                value = input(prompt)
                return validate_positive_number(value)
            except ValueError as e:
                print(f"❌ Ошибка: {e}")
    
    def add_wallpaper(self):
        """Добавление обоев"""
        self.print_header("Добавление обоев")
        
        name = input("Название обоев: ")
        price = self.input_positive_number("Цена за рулон (₽): ")
        
        use_custom = input("Использовать стандартные размеры рулона (0.53×10.05м)? (д/н): ").lower()
        
        if use_custom == 'н':
            width = self.input_positive_number("Ширина рулона (м): ")
            length = self.input_positive_number("Длина рулона (м): ")
            wallpaper = Wallpaper(name, price, width, length)
        else:
            wallpaper = Wallpaper(name, price)
        
        self.materials.append(wallpaper)
        print(f"✅ Обои добавлены: {wallpaper}")
    
    def add_tile(self):
        """Добавление плитки"""
        self.print_header("Добавление плитки")
        
        name = input("Название плитки: ")
        price = self.input_positive_number("Цена за упаковку (₽): ")
        tiles_per_box = int(self.input_positive_number("Количество плиток в упаковке: "))
        
        use_custom = input("Использовать стандартные размеры плитки (0.3×0.3м)? (д/н): ").lower()
        
        if use_custom == 'н':
            width = self.input_positive_number("Ширина плитки (м): ")
            height = self.input_positive_number("Высота плитки (м): ")
            tile = Tile(name, price, tiles_per_box, width, height)
        else:
            tile = Tile(name, price, tiles_per_box)
        
        self.materials.append(tile)
        print(f"✅ Плитка добавлена: {tile}")
    
    def add_laminate(self):
        """Добавление ламината"""
        self.print_header("Добавление ламината")
        
        name = input("Название ламината: ")
        price = self.input_positive_number("Цена за упаковку (₽): ")
        planks_per_pack = int(self.input_positive_number("Количество досок в упаковке: "))
        
        use_custom = input("Использовать стандартные размеры доски (0.193×1.380м)? (д/н): ").lower()
        
        if use_custom == 'н':
            width = self.input_positive_number("Ширина доски (м): ")
            length = self.input_positive_number("Длина доски (м): ")
            laminate = Laminate(name, price, planks_per_pack, width, length)
        else:
            laminate = Laminate(name, price, planks_per_pack)
        
        self.materials.append(laminate)
        print(f"✅ Ламинат добавлен: {laminate}")
    
    def show_materials(self):
        """Показать список материалов"""
        if not self.materials:
            print("📋 Список материалов пуст")
            return
        
        self.print_header("Список материалов")
        for idx, material in enumerate(self.materials, 1):
            print(f"{idx}. {material}")
    
    def calculate_simple(self):
        """Простой расчёт по площади"""
        if not self.materials:
            print("❌ Сначала добавьте материалы!")
            return
        
        self.print_header("Простой расчёт")
        self.show_materials()
        
        choice = int(input("\nВыберите материал (номер): ")) - 1
        if choice < 0 or choice >= len(self.materials):
            print("❌ Неверный выбор!")
            return
        
        material = self.materials[choice]
        area = self.input_positive_number("Введите площадь (м²): ")
        
        reserve = input(f"Запас материала (текущий: {self.calculator.reserve_percent}%): ")
        if reserve.strip():
            self.calculator.reserve_percent = validate_positive_number(reserve)
        
        result = self.calculator.calculate(material, area)
        self.results.append(result)
        
        self.print_separator()
        print("📊 РЕЗУЛЬТАТ РАСЧЁТА:")
        print(result)
        self.print_separator()
    
    def calculate_room(self):
        """Расчёт для комнаты"""
        if not self.materials:
            print("❌ Сначала добавьте материалы!")
            return
        
        self.print_header("Расчёт для комнаты")
        self.show_materials()
        
        choice = int(input("\nВыберите материал (номер): ")) - 1
        if choice < 0 or choice >= len(self.materials):
            print("❌ Неверный выбор!")
            return
        
        material = self.materials[choice]
        
        print("\nТип расчёта:")
        print("1. Пол")
        print("2. Стены")
        calc_type = input("Выбор: ")
        
        length = self.input_positive_number("Длина комнаты (м): ")
        width = self.input_positive_number("Ширина комнаты (м): ")
        
        if calc_type == '2':
            height = self.input_positive_number("Высота потолка (м): ")
            door_area = self.input_positive_number("Площадь дверей (м²) [0 если нет]: ")
            window_area = self.input_positive_number("Площадь окон (м²) [0 если нет]: ")
            
            result = self.room_calculator.calculate_materials_for_room(
                material, length, width, height, door_area, window_area, 'wall'
            )
        else:
            result = self.room_calculator.calculate_materials_for_room(
                material, length, width, surface_type='floor'
            )
        
        self.results.append(result)
        
        self.print_separator()
        print("📊 РЕЗУЛЬТАТ РАСЧЁТА:")
        print(result)
        self.print_separator()
    
    def compare_materials(self):
        """Сравнение материалов"""
        if len(self.materials) < 2:
            print("❌ Для сравнения нужно минимум 2 материала!")
            return
        
        self.print_header("Сравнение материалов")
        area = self.input_positive_number("Введите площадь для сравнения (м²): ")
        
        results = self.calculator.compare_materials(self.materials, area)
        
        print("\n📊 РЕЗУЛЬТАТЫ СРАВНЕНИЯ (от дешёвого к дорогому):")
        self.print_separator()
        
        for idx, result in enumerate(results, 1):
            print(f"\n{idx}. {result.material.name}")
            print(f"   Единиц: {result.units_needed}")
            print(f"   Стоимость: {result.total_cost:.2f} ₽")
        
        self.print_separator()
    
    def export_results(self):
        """Экспорт результатов"""
        if not self.results:
            print("❌ Нет результатов для экспорта!")
            return
        
        self.print_header("Экспорт результатов")
        
        print("Доступные форматы:")
        print("1. DOCX (Word)")
        print("2. XLSX (Excel)")
        print("3. Оба формата")
        
        choice = input("Выбор: ")
        
        filename_base = input("Имя файла (без расширения, Enter для авто): ").strip()
        
        try:
            if choice in ['1', '3']:
                filename = f"{filename_base}.docx" if filename_base else None
                exporter = DocxExporter(filename)
                saved_file = exporter.export(self.results)
                print(f"✅ Экспортировано в DOCX: {saved_file}")
            
            if choice in ['2', '3']:
                filename = f"{filename_base}.xlsx" if filename_base else None
                exporter = ExcelExporter(filename)
                saved_file = exporter.export(self.results)
                print(f"✅ Экспортировано в XLSX: {saved_file}")
        
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
    
    def show_menu(self):
        """Показать главное меню"""
        self.print_header("Калькулятор отделочных материалов")
        print("1. Добавить обои")
        print("2. Добавить плитку")
        print("3. Добавить ламинат")
        print("4. Показать список материалов")
        print("5. Простой расчёт (по площади)")
        print("6. Расчёт для комнаты")
        print("7. Сравнить материалы")
        print("8. Экспортировать результаты")
        print("0. Выход")
        self.print_separator()
    
    def run(self):
        """Запуск приложения"""
        print("\n🏗️  Добро пожаловать в калькулятор отделочных материалов!\n")
        
        while True:
            self.show_menu()
            choice = input("Выберите действие: ")
            
            try:
                if choice == '1':
                    self.add_wallpaper()
                elif choice == '2':
                    self.add_tile()
                elif choice == '3':
                    self.add_laminate()
                elif choice == '4':
                    self.show_materials()
                elif choice == '5':
                    self.calculate_simple()
                elif choice == '6':
                    self.calculate_room()
                elif choice == '7':
                    self.compare_materials()
                elif choice == '8':
                    self.export_results()
                elif choice == '0':
                    print("\n👋 До свидания!")
                    sys.exit(0)
                else:
                    print("❌ Неверный выбор!")
            
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ Произошла ошибка: {e}")
            
            input("\n⏎ Нажмите Enter для продолжения...")
            self.clear_screen()


def main():
    """Точка входа в программу"""
    app = MaterialCalculatorApp()
    app.run()


if __name__ == "__main__":
    main()