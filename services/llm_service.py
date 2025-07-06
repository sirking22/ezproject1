"""
Advanced LLM Service for Notion operations with mass editing and intelligent processing
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import httpx
from datetime import datetime

try:
    from .advanced_notion_service import (
        AdvancedNotionService, 
        NotionFilter, 
        NotionUpdate, 
        NotionRelation
    )
except ImportError:
    from advanced_notion_service import (
        AdvancedNotionService, 
        NotionFilter, 
        NotionUpdate, 
        NotionRelation
    )

logger = logging.getLogger(__name__)

@dataclass
class LLMTask:
    """Задача для LLM обработки"""
    task_type: str
    data: Dict[str, Any]
    context: Optional[str] = None
    priority: int = 1

class AdvancedLLMService:
    """Продвинутый LLM сервис для работы с Notion"""
    
    def __init__(self):
        self.notion_service = AdvancedNotionService()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = "deepseek/deepseek-chat"
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # Системные промпты для разных задач
        self.prompts = {
            "analyze": """Ты эксперт по анализу данных. Проанализируй предоставленные данные из Notion и дай подробный анализ с выводами и рекомендациями.""",
            
            "categorize": """Ты эксперт по категоризации контента. Проанализируй предоставленные элементы и предложи их категоризацию с обоснованием.""",
            
            "extract": """Ты эксперт по извлечению структурированных данных. Из предоставленного текста извлеки ключевую информацию в структурированном виде.""",
            
            "summarize": """Ты эксперт по созданию кратких сводок. Создай краткую но информативную сводку по предоставленным данным.""",
            
            "relate": """Ты эксперт по анализу связей. Найди и опиши связи между предоставленными элементами данных.""",
            
            "update": """Ты эксперт по обновлению данных. На основе предоставленной информации предложи обновления для указанных элементов.""",
            
            "prioritize": """Ты эксперт по приоритизации задач. Проанализируй предоставленные элементы и предложи их приоритизацию с обоснованием.""",
            
            "generate": """Ты эксперт по генерации контента. Создай качественный контент на основе предоставленных данных и требований."""
        }
    
    async def analyze_database_with_llm(
        self, 
        db_name: str, 
        analysis_type: str = "comprehensive",
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Анализирует базу данных с помощью LLM"""
        
        db_id = await self.notion_service.get_database_by_name(db_name)
        if not db_id:
            return {"error": f"Database '{db_name}' not found"}
        
        try:
            # Получаем данные из базы
            pages = await self.notion_service.query_database_bulk(db_id, limit=limit)
            
            # Подготавливаем данные для LLM
            llm_data = {
                "database_name": db_name,
                "total_pages": len(pages),
                "sample_pages": self._prepare_pages_for_llm(pages[:10])  # Первые 10 для примера
            }
            
            # Создаем промпт
            prompt = f"""
            Проанализируй базу данных Notion "{db_name}":
            
            Общая информация:
            - Всего записей: {llm_data['total_pages']}
            
            Примеры записей:
            {json.dumps(llm_data['sample_pages'], indent=2, ensure_ascii=False)}
            
            Тип анализа: {analysis_type}
            
            Предоставь подробный анализ с:
            1. Обзором структуры данных
            2. Качеством заполнения полей
            3. Выявленными паттернами
            4. Рекомендациями по улучшению
            5. Предложениями по оптимизации
            """
            
            # Получаем ответ от LLM
            llm_response = await self._call_llm(prompt, "analyze")
            
            return {
                "database_name": db_name,
                "analysis_type": analysis_type,
                "data_summary": llm_data,
                "llm_analysis": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing database with LLM: {e}")
            return {"error": str(e)}
    
    async def bulk_categorize_pages(
        self, 
        db_name: str, 
        category_property: str,
        criteria: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Массовая категоризация страниц с помощью LLM"""
        
        db_id = await self.notion_service.get_database_by_name(db_name)
        if not db_id:
            return {"error": f"Database '{db_name}' not found"}
        
        try:
            # Получаем страницы для категоризации
            pages = await self.notion_service.query_database_bulk(db_id, limit=limit)
            
            # Группируем страницы для пакетной обработки
            batch_size = 20
            results = []
            
            for i in range(0, len(pages), batch_size):
                batch = pages[i:i + batch_size]
                batch_data = self._prepare_pages_for_llm(batch)
                
                # Создаем промпт для категоризации
                prompt = f"""
                Категоризируй следующие записи по критерию: {criteria}
                
                Записи для категоризации:
                {json.dumps(batch_data, indent=2, ensure_ascii=False)}
                
                Верни результат в формате JSON:
                {{
                    "page_id": "категория",
                    ...
                }}
                
                Категории должны быть краткими и последовательными.
                """
                
                # Получаем категории от LLM
                llm_response = await self._call_llm(prompt, "categorize")
                
                try:
                    categories = json.loads(llm_response)
                    
                    # Подготавливаем обновления
                    updates = []
                    for page_id, category in categories.items():
                        if page_id in [p["id"] for p in batch]:
                            updates.append((
                                page_id,
                                [NotionUpdate(category_property, category, "select")]
                            ))
                    
                    # Выполняем обновления
                    update_results = await self.notion_service.update_pages_bulk(updates)
                    results.extend(update_results)
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response from LLM: {llm_response}")
                
                # Пауза между пакетами
                await asyncio.sleep(1)
            
            return {
                "database_name": db_name,
                "categorized_pages": len([r for r in results if r.get("success")]),
                "failed_pages": len([r for r in results if not r.get("success")]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error bulk categorizing: {e}")
            return {"error": str(e)}
    
    async def intelligent_data_extraction(
        self, 
        source_text: str, 
        target_db: str,
        extraction_schema: Dict[str, str]
    ) -> Dict[str, Any]:
        """Интеллектуальное извлечение данных из текста в Notion"""
        
        db_id = await self.notion_service.get_database_by_name(target_db)
        if not db_id:
            return {"error": f"Database '{target_db}' not found"}
        
        try:
            # Получаем схему целевой базы данных
            db_schema = await self.notion_service.get_database_schema(db_id)
            
            # Создаем промпт для извлечения данных
            prompt = f"""
            Извлеки структурированные данные из следующего текста:
            
            {source_text}
            
            Схема извлечения:
            {json.dumps(extraction_schema, indent=2, ensure_ascii=False)}
            
            Схема целевой базы данных:
            {json.dumps(db_schema, indent=2, ensure_ascii=False)}
            
            Верни результат в формате JSON, готовом для создания записей в Notion:
            {{
                "records": [
                    {{
                        "property_name": "value",
                        ...
                    }},
                    ...
                ]
            }}
            """
            
            # Получаем извлеченные данные
            llm_response = await self._call_llm(prompt, "extract")
            
            try:
                extracted_data = json.loads(llm_response)
                records = extracted_data.get("records", [])
                
                # Создаем записи в Notion
                created_pages = []
                for record in records:
                    try:
                        # Преобразуем данные в формат Notion
                        properties = {}
                        for prop_name, value in record.items():
                            if prop_name in db_schema:
                                prop_type = db_schema[prop_name].get("type", "rich_text")
                                properties[prop_name] = self.notion_service._format_property_value(
                                    value, prop_type
                                )
                        
                        # Создаем страницу
                        page = await self.notion_service.client.pages.create(
                            parent={"database_id": db_id},
                            properties=properties
                        )
                        created_pages.append(page)
                        
                    except Exception as e:
                        logger.error(f"Error creating page: {e}")
                
                return {
                    "source_length": len(source_text),
                    "extracted_records": len(records),
                    "created_pages": len(created_pages),
                    "pages": created_pages
                }
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from LLM: {llm_response}")
                return {"error": "Invalid response format from LLM"}
            
        except Exception as e:
            logger.error(f"Error in data extraction: {e}")
            return {"error": str(e)}
    
    async def smart_relation_builder(
        self, 
        source_db: str, 
        target_db: str,
        relation_criteria: str
    ) -> Dict[str, Any]:
        """Умное создание связей между записями в разных базах"""
        
        source_db_id = await self.notion_service.get_database_by_name(source_db)
        target_db_id = await self.notion_service.get_database_by_name(target_db)
        
        if not source_db_id or not target_db_id:
            return {"error": "One or both databases not found"}
        
        try:
            # Получаем данные из обеих баз
            source_pages = await self.notion_service.query_database_bulk(source_db_id)
            target_pages = await self.notion_service.query_database_bulk(target_db_id)
            
            # Подготавливаем данные для LLM
            source_data = self._prepare_pages_for_llm(source_pages)
            target_data = self._prepare_pages_for_llm(target_pages)
            
            # Создаем промпт для поиска связей
            prompt = f"""
            Найди логические связи между записями в двух базах данных:
            
            Критерий связи: {relation_criteria}
            
            База данных источника ({source_db}):
            {json.dumps(source_data, indent=2, ensure_ascii=False)}
            
            База данных назначения ({target_db}):
            {json.dumps(target_data, indent=2, ensure_ascii=False)}
            
            Верни результат в формате JSON:
            {{
                "relations": [
                    {{
                        "source_page_id": "id",
                        "target_page_id": "id",
                        "confidence": 0.95,
                        "reason": "explanation"
                    }},
                    ...
                ]
            }}
            
            Включай только связи с высокой уверенностью (>0.8).
            """
            
            # Получаем предложенные связи
            llm_response = await self._call_llm(prompt, "relate")
            
            try:
                relations_data = json.loads(llm_response)
                relations = relations_data.get("relations", [])
                
                # Определяем свойство связи (первое relation свойство в источнике)
                source_schema = await self.notion_service.get_database_schema(source_db_id)
                relation_property = None
                
                for prop_name, prop_config in source_schema.items():
                    if prop_config.get("type") == "relation":
                        relation_property = prop_name
                        break
                
                if not relation_property:
                    return {"error": "No relation property found in source database"}
                
                # Создаем связи
                notion_relations = [
                    NotionRelation(
                        source_page_id=rel["source_page_id"],
                        target_page_id=rel["target_page_id"],
                        relation_property=relation_property
                    )
                    for rel in relations if rel.get("confidence", 0) > 0.8
                ]
                
                # Выполняем создание связей
                results = await self.notion_service.create_relations_bulk(notion_relations)
                
                return {
                    "source_database": source_db,
                    "target_database": target_db,
                    "proposed_relations": len(relations),
                    "created_relations": len([r for r in results if r.get("success")]),
                    "failed_relations": len([r for r in results if not r.get("success")]),
                    "relations_details": relations,
                    "results": results
                }
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from LLM: {llm_response}")
                return {"error": "Invalid response format from LLM"}
            
        except Exception as e:
            logger.error(f"Error building relations: {e}")
            return {"error": str(e)}
    
    async def bulk_content_generation(
        self, 
        db_name: str,
        template_field: str,
        target_field: str,
        generation_prompt: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Массовая генерация контента для записей"""
        
        db_id = await self.notion_service.get_database_by_name(db_name)
        if not db_id:
            return {"error": f"Database '{db_name}' not found"}
        
        try:
            # Получаем записи для обработки
            pages = await self.notion_service.query_database_bulk(db_id, limit=limit)
            
            # Обрабатываем пачками
            batch_size = 10
            results = []
            
            for i in range(0, len(pages), batch_size):
                batch = pages[i:i + batch_size]
                
                # Подготавливаем данные для генерации
                generation_tasks = []
                for page in batch:
                    template_value = self._extract_field_value(page, template_field)
                    if template_value:
                        generation_tasks.append({
                            "page_id": page["id"],
                            "template": template_value,
                            "prompt": generation_prompt
                        })
                
                # Генерируем контент для пачки
                for task in generation_tasks:
                    full_prompt = f"""
                    {task['prompt']}
                    
                    Исходные данные: {task['template']}
                    
                    Создай качественный контент на основе исходных данных.
                    """
                    
                    generated_content = await self._call_llm(full_prompt, "generate")
                    
                    # Обновляем запись
                    update_result = await self.notion_service.update_pages_bulk([
                        (task["page_id"], [NotionUpdate(target_field, generated_content)])
                    ])
                    
                    results.extend(update_result)
                    
                    # Пауза между запросами
                    await asyncio.sleep(0.5)
                
                # Пауза между пачками
                await asyncio.sleep(2)
            
            return {
                "database_name": db_name,
                "processed_pages": len([r for r in results if r.get("success")]),
                "failed_pages": len([r for r in results if not r.get("success")]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk content generation: {e}")
            return {"error": str(e)}
    
    def _prepare_pages_for_llm(self, pages: List[Dict]) -> List[Dict]:
        """Подготавливает страницы для передачи в LLM"""
        prepared_pages = []
        
        for page in pages:
            simplified_page = {
                "id": page["id"],
                "properties": {}
            }
            
            for prop_name, prop_value in page.get("properties", {}).items():
                prop_type = prop_value.get("type", "unknown")
                simplified_value = self.notion_service._extract_property_value(prop_value, prop_type)
                if simplified_value:
                    simplified_page["properties"][prop_name] = simplified_value
            
            prepared_pages.append(simplified_page)
        
        return prepared_pages
    
    def _extract_field_value(self, page: Dict, field_name: str) -> Optional[str]:
        """Извлекает значение поля из страницы"""
        prop_value = page.get("properties", {}).get(field_name)
        if not prop_value:
            return None
        
        prop_type = prop_value.get("type", "unknown")
        return str(self.notion_service._extract_property_value(prop_value, prop_type))
    
    async def _call_llm(self, prompt: str, task_type: str = "general") -> str:
        """Вызывает LLM API"""
        try:
            system_prompt = self.prompts.get(task_type, self.prompts["analyze"])
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"LLM API error: {response.status_code} - {response.text}")
                    return f"Ошибка API: {response.status_code}"
                    
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Ошибка вызова LLM: {str(e)}" 