#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 СИСТЕМА УПРАВЛЕНИЯ МАТЕРИАЛАМИ ДЛЯ ПРОДУКТОВ RAMIT

Цель: Автоматически находить и связывать материалы (видео, фото, документы) 
с продуктами в базе линеек продуктов.

Логика:
1. Получить все продукты из базы линеек продуктов
2. Найти материалы на Яндекс.Диске по артикулу продукта
3. Создать связи между продуктами и материалами
4. Валидировать ссылки и проверять доступность
"""

import os
import re
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from notion_client import AsyncClient
import requests

load_dotenv()

class ProductMaterialsManager:
    """Менеджер материалов для продуктов RAMIT"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.product_lines_db_id = os.getenv('PRODUCT_LINES_DB')
        self.materials_db_id = os.getenv('MATERIALS_DB')
        self.yandex_disk_token = os.getenv('YANDEX_DISK_TOKEN')
        
        if not self.notion_token:
            raise ValueError("❌ NOTION_TOKEN не найден в .env")
        
        if not self.product_lines_db_id:
            raise ValueError("❌ PRODUCT_LINES_DB не найден в .env")
        
        if not self.materials_db_id:
            raise ValueError("❌ MATERIALS_DB не найден в .env")
        
        if not self.yandex_disk_token:
            raise ValueError("❌ YANDEX_DISK_TOKEN не найден в .env")
        
        self.client = AsyncClient(auth=self.notion_token)
        
        # Типы материалов для поиска
        self.material_types = {
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'photo': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
            'archive': ['.zip', '.rar', '.7z']
        }
        
        # Паттерны для поиска материалов по артикулу
        self.material_patterns = [
            r'(\w+-\d+)',  # RGJ-04, BDM-07
            r'(\w+\d+)',   # RGJ04, BDM07
            r'(\w+_\d+)',  # RGJ_04, BDM_07
        ]
    
    async def get_all_product_lines(self) -> List[Dict]:
        """Получить все линейки продуктов"""
        
        print("🔍 Получение всех линеек продуктов...")
        
        try:
            response = await self.client.databases.query(
                database_id=str(self.product_lines_db_id)
            )
            
            products = response.get("results", [])
            print(f"✅ Найдено {len(products)} линеек продуктов")
            
            return products
            
        except Exception as e:
            print(f"❌ Ошибка при получении линеек продуктов: {e}")
            return []
    
    def extract_article_from_product(self, product_data: Dict) -> Optional[str]:
        """Извлечь артикул из продукта"""
        
        properties = product_data.get("properties", {})
        article_property = properties.get("Артикул", {})
        
        if article_property.get("type") == "select":
            select_data = article_property.get("select", {})
            if select_data:
                return select_data.get("name")
        
        return None
    
    def search_materials_on_yandex_disk(self, article: str) -> List[Dict]:
        """Поиск материалов на Яндекс.Диске по артикулу"""
        
        print(f"🔍 Поиск материалов для артикула {article} на Яндекс.Диске...")
        
        materials = []
        
        try:
            # Поиск по разным вариантам артикула
            search_variants = [
                article,
                article.replace('-', ''),
                article.replace('-', '_'),
                article.lower(),
                article.upper()
            ]
            
            for variant in search_variants:
                # Поиск файлов на Яндекс.Диске
                search_url = "https://cloud-api.yandex.net/v1/disk/resources/search"
                headers = {
                    "Authorization": f"OAuth {self.yandex_disk_token}",
                    "Content-Type": "application/json"
                }
                
                params = {
                    "q": variant,
                    "limit": 100
                }
                
                response = requests.get(search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    for item in items:
                        file_path = item.get("path", "")
                        file_name = item.get("name", "")
                        file_type = item.get("mime_type", "")
                        file_size = item.get("size", 0)
                        
                        # Определяем тип материала
                        material_type = self.determine_material_type(file_name, file_type)
                        
                        if material_type:
                            materials.append({
                                "name": file_name,
                                "path": file_path,
                                "type": material_type,
                                "size": file_size,
                                "mime_type": file_type,
                                "article": article,
                                "search_variant": variant
                            })
            
            print(f"✅ Найдено {len(materials)} материалов для артикула {article}")
            return materials
            
        except Exception as e:
            print(f"❌ Ошибка при поиске материалов: {e}")
            return []
    
    def determine_material_type(self, file_name: str, mime_type: str) -> Optional[str]:
        """Определить тип материала по имени файла и MIME-типу"""
        
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Проверяем по расширению
        for material_type, extensions in self.material_types.items():
            if file_extension in extensions:
                return material_type
        
        # Проверяем по MIME-типу
        if 'video' in mime_type:
            return 'video'
        elif 'image' in mime_type:
            return 'photo'
        elif 'pdf' in mime_type or 'document' in mime_type:
            return 'document'
        elif 'archive' in mime_type or 'zip' in mime_type:
            return 'archive'
        
        return None
    
    async def create_material_in_notion(self, material_data: Dict) -> Optional[str]:
        """Создать материал в базе материалов Notion"""
        
        try:
            # Создаем запись в базе материалов
            page_data = {
                "parent": {"database_id": self.materials_db_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": material_data["name"]
                                }
                            }
                        ]
                    },
                    "Тип": {
                        "select": {
                            "name": material_data["type"].title()
                        }
                    },
                    "Размер": {
                        "number": material_data["size"]
                    },
                    "URL": {
                        "url": f"https://disk.yandex.ru{material_data['path']}"
                    },
                    "Артикул продукта": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": material_data["article"]
                                }
                            }
                        ]
                    },
                    "Статус": {
                        "status": {
                            "name": "Активный"
                        }
                    }
                }
            }
            
            response = await self.client.pages.create(**page_data)
            created_page_id = response["id"]
            
            print(f"✅ Создан материал: {material_data['name']} (ID: {created_page_id})")
            return created_page_id
            
        except Exception as e:
            print(f"❌ Ошибка при создании материала: {e}")
            return None
    
    async def link_material_to_product(self, product_id: str, material_id: str):
        """Связать материал с продуктом"""
        
        try:
            # Получаем текущие связи продукта
            product_response = await self.client.pages.retrieve(product_id)
            product_properties = product_response.get("properties", {})
            
            # Ищем поле для связи с материалами
            materials_field = None
            for field_name, field_data in product_properties.items():
                if "материал" in field_name.lower() or "файл" in field_name.lower():
                    if field_data.get("type") == "relation":
                        materials_field = field_name
                        break
            
            if materials_field:
                # Получаем существующие связи
                existing_relations = product_properties[materials_field].get("relation", [])
                
                # Добавляем новую связь
                new_relations = existing_relations + [{"id": material_id}]
                
                # Обновляем продукт
                await self.client.pages.update(
                    page_id=product_id,
                    properties={
                        materials_field: {
                            "relation": new_relations
                        }
                    }
                )
                
                print(f"✅ Материал связан с продуктом")
            else:
                print(f"⚠️ Поле для связи с материалами не найдено в продукте")
                
        except Exception as e:
            print(f"❌ Ошибка при связывании материала: {e}")
    
    async def process_product_materials(self, product_data: Dict):
        """Обработать материалы для одного продукта"""
        
        # Извлекаем артикул
        article = self.extract_article_from_product(product_data)
        
        if not article:
            print(f"⚠️ Не удалось извлечь артикул из продукта")
            return
        
        # Получаем название продукта
        properties = product_data.get("properties", {})
        name_property = properties.get("Name", {})
        
        if name_property.get("type") != "title":
            print(f"⚠️ Неверный тип поля названия продукта")
            return
        
        title_content = name_property.get("title", [])
        if not title_content:
            print(f"⚠️ Пустое название продукта")
            return
        
        product_name = title_content[0].get("plain_text", "")
        
        print(f"\n📋 Обработка продукта: {product_name} (артикул: {article})")
        
        # Ищем материалы на Яндекс.Диске
        materials = self.search_materials_on_yandex_disk(article)
        
        if not materials:
            print(f"⚠️ Материалы для артикула {article} не найдены")
            return
        
        # Создаем материалы в Notion и связываем с продуктом
        for material in materials:
            material_id = await self.create_material_in_notion(material)
            
            if material_id:
                await self.link_material_to_product(product_data["id"], material_id)
    
    async def process_all_products(self):
        """Обработать материалы для всех продуктов"""
        
        print("🚀 НАЧАЛО ОБРАБОТКИ МАТЕРИАЛОВ ДЛЯ ПРОДУКТОВ")
        print("=" * 60)
        
        # Получаем все продукты
        products = await self.get_all_product_lines()
        
        if not products:
            print("❌ Линеки продуктов не найдены")
            return
        
        processed_count = 0
        materials_count = 0
        error_count = 0
        
        for product in products:
            try:
                await self.process_product_materials(product)
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка при обработке продукта: {e}")
                error_count += 1
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ МАТЕРИАЛОВ:")
        print(f"   ✅ Обработано продуктов: {processed_count}")
        print(f"   📁 Найдено материалов: {materials_count}")
        print(f"   ❌ Ошибок: {error_count}")
        print(f"   📋 Всего продуктов: {len(products)}")
        print("=" * 60)

async def main():
    """Основная функция"""
    
    try:
        manager = ProductMaterialsManager()
        await manager.process_all_products()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 