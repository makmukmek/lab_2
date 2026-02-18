"""
Тесты для модуля exporters.py
Проверка экспортеров в форматы DOCX и Excel
"""

import pytest
import os
from pathlib import Path
from package.exporters import BaseExporter, DocxExporter, ExcelExporter
from package.models import CalculationResult


class TestBaseExporter:
    """Тесты для базового класса BaseExporter"""
    
    def test_base_exporter_cannot_be_instantiated(self):
        """Тест: BaseExporter нельзя создать напрямую (ABC)"""
        with pytest.raises(TypeError):
            BaseExporter()
    
    def test_base_exporter_allowed_extensions_default(self, docx_exporter):
        """Тест: Разрешённые расширения по умолчанию для DocxExporter"""
        assert 'docx' in docx_exporter.allowed_extensions
        assert 'doc' in docx_exporter.allowed_extensions
    
    def test_base_exporter_allowed_extensions_excel(self, excel_exporter):
        """Тест: Разрешённые расширения для ExcelExporter"""
        assert 'xlsx' in excel_exporter.allowed_extensions
        assert 'xls' in excel_exporter.allowed_extensions
    
    def test_filename_property_get(self, docx_exporter, tmp_path):
        """Тест: Получение имени файла"""
        filename = str(tmp_path / "test.docx")
        exporter = DocxExporter(filename)
        assert exporter.filename == filename
    
    def test_filename_property_set(self, docx_exporter, tmp_path):
        """Тест: Установка имени файла"""
        new_filename = str(tmp_path / "new_test.docx")
        docx_exporter.filename = new_filename
        assert docx_exporter.filename == new_filename
    
    def test_filename_validation_empty(self, docx_exporter):
        """Тест: Валидация пустого имени файла"""
        with pytest.raises(ValueError, match="не может быть пустым"):
            docx_exporter.filename = ""
    
    def test_filename_validation_invalid_extension(self, docx_exporter):
        """Тест: Валидация неверного расширения"""
        with pytest.raises(ValueError, match="не разрешено"):
            docx_exporter.filename = "test.txt"
    
    def test_allowed_extensions_property_get(self, docx_exporter):
        """Тест: Получение списка разрешённых расширений"""
        extensions = docx_exporter.allowed_extensions
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_allowed_extensions_property_set(self, docx_exporter):
        """Тест: Установка списка разрешённых расширений"""
        new_extensions = ['docx', 'doc', 'odt']
        docx_exporter.allowed_extensions = new_extensions
        assert set(docx_exporter.allowed_extensions) == set(new_extensions)
    
    def test_allowed_extensions_validation_not_list(self, docx_exporter):
        """Тест: Валидация типа allowed_extensions"""
        with pytest.raises(ValueError, match="должен быть списком"):
            docx_exporter.allowed_extensions = "docx,doc"
    
    def test_allowed_extensions_validation_invalid_format(self, docx_exporter):
        """Тест: Валидация формата расширений"""
        with pytest.raises(ValueError, match="строками из букв и цифр"):
            docx_exporter.allowed_extensions = ['doc.x', 'invalid.ext']
    
    def test_allowed_extensions_validation_current_filename(self, docx_exporter, tmp_path):
        """Тест: Валидация текущего filename при изменении allowed_extensions"""
        filename = str(tmp_path / "test.docx")
        docx_exporter.filename = filename
        # Меняем расширения, исключая docx
        with pytest.raises(ValueError):
            docx_exporter.allowed_extensions = ['xlsx']
    
    def test_generate_filename(self, docx_exporter):
        """Тест: Генерация имени файла"""
        filename = docx_exporter._generate_filename("docx")
        assert filename.endswith(".docx")
        assert "calculation_report_" in filename
    
    def test_generate_filename_uses_allowed_extension(self, docx_exporter):
        """Тест: Генерация использует разрешённое расширение"""
        # Если передать неразрешённое расширение, должно использоваться первое разрешённое
        filename = docx_exporter._generate_filename("txt")
        assert filename.endswith(".docx")  # Первое разрешённое расширение


class TestDocxExporter:
    """Тесты для класса DocxExporter"""
    
    def test_docx_exporter_creation(self, tmp_path):
        """Тест: Создание DOCX экспортера"""
        filename = str(tmp_path / "test.docx")
        exporter = DocxExporter(filename)
        assert exporter.filename == filename
    
    def test_docx_exporter_creation_no_filename(self):
        """Тест: Создание DOCX экспортера без имени файла"""
        exporter = DocxExporter()
        assert exporter.filename is None
    
    def test_docx_export_single_result(self, docx_exporter, calculation_result):
        """Тест: Экспорт одного результата"""
        filename = docx_exporter.export(calculation_result)
        assert os.path.exists(filename)
        assert filename.endswith(".docx")
        assert docx_exporter._export_count == 1
    
    def test_docx_export_multiple_results(self, docx_exporter, sample_results):
        """Тест: Экспорт нескольких результатов"""
        filename = docx_exporter.export(sample_results)
        assert os.path.exists(filename)
        assert docx_exporter._export_count == 1
    
    def test_docx_export_empty_list(self, docx_exporter):
        """Тест: Экспорт пустого списка"""
        with pytest.raises(ValueError, match="Нет данных для экспорта"):
            docx_exporter.export([])
    
    def test_docx_export_auto_filename(self, tmp_path, calculation_result):
        """Тест: Автоматическая генерация имени файла"""
        exporter = DocxExporter()
        filename = exporter.export(calculation_result)
        assert os.path.exists(filename)
        assert filename.endswith(".docx")
        assert exporter.filename == filename
    
    def test_docx_export_file_content(self, docx_exporter, calculation_result):
        """Тест: Проверка содержимого файла"""
        filename = docx_exporter.export(calculation_result)
        # Проверяем, что файл создан и не пустой
        assert os.path.getsize(filename) > 0
    
    def test_docx_export_count_increment(self, docx_exporter, calculation_result):
        """Тест: Увеличение счётчика экспортов"""
        initial_count = docx_exporter._export_count
        docx_exporter.export(calculation_result)
        assert docx_exporter._export_count == initial_count + 1
    
    def test_docx_exporter_str(self, docx_exporter):
        """Тест: Строковое представление"""
        str_repr = str(docx_exporter)
        assert "DocxExporter" in str_repr
    
    def test_docx_exporter_repr(self, docx_exporter):
        """Тест: Представление для отладки"""
        repr_str = repr(docx_exporter)
        assert "DocxExporter" in repr_str
        assert "allowed_extensions" in repr_str


class TestExcelExporter:
    """Тесты для класса ExcelExporter"""
    
    def test_excel_exporter_creation(self, tmp_path):
        """Тест: Создание Excel экспортера"""
        filename = str(tmp_path / "test.xlsx")
        exporter = ExcelExporter(filename)
        assert exporter.filename == filename
    
    def test_excel_exporter_creation_no_filename(self):
        """Тест: Создание Excel экспортера без имени файла"""
        exporter = ExcelExporter()
        assert exporter.filename is None
    
    def test_excel_export_single_result(self, excel_exporter, calculation_result):
        """Тест: Экспорт одного результата"""
        filename = excel_exporter.export(calculation_result)
        assert os.path.exists(filename)
        assert filename.endswith(".xlsx")
        assert excel_exporter._export_count == 1
    
    def test_excel_export_multiple_results(self, excel_exporter, sample_results):
        """Тест: Экспорт нескольких результатов"""
        filename = excel_exporter.export(sample_results)
        assert os.path.exists(filename)
        assert excel_exporter._export_count == 1
    
    def test_excel_export_empty_list(self, excel_exporter):
        """Тест: Экспорт пустого списка"""
        with pytest.raises(ValueError, match="Нет данных для экспорта"):
            excel_exporter.export([])
    
    def test_excel_export_auto_filename(self, tmp_path, calculation_result):
        """Тест: Автоматическая генерация имени файла"""
        exporter = ExcelExporter()
        filename = exporter.export(calculation_result)
        assert os.path.exists(filename)
        assert filename.endswith(".xlsx")
        assert exporter.filename == filename
    
    def test_excel_export_file_content(self, excel_exporter, calculation_result):
        """Тест: Проверка содержимого файла"""
        filename = excel_exporter.export(calculation_result)
        # Проверяем, что файл создан и не пустой
        assert os.path.getsize(filename) > 0
    
    def test_excel_export_count_increment(self, excel_exporter, calculation_result):
        """Тест: Увеличение счётчика экспортов"""
        initial_count = excel_exporter._export_count
        excel_exporter.export(calculation_result)
        assert excel_exporter._export_count == initial_count + 1
    
    def test_excel_exporter_str(self, excel_exporter):
        """Тест: Строковое представление"""
        str_repr = str(excel_exporter)
        assert "ExcelExporter" in str_repr
    
    def test_excel_exporter_repr(self, excel_exporter):
        """Тест: Представление для отладки"""
        repr_str = repr(excel_exporter)
        assert "ExcelExporter" in repr_str
        assert "allowed_extensions" in repr_str


class TestContextManager:
    """Тесты для context manager"""
    
    def test_context_manager_enter(self, docx_exporter):
        """Тест: Вход в контекстный менеджер"""
        with docx_exporter as exporter:
            assert exporter._is_context_active is True
        assert docx_exporter._is_context_active is False
    
    def test_context_manager_exit(self, docx_exporter):
        """Тест: Выход из контекстного менеджера"""
        with docx_exporter:
            pass
        assert docx_exporter._is_context_active is False
    
    def test_context_manager_returns_self(self, docx_exporter):
        """Тест: Context manager возвращает сам объект"""
        with docx_exporter as exporter:
            assert exporter is docx_exporter
    
    def test_context_manager_with_export(self, docx_exporter, calculation_result):
        """Тест: Использование context manager с экспортом"""
        with docx_exporter as exporter:
            assert exporter._is_context_active is True
            filename = exporter.export(calculation_result)
            assert os.path.exists(filename)
        assert exporter._is_context_active is False
    
    def test_context_manager_exception_propagation(self, docx_exporter):
        """Тест: Исключения не подавляются context manager"""
        with pytest.raises(ValueError):
            with docx_exporter as exporter:
                exporter.filename = ""  # Вызовет исключение


class TestExtensionValidation:
    """Тесты для валидации расширений"""
    
    def test_docx_extension_validation(self, tmp_path):
        """Тест: Валидация расширения .docx"""
        filename = str(tmp_path / "test.docx")
        exporter = DocxExporter(filename)
        assert exporter.filename == filename
    
    def test_doc_extension_validation(self, tmp_path):
        """Тест: Валидация расширения .doc"""
        filename = str(tmp_path / "test.doc")
        exporter = DocxExporter(filename)
        assert exporter.filename == filename
    
    def test_xlsx_extension_validation(self, tmp_path):
        """Тест: Валидация расширения .xlsx"""
        filename = str(tmp_path / "test.xlsx")
        exporter = ExcelExporter(filename)
        assert exporter.filename == filename
    
    def test_xls_extension_validation(self, tmp_path):
        """Тест: Валидация расширения .xls"""
        filename = str(tmp_path / "test.xls")
        exporter = ExcelExporter(filename)
        assert exporter.filename == filename
    
    def test_invalid_extension_docx_exporter(self, tmp_path):
        """Тест: Неверное расширение для DocxExporter"""
        filename = str(tmp_path / "test.xlsx")
        with pytest.raises(ValueError, match="не разрешено"):
            DocxExporter(filename)
    
    def test_invalid_extension_excel_exporter(self, tmp_path):
        """Тест: Неверное расширение для ExcelExporter"""
        filename = str(tmp_path / "test.docx")
        with pytest.raises(ValueError, match="не разрешено"):
            ExcelExporter(filename)
    
    def test_case_insensitive_extension(self, tmp_path):
        """Тест: Расширение нечувствительно к регистру"""
        filename = str(tmp_path / "test.DOCX")
        exporter = DocxExporter(filename)
        assert exporter.filename == filename
    
    def test_extension_with_dot(self, tmp_path):
        """Тест: Расширение с точкой в allowed_extensions"""
        filename = str(tmp_path / "test.docx")
        exporter = DocxExporter(filename)
        # Должно работать даже если в allowed_extensions есть точка
        exporter.allowed_extensions = ['.docx', 'doc']
        assert exporter.filename == filename


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_export_very_long_filename(self, tmp_path, calculation_result):
        """Тест: Экспорт с очень длинным именем файла"""
        long_name = "a" * 200 + ".docx"
        filename = str(tmp_path / long_name)
        exporter = DocxExporter(filename)
        result_filename = exporter.export(calculation_result)
        assert os.path.exists(result_filename)
    
    def test_export_special_characters_filename(self, tmp_path, calculation_result):
        """Тест: Экспорт с особыми символами в имени"""
        filename = str(tmp_path / "test_123-456.docx")
        exporter = DocxExporter(filename)
        result_filename = exporter.export(calculation_result)
        assert os.path.exists(result_filename)
    
    def test_multiple_exports_same_exporter(self, docx_exporter, calculation_result):
        """Тест: Множественные экспорты одним экспортером"""
        filename1 = docx_exporter.export(calculation_result)
        filename2 = docx_exporter.export(calculation_result)
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)
        assert docx_exporter._export_count == 2
    
    def test_export_large_number_of_results(self, excel_exporter, calculator, sample_wallpaper):
        """Тест: Экспорт большого количества результатов"""
        results = []
        for i in range(100):
            result = calculator.calculate(sample_wallpaper, 10.0 + i)
            results.append(result)
        filename = excel_exporter.export(results)
        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0

