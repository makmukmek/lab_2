"""
Модуль database.py
Содержит классы для работы с базой данных SQLite3
Уровень: WELL-DONE
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from .models import Material, Wallpaper, Tile, Laminate, CalculationResult


class DatabaseManager:
    """Менеджер для работы с базой данных SQLite3"""
    
    def __init__(self, db_path='data/materials_calculator.db'):
        """
        Инициализация менеджера БД
        
        Args:
            db_path (str): Путь к файлу базы данных
        """
        self.db_path = db_path
        self.connection = None
        
        # Создаём директорию для БД, если её нет
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Убедиться, что БД и таблицы созданы"""
        with self.get_connection() as conn:
            self._create_tables(conn)
    
    def _create_tables(self, conn):
        """
        Создать таблицы в базе данных
        
        Args:
            conn: Соединение с БД
        """
        cursor = conn.cursor()
        
        # Таблица материалов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                material_type TEXT NOT NULL,
                price_per_unit REAL NOT NULL,
                unit_coverage REAL NOT NULL,
                specifications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица расчётов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,
                material_name TEXT NOT NULL,
                material_type TEXT NOT NULL,
                area REAL NOT NULL,
                reserve_percent REAL NOT NULL,
                units_needed INTEGER NOT NULL,
                total_cost REAL NOT NULL,
                calculation_type TEXT,
                room_dimensions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # Таблица истории экспортов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                format TEXT NOT NULL,
                calculations_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager для получения соединения с БД
        
        Yields:
            sqlite3.Connection: Соединение с базой данных
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа по именам колонок
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def __enter__(self):
        """Вход в context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из context manager"""
        if self.connection:
            if exc_type:
                self.connection.rollback()
            else:
                self.connection.commit()
            self.connection.close()
            self.connection = None
    
    def __str__(self):
        return f"DatabaseManager(db_path='{self.db_path}')"
    
    def __repr__(self):
        return f"DatabaseManager('{self.db_path}')"
    
    # ========== CRUD для материалов ==========
    
    def save_material(self, material):
        """
        Сохранить материал в БД
        
        Args:
            material (Material): Объект материала
        
        Returns:
            int: ID сохранённого материала
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Определяем тип материала
            material_type = material.__class__.__name__.lower()
            
            # Получаем детальную информацию
            specs = material.get_detailed_info()
            
            cursor.execute('''
                INSERT INTO materials (name, material_type, price_per_unit, unit_coverage, specifications)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                material.name,
                material_type,
                material.price_per_unit,
                material.unit_coverage,
                json.dumps(specs)
            ))
            
            return cursor.lastrowid
    
    def get_material(self, material_id):
        """
        Получить материал по ID
        
        Args:
            material_id (int): ID материала
        
        Returns:
            dict: Данные материала или None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM materials WHERE id = ?', (material_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_materials(self):
        """
        Получить все материалы из БД
        
        Returns:
            list: Список словарей с данными материалов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM materials ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def delete_material(self, material_id):
        """
        Удалить материал из БД
        
        Args:
            material_id (int): ID материала
        
        Returns:
            bool: True если удалён, False если не найден
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM materials WHERE id = ?', (material_id,))
            return cursor.rowcount > 0
    
    # ========== CRUD для расчётов ==========
    
    def save_calculation(self, calculation_result, calculation_type='simple', room_dimensions=None):
        """
        Сохранить результат расчёта в БД
        
        Args:
            calculation_result (CalculationResult): Результат расчёта
            calculation_type (str): Тип расчёта ('simple', 'room_floor', 'room_wall')
            room_dimensions (dict): Размеры комнаты (если применимо)
        
        Returns:
            int: ID сохранённого расчёта
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            material = calculation_result.material
            material_type = material.__class__.__name__.lower()
            
            # Сериализуем размеры комнаты если есть
            room_dims_json = json.dumps(room_dimensions) if room_dimensions else None
            
            cursor.execute('''
                INSERT INTO calculations 
                (material_name, material_type, area, reserve_percent, 
                 units_needed, total_cost, calculation_type, room_dimensions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                material.name,
                material_type,
                calculation_result.area,
                calculation_result.reserve_percent,
                calculation_result.units_needed,
                calculation_result.total_cost,
                calculation_type,
                room_dims_json
            ))
            
            return cursor.lastrowid
    
    def get_calculation_history(self, limit=10):
        """
        Получить историю расчётов
        
        Args:
            limit (int): Максимальное количество записей
        
        Returns:
            list: Список словарей с данными расчётов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM calculations 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_all_calculations(self):
        """
        Получить все расчёты
        
        Returns:
            list: Список всех расчётов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM calculations ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def delete_calculation(self, calculation_id):
        """
        Удалить расчёт из БД
        
        Args:
            calculation_id (int): ID расчёта
        
        Returns:
            bool: True если удалён
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calculations WHERE id = ?', (calculation_id,))
            return cursor.rowcount > 0
    
    def clear_all_calculations(self):
        """
        Очистить всю историю расчётов
        
        Returns:
            int: Количество удалённых записей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calculations')
            return cursor.rowcount
    
    # ========== Статистика ==========
    
    def get_statistics(self):
        """
        Получить статистику по расчётам
        
        Returns:
            dict: Статистические данные
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Общее количество расчётов
            cursor.execute('SELECT COUNT(*) as total FROM calculations')
            total_calculations = cursor.fetchone()['total']
            
            # Общая стоимость всех расчётов
            cursor.execute('SELECT SUM(total_cost) as total_cost FROM calculations')
            total_cost = cursor.fetchone()['total_cost'] or 0
            
            # Общая площадь
            cursor.execute('SELECT SUM(area) as total_area FROM calculations')
            total_area = cursor.fetchone()['total_area'] or 0
            
            # Самый популярный материал
            cursor.execute('''
                SELECT material_name, COUNT(*) as count 
                FROM calculations 
                GROUP BY material_name 
                ORDER BY count DESC 
                LIMIT 1
            ''')
            popular_material = cursor.fetchone()
            
            # Средняя стоимость расчёта
            avg_cost = total_cost / total_calculations if total_calculations > 0 else 0
            
            # Распределение по типам материалов
            cursor.execute('''
                SELECT material_type, COUNT(*) as count, SUM(total_cost) as cost
                FROM calculations 
                GROUP BY material_type
            ''')
            material_distribution = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_calculations': total_calculations,
                'total_cost': round(total_cost, 2),
                'total_area': round(total_area, 2),
                'average_cost': round(avg_cost, 2),
                'most_popular_material': popular_material['material_name'] if popular_material else None,
                'popular_material_count': popular_material['count'] if popular_material else 0,
                'material_distribution': material_distribution
            }
    
    def get_recent_calculations_summary(self, days=7):
        """
        Получить сводку по недавним расчётам
        
        Args:
            days (int): Количество дней для анализа
        
        Returns:
            dict: Сводка расчётов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as count,
                    SUM(total_cost) as total_cost,
                    SUM(area) as total_area
                FROM calculations 
                WHERE created_at >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            row = cursor.fetchone()
            
            return {
                'period_days': days,
                'calculations_count': row['count'],
                'total_cost': round(row['total_cost'] or 0, 2),
                'total_area': round(row['total_area'] or 0, 2)
            }
    
    # ========== История экспортов ==========
    
    def save_export(self, filename, format_type, calculations_count):
        """
        Сохранить информацию об экспорте
        
        Args:
            filename (str): Имя файла
            format_type (str): Формат ('docx' или 'xlsx')
            calculations_count (int): Количество экспортированных расчётов
        
        Returns:
            int: ID записи экспорта
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO export_history (filename, format, calculations_count)
                VALUES (?, ?, ?)
            ''', (filename, format_type, calculations_count))
            
            return cursor.lastrowid
    
    def get_export_history(self, limit=10):
        """
        Получить историю экспортов
        
        Args:
            limit (int): Максимальное количество записей
        
        Returns:
            list: Список экспортов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM export_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # ========== Утилиты ==========
    
    def get_database_info(self):
        """
        Получить информацию о базе данных
        
        Returns:
            dict: Информация о БД
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Количество записей в каждой таблице
            cursor.execute('SELECT COUNT(*) as count FROM materials')
            materials_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM calculations')
            calculations_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM export_history')
            exports_count = cursor.fetchone()['count']
            
            # Размер БД (примерный)
            import os
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'db_path': self.db_path,
                'materials_count': materials_count,
                'calculations_count': calculations_count,
                'exports_count': exports_count,
                'db_size_kb': round(db_size / 1024, 2)
            }
    
    def backup_database(self, backup_path):
        """
        Создать резервную копию БД
        
        Args:
            backup_path (str): Путь для сохранения backup
        
        Returns:
            bool: True если успешно
        """
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Ошибка при создании backup: {e}")
            return False