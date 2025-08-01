#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 МИГРАЦИЯ ПРОЕКТОВ В БАЗУ ЛИНЕЕК ПРОДУКТОВ

Цель: Перенести проекты с тегом "Полиграфия товаров" из базы проектов 
в базу линеек продуктов с корректным названием (артикул + категория).

Логика:
1. Найти все проекты с тегом "Полиграфия товаров" за 2025 год
2. Извлечь артикул из названия проекта (3 буквы + цифры)
3. Определить категорию продукта (блендер, соковыжималка и т.д.)
4. Создать запись в базе линеек продуктов с правильным названием
5. Связать с исходным проектом через relation
"""

import os
import re
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

class ProductsMigrationService:
    """Сервис миграции проектов в линеки продуктов"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.projects_db_id = os.getenv('PROJECTS_DB')  # 342f18c6-7a5e-41fe-ad73-dcec00770f4e
        self.product_lines_db_id = os.getenv('PRODUCT_LINES_DB')  # ebaf801e-b212-465e-8b3f-e888eb583081
        
        if not self.notion_token:
            raise ValueError("❌ NOTION_TOKEN не найден в .env")
        
        if not self.projects_db_id:
            raise ValueError("❌ PROJECTS_DB не найден в .env")
        
        if not self.product_lines_db_id:
            raise ValueError("❌ PRODUCT_LINES_DB не найден в .env")
        
        # Убеждаемся, что ID баз не None
        if not self.projects_db_id or not self.product_lines_db_id:
            raise ValueError("❌ ID баз данных не могут быть None")
        
        self.client = AsyncClient(auth=self.notion_token)
        
        # Паттерны для извлечения артикулов (расширенные)
        self.article_patterns = [
            r'([A-Z]{3}-\d{2})',    # RGJ-04, BDM-07, ODM-01, RMD-02, RAP-01, RMC-01, RMJ-03
            r'([A-Z]{3}\d{2})',     # RGJ04, BDM07
            r'([A-Z]{2,3}\d{1,2})', # RG4, BD7
            r'([A-Z]{4}-\d{2})',    # Новые 4-буквенные артикулы
            r'([A-Z]{2}-\d{3})',    # Короткие артикулы с 3 цифрами
            r'([A-Z]{3}-\d{1})',    # 3 буквы + 1 цифра
            r'([A-Z]{2}\d{2})',     # 2 буквы + 2 цифры
            r'([A-Z]{3}-\d{2})',    # RMA-03, RMA-04, RMO-05, RPB-05, RPP-01, RPC-02, RGC-01, RMB-03, RMB-04, RFC-01, RAB-01, RMA-02
            r'([A-Z]{3}\d{2})',     # BDS-04, BDM-06, BDL-09
            r'([A-Z]{3}-\d{1})',    # RMP-04
            r'([A-Z]{3}\d{1})',     # IDF
        ]
        
        # Категории продуктов (расширенные на основе всех продуктов RAMIT)
        self.product_categories = {
            # Существующие категории
            'RGJ': 'Соковыжималка', 'JDM': 'Соковыжималка', 'RVJ': 'Соковыжималка',
            'RMJ': 'Соковыжималка', 'RMS': 'Соковыжималка',
            'RMG': 'Мельница',
            'BDM': 'Блендер', 'BDG': 'Блендер', 'RVB': 'Вакуумный блендер',
            'MIX': 'Миксер',
            'COF': 'Кофемолка', 'RMK': 'Кофемолка',
            'TEA': 'Чайник',
            'TOA': 'Тостер',
            'OVN': 'Духовка',
            'MIC': 'Микроволновка',
            'WAS': 'Посудомойка', 'DISH': 'Посудомойка',
            'REF': 'Холодильник',
            'COOK': 'Плита',
            'GRIL': 'Гриль', 'RAR': 'Аэрогриль',
            'STEAM': 'Пароварка', 'RMP': 'Пароварка',
            'SLOW': 'Мультиварка',
            'PRES': 'Скороварка',
            
            # Новые категории
            'ODM': 'Маслопресс',
            'RMD': 'Дистиллятор',
            'RAP': 'Кастрюли',
            'RMC': 'Кофемашина',
            'RMF': 'Фильтр',
            'RMV': 'Вакуумный пакер', 'RPV': 'Вакуумный пакер', 'RFV': 'Вакуумный пакер',
            'RCK': 'Нож',
            'RPI': 'Пила',
            'RMH': 'Хлебопечка',
            
            # Дополнительные категории
            'AIR': 'Очиститель воздуха',
            'HUM': 'Увлажнитель',
            'VAC': 'Пылесос',
            'IRR': 'Ирригатор',
            'MAS': 'Массажер',
            'LIG': 'Лампа',
            'FAN': 'Вентилятор',
            'HEA': 'Обогреватель',
            'COO': 'Кулер',
            'WAT': 'Водонагреватель',
            
            # Новые категории из проектов
            'RMA': 'Аэрогриль',
            'RMO': 'Озонатор',
            'RPB': 'Блендер',
            'RPP': 'Комбайн',
            'RPC': 'Плита',
            'RGC': 'Контейнер',
            'RMB': 'Бутылка',
            'RFC': 'Мультиварка',
            'RAB': 'Доска',
            'IDF': 'Турмалиновые изделия',
            'BDS': 'Блендер',
            'BDL': 'Блендер'
        }
    
    async def get_polygraphy_projects(self) -> List[Dict]:
        """Получить все проекты с тегом 'Полиграфия товаров' за 2024-2025 годы"""
        
        print("🔍 Поиск проектов с тегом 'Полиграфия товаров' за 2024-2025 годы...")
        
        # Фильтр: тег "Полиграфия товаров" + дата в 2024-2025 годах
        filter_params = {
            "and": [
                {
                    "or": [
                        {
                            "property": " Теги",
                            "multi_select": {
                                "contains": "Полиграфия товаров"
                            }
                        },
                        {
                            "property": " Теги",
                            "multi_select": {
                                "contains": "Полиграфия продуктов"
                            }
                        }
                    ]
                },
                {
                    "property": "Дата",
                    "date": {
                        "on_or_after": "2024-01-01"
                    }
                }
            ]
        }
        
        try:
            response = await self.client.databases.query(
                database_id=str(self.projects_db_id),
                filter=filter_params
            )
            
            projects = response.get("results", [])
            print(f"✅ Найдено {len(projects)} проектов с тегом 'Полиграфия товаров'")
            
            return projects
            
        except Exception as e:
            print(f"❌ Ошибка при получении проектов: {e}")
            return []
    
    def extract_article_and_category(self, project_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Извлечь артикул и категорию из названия проекта"""
        
        # Ищем артикул по паттернам
        for pattern in self.article_patterns:
            match = re.search(pattern, project_name.upper())
            if match:
                article = match.group(1)
                
                # Определяем категорию по префиксу артикула
                for prefix, category in self.product_categories.items():
                    if article.startswith(prefix):
                        return article, category
                
                # Если не нашли точное совпадение, пробуем по первым буквам
                for prefix, category in self.product_categories.items():
                    if article[:len(prefix)] == prefix:
                        return article, category
        
        return None, None
    
    def generate_product_line_name(self, article: str, category: str) -> str:
        """Сгенерировать название линейки продукта"""
        return f"{category} {article}"
    
    async def check_existing_product_line(self, article: str) -> Optional[str]:
        """Проверить существование линейки продукта с таким артикулом"""
        
        try:
            response = await self.client.databases.query(
                database_id=str(self.product_lines_db_id),
                filter={
                    "property": "Артикул",
                    "select": {
                        "equals": article
                    }
                }
            )
            
            results = response.get("results", [])
            if results:
                return results[0]["id"]  # Возвращаем ID существующей записи
            
            return None
            
        except Exception as e:
            print(f"❌ Ошибка при проверке существующей линейки: {e}")
            return None
    
    async def create_product_line(self, project_data: Dict, article: str, category: str) -> Optional[str]:
        """Создать запись в базе линеек продуктов"""
        
        product_line_name = self.generate_product_line_name(article, category)
        
        # Получаем свойства проекта
        project_properties = project_data.get("properties", {})
        project_name = ""
        
        # Извлекаем название проекта
        name_property = project_properties.get("Проект", {})
        if name_property.get("type") == "title":
            title_content = name_property.get("title", [])
            if title_content:
                project_name = title_content[0].get("plain_text", "")
        
        # Получаем описание проекта
        description = ""
        desc_property = project_properties.get("Описание", {})
        if desc_property.get("type") == "rich_text":
            rich_text_content = desc_property.get("rich_text", [])
            if rich_text_content:
                description = rich_text_content[0].get("plain_text", "")
        
        # Получаем дату проекта
        project_date = None
        date_property = project_properties.get("Дата", {})
        if date_property.get("type") == "date":
            project_date = date_property.get("date", {}).get("start")
        
        try:
            # Создаем запись в базе линеек продуктов
            page_data = {
                "parent": {"database_id": self.product_lines_db_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": product_line_name
                                }
                            }
                        ]
                    },
                    "Артикул": {
                        "select": {
                            "name": article
                        }
                    },
                    "Категория": {
                        "select": {
                            "name": category
                        }
                    },
                    "Статус": {
                        "status": {
                            "name": "Backlog"
                        }
                    },
                    "Проекты полиграфии продуктов": {
                        "relation": [
                            {
                                "id": project_data["id"]
                            }
                        ]
                    }
                }
            }
            
            response = await self.client.pages.create(**page_data)
            created_page_id = response["id"]
            
            print(f"✅ Создана линейка продукта: {product_line_name} (ID: {created_page_id})")
            return created_page_id
            
        except Exception as e:
            print(f"❌ Ошибка при создании линейки продукта: {e}")
            return None
    
    async def update_project_with_relation(self, project_id: str, product_line_id: str):
        """Обновить проект, добавив связь с линейкой продукта"""
        
        try:
            # Проверяем, есть ли поле для связи с линеками продуктов
            project_response = await self.client.pages.retrieve(project_id)
            project_properties = project_response.get("properties", {})
            
            # Ищем поле для связи с линеками продуктов
            relation_field = None
            for field_name, field_data in project_properties.items():
                if "линейк" in field_name.lower() or "продукт" in field_name.lower():
                    if field_data.get("type") == "relation":
                        relation_field = field_name
                        break
            
            if relation_field:
                # Добавляем связь
                await self.client.pages.update(
                    page_id=project_id,
                    properties={
                        relation_field: {
                            "relation": [
                                {
                                    "id": product_line_id
                                }
                            ]
                        }
                    }
                )
                print(f"✅ Добавлена связь проекта с линейкой продукта")
            else:
                print(f"⚠️ Поле для связи с линеками продуктов не найдено в проекте")
                
        except Exception as e:
            print(f"❌ Ошибка при обновлении проекта: {e}")
    
    async def migrate_projects_to_product_lines(self):
        """Основной метод миграции"""
        
        print("🚀 НАЧАЛО МИГРАЦИИ ПРОЕКТОВ В ЛИНЕЙКИ ПРОДУКТОВ")
        print("=" * 60)
        
        # Получаем проекты с тегом "Полиграфия товаров"
        projects = await self.get_polygraphy_projects()
        
        if not projects:
            print("❌ Проекты с тегом 'Полиграфия товаров' не найдены")
            return
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for project in projects:
            try:
                # Получаем название проекта
                project_properties = project.get("properties", {})
                name_property = project_properties.get("Проект", {})
                
                if name_property.get("type") != "title":
                    print(f"⚠️ Неверный тип поля названия проекта")
                    skipped_count += 1
                    continue
                
                title_content = name_property.get("title", [])
                if not title_content:
                    print(f"⚠️ Пустое название проекта")
                    skipped_count += 1
                    continue
                
                project_name = title_content[0].get("plain_text", "")
                
                print(f"\n📋 Обработка проекта: {project_name}")
                
                # Извлекаем артикул и категорию
                article, category = self.extract_article_and_category(project_name)
                
                if not article or not category:
                    print(f"⚠️ Не удалось извлечь артикул или категорию из '{project_name}'")
                    skipped_count += 1
                    continue
                
                print(f"   Артикул: {article}")
                print(f"   Категория: {category}")
                
                # Проверяем существование линейки продукта
                existing_id = await self.check_existing_product_line(article)
                
                if existing_id:
                    print(f"   ✅ Линейка продукта с артикулом {article} уже существует")
                    # Обновляем связь с проектом
                    await self.update_project_with_relation(project["id"], existing_id)
                    migrated_count += 1
                else:
                    # Создаем новую линейку продукта
                    product_line_id = await self.create_product_line(project, article, category)
                    
                    if product_line_id:
                        # Обновляем связь с проектом
                        await self.update_project_with_relation(project["id"], product_line_id)
                        migrated_count += 1
                    else:
                        error_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка при обработке проекта: {e}")
                error_count += 1
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ МИГРАЦИИ:")
        print(f"   ✅ Успешно мигрировано: {migrated_count}")
        print(f"   ⚠️ Пропущено: {skipped_count}")
        print(f"   ❌ Ошибок: {error_count}")
        print(f"   📋 Всего обработано: {len(projects)}")
        print("=" * 60)

async def main():
    """Главная функция"""
    
    try:
        service = ProductsMigrationService()
        await service.migrate_projects_to_product_lines()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 