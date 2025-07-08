#!/usr/bin/env python3
"""
🎯 ВНЕДРЕНИЕ KPI СИСТЕМЫ
Создает все KPI для YouTube, Полиграфии, Соцсетей и Карточек товаров
с автоматическим добавлением опций в поля
"""

import asyncio
import json
import os
from typing import Dict, List, Any
from datetime import datetime

# Импортируем безопасные операции
from safe_database_operations import SafeDatabaseOperations

class KPISystemImplementation:
    """Внедрение полной KPI системы"""
    
    def __init__(self):
        self.kpi_db_id = "1d6ace03d9ff80bfb809ed21dfd2150c"
        self.safe_ops = SafeDatabaseOperations()
        
        # Определяем все KPI по направлениям
        self.kpi_structure = {
            "YouTube": [
                {"name": "Просмотры", "type": "number", "goal": 10000},
                {"name": "Подписчики", "type": "number", "goal": 1000},
                {"name": "CTR", "type": "number", "goal": 5.0},
                {"name": "Вовлечённость", "type": "number", "goal": 8.0}
            ],
            "Полиграфия": [
                {"name": "Эффективность", "type": "number", "goal": 95.0},
                {"name": "Количество правок", "type": "number", "goal": 2},
                {"name": "Качество выполнения", "type": "number", "goal": 90.0},
                {"name": "Время выполнения", "type": "number", "goal": 48}
            ],
            "Соцсети": [
                {"name": "Переходы", "type": "number", "goal": 500},
                {"name": "Клики", "type": "number", "goal": 1000},
                {"name": "Вовлечённость", "type": "number", "goal": 6.0},
                {"name": "Охват", "type": "number", "goal": 5000}
            ],
            "Карточки товаров": [
                {"name": "Добавления в корзину", "type": "number", "goal": 200},
                {"name": "Продажи", "type": "number", "goal": 50},
                {"name": "Конверсия", "type": "number", "goal": 25.0},
                {"name": "Клики", "type": "number", "goal": 1000},
                {"name": "Просмотры", "type": "number", "goal": 10000}
            ]
        }
    
    async def create_kpi_records(self):
        """Создание всех KPI записей"""
        print("🎯 ВНЕДРЕНИЕ KPI СИСТЕМЫ")
        print("=" * 50)
        
        total_created = 0
        total_errors = 0
        
        for direction, kpis in self.kpi_structure.items():
            print(f"\n📊 Создаем KPI для направления: {direction}")
            print("-" * 40)
            
            for kpi in kpis:
                try:
                    # Создаем properties для записи
                    properties = {
                        "Name": {
                            "title": [{
                                "text": {
                                    "content": f"{direction} - {kpi['name']}"
                                }
                            }]
                        },
                        "Тип контента / направление": {
                            "multi_select": [{"name": direction}]
                        },
                        "Тип KPI": {
                            "select": {"name": kpi['name']}
                        },
                        "Цель / задача": {
                            "rich_text": [{
                                "text": {
                                    "content": f"{kpi['goal']} {self._get_unit(kpi['name'])}"
                                }
                            }]
                        }
                    }
                    
                    # Создаем запись с автоматическим добавлением опций
                    result = await self.safe_ops.safe_create_page_with_auto_options(
                        self.kpi_db_id, 
                        properties
                    )
                    
                    if result["success"]:
                        print(f"  ✅ {direction} - {kpi['name']}: {result['page_id']}")
                        total_created += 1
                    else:
                        print(f"  ❌ {direction} - {kpi['name']}: {result.get('error', 'Неизвестная ошибка')}")
                        total_errors += 1
                        
                except Exception as e:
                    print(f"  ❌ {direction} - {kpi['name']}: {e}")
                    total_errors += 1
        
        print(f"\n📈 ИТОГИ:")
        print(f"  ✅ Создано записей: {total_created}")
        print(f"  ❌ Ошибок: {total_errors}")
        print(f"  📊 Всего KPI: {sum(len(kpis) for kpis in self.kpi_structure.values())}")
    
    def _get_unit(self, kpi_name: str) -> str:
        """Получение единицы измерения для KPI"""
        units = {
            "Просмотры": "просмотров",
            "Подписчики": "подписчиков", 
            "CTR": "%",
            "Вовлечённость": "%",
            "Эффективность": "%",
            "Количество правок": "правок",
            "Качество выполнения": "%",
            "Время выполнения": "часов",
            "Переходы": "переходов",
            "Клики": "кликов",
            "Охват": "охват",
            "Добавления в корзину": "добавлений",
            "Продажи": "продаж",
            "Конверсия": "%"
        }
        return units.get(kpi_name, "")
    
    async def test_mcp_integration(self):
        """Тестирование интеграции с MCP сервером"""
        print("\n🔧 ТЕСТИРОВАНИЕ MCP ИНТЕГРАЦИИ")
        print("=" * 40)
        
        # Тестовая запись
        test_properties = {
            "Name": {
                "title": [{
                    "text": {
                        "content": "Тест MCP интеграции"
                    }
                }]
            },
            "Тип контента / направление": {
                "multi_select": [{"name": "YouTube"}]
            },
            "Тип KPI": {
                "select": {"name": "Просмотры"}
            },
            "Цель / задача": {
                "rich_text": [{
                    "text": {
                        "content": "1000 просмотров"
                    }
                }]
            }
        }
        
        try:
            result = await self.safe_ops.safe_create_page_with_auto_options(
                self.kpi_db_id,
                test_properties
            )
            
            if result["success"]:
                print("  ✅ MCP интеграция работает корректно")
                print(f"  📝 ID записи: {result['page_id']}")
            else:
                print(f"  ❌ Ошибка MCP: {result.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            print(f"  ❌ Исключение MCP: {e}")
    
    async def verify_kpi_structure(self):
        """Проверка структуры KPI базы"""
        print("\n🔍 ПРОВЕРКА СТРУКТУРЫ KPI БАЗЫ")
        print("=" * 40)
        
        try:
            # Получаем информацию о базе
            db_info = await self.safe_ops.get_database_info(self.kpi_db_id)
            
            if db_info:
                properties = db_info.get("properties", {})
                print(f"  📋 Всего полей: {len(properties)}")
                
                # Проверяем ключевые поля
                key_fields = ["Name", "Тип контента / направление", "Тип KPI", "Цель / задача"]
                for field in key_fields:
                    if field in properties:
                        print(f"  ✅ {field}")
                    else:
                        print(f"  ❌ {field} - ОТСУТСТВУЕТ")
                        
            else:
                print("  ❌ Не удалось получить информацию о базе")
                
        except Exception as e:
            print(f"  ❌ Ошибка проверки: {e}")

async def main():
    """Основная функция"""
    kpi_system = KPISystemImplementation()
    
    # Проверяем структуру
    await kpi_system.verify_kpi_structure()
    
    # Тестируем MCP интеграцию
    await kpi_system.test_mcp_integration()
    
    # Создаем все KPI
    await kpi_system.create_kpi_records()
    
    print("\n🎉 ВНЕДРЕНИЕ KPI СИСТЕМЫ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    asyncio.run(main()) 