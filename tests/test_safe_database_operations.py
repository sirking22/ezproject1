#!/usr/bin/env python3
"""
Тесты для безопасных операций с Notion
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from safe_database_operations import SafeDatabaseOperations

class TestSafeDatabaseOperations:
    """Тесты для SafeDatabaseOperations"""
    
    @pytest.fixture
    def safe_ops(self):
        """Фикстура для SafeDatabaseOperations"""
        ops = SafeDatabaseOperations()
        ops.server = Mock()
        return ops
    
    @pytest.mark.asyncio
    async def test_validate_payload_valid(self, safe_ops):
        """Тест валидации корректного payload"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Тип KPI": {"select": {"name": "Охват"}},
            "Целевое значение": {"number": 100}
        }
        
        # Мокаем схему
        safe_ops._get_database_schema = AsyncMock(return_value={
            "properties": {
                "Name": {"type": "title"},
                "Тип KPI": {"type": "select"},
                "Целевое значение": {"type": "number"}
            },
            "select_options": {
                "Тип KPI": ["Охват", "Вовлечённость", "Количество"]
            }
        })
        
        is_valid, errors = await safe_ops.validate_payload("test_db", properties)
        
        assert is_valid
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_payload_invalid_field(self, safe_ops):
        """Тест валидации payload с несуществующим полем"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Несуществующее поле": {"text": "value"}
        }
        
        # Мокаем схему
        safe_ops._get_database_schema = AsyncMock(return_value={
            "properties": {
                "Name": {"type": "title"}
            }
        })
        
        is_valid, errors = await safe_ops.validate_payload("test_db", properties)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("не существует в схеме" in error for error in errors)
    
    @pytest.mark.asyncio
    async def test_validate_payload_invalid_select_value(self, safe_ops):
        """Тест валидации payload с недопустимым значением select"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Тип KPI": {"select": {"name": "Недопустимое значение"}}
        }
        
        # Мокаем схему
        safe_ops._get_database_schema = AsyncMock(return_value={
            "properties": {
                "Name": {"type": "title"},
                "Тип KPI": {"type": "select"}
            },
            "select_options": {
                "Тип KPI": ["Охват", "Вовлечённость", "Количество"]
            }
        })
        
        is_valid, errors = await safe_ops.validate_payload("test_db", properties)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("содержит недопустимые значения" in error for error in errors)
    
    @pytest.mark.asyncio
    async def test_safe_create_page_success(self, safe_ops):
        """Тест успешного создания страницы"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Тип KPI": {"select": {"name": "Охват"}},
            "Целевое значение": {"number": 100}
        }
        
        # Мокаем все методы
        safe_ops.validate_payload = AsyncMock(return_value=(True, []))
        safe_ops.server.create_page = AsyncMock(return_value=[{
            "success": True,
            "page": {"id": "test-page-id"}
        }])
        safe_ops._post_check_page = AsyncMock(return_value=(True, []))
        
        result = await safe_ops.safe_create_page("test_db", properties)
        
        assert result["success"]
        assert result["page_id"] == "test-page-id"
        assert result["validation_passed"]
        assert result["post_check_passed"]
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_safe_create_page_validation_failed(self, safe_ops):
        """Тест создания страницы с ошибкой валидации"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Несуществующее поле": {"text": "value"}
        }
        
        # Мокаем валидацию с ошибкой
        safe_ops.validate_payload = AsyncMock(return_value=(False, ["Поле не существует"]))
        
        result = await safe_ops.safe_create_page("test_db", properties)
        
        assert not result["success"]
        assert not result["validation_passed"]
        assert len(result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_safe_create_page_post_check_failed(self, safe_ops):
        """Тест создания страницы с ошибкой post-check"""
        properties = {
            "Name": {"title": [{"text": {"content": "Test"}}]},
            "Тип KPI": {"select": {"name": "Охват"}}
        }
        
        # Мокаем успешную валидацию и создание, но неудачный post-check
        safe_ops.validate_payload = AsyncMock(return_value=(True, []))
        safe_ops.server.create_page = AsyncMock(return_value=[{
            "success": True,
            "page": {"id": "test-page-id"}
        }])
        safe_ops._post_check_page = AsyncMock(return_value=(False, ["Поле Name пустое"]))
        
        result = await safe_ops.safe_create_page("test_db", properties)
        
        # Страница создана, но с предупреждениями
        assert result["success"]
        assert not result["post_check_passed"]
        assert len(result["warnings"]) > 0
    
    def test_is_field_empty(self, safe_ops):
        """Тест проверки пустых полей"""
        # Пустые поля
        assert safe_ops._is_field_empty(None)
        assert safe_ops._is_field_empty({})
        assert safe_ops._is_field_empty({"title": []})
        assert safe_ops._is_field_empty({"title": [{}]})
        assert safe_ops._is_field_empty({"title": [{"text": {}}]})
        assert safe_ops._is_field_empty({"select": None})
        assert safe_ops._is_field_empty({"multi_select": []})
        
        # Непустые поля
        assert not safe_ops._is_field_empty({"title": [{"text": {"content": "Test"}}]})
        assert not safe_ops._is_field_empty({"select": {"name": "Test"}})
        assert not safe_ops._is_field_empty({"number": 100})
    
    @pytest.mark.asyncio
    async def test_safe_bulk_create(self, safe_ops):
        """Тест массового создания"""
        properties_list = [
            {"Name": {"title": [{"text": {"content": "Test 1"}}]}},
            {"Name": {"title": [{"text": {"content": "Test 2"}}]}},
            {"Name": {"title": [{"text": {"content": "Test 3"}}]}}
        ]
        
        # Мокаем safe_create_page
        safe_ops.safe_create_page = AsyncMock(side_effect=[
            {"success": True, "page_id": "page-1", "validation_passed": True, "post_check_passed": True},
            {"success": False, "errors": ["Ошибка валидации"]},
            {"success": True, "page_id": "page-3", "validation_passed": True, "post_check_passed": True}
        ])
        
        result = await safe_ops.safe_bulk_create("test_db", properties_list)
        
        assert result["total"] == 3
        assert result["created"] == 2
        assert result["failed"] == 1
        assert len(result["created_pages"]) == 2
        assert len(result["errors"]) > 0

if __name__ == "__main__":
    pytest.main([__file__]) 