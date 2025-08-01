#!/usr/bin/env python3
"""
🎯 PRODUCT LIFECYCLE MANAGER
Управление жизненным циклом продуктов RAMIT

ФУНКЦИОНАЛ:
1. Автоматические переходы между статусами жизненного цикла
2. Мониторинг времени в каждом статусе
3. Уведомления о задержках
4. Аналитика жизненного цикла
5. Интеграция с существующими базами

ЖИЗНЕННЫЙ ЦИКЛ:
Предпроизводство → Производство → Продвижение → Поддержка → Архив
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from notion_client import AsyncClient
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/product_lifecycle.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductStatus:
    """Статус продукта в жизненном цикле"""
    name: str
    description: str
    color: str
    next_statuses: List[str]
    min_duration_days: int = 0
    max_duration_days: int = 365
    auto_transition: bool = False
    transition_conditions: Optional[Dict[str, Any]] = None

@dataclass
class ProductLifecycleEvent:
    """Событие жизненного цикла продукта"""
    product_id: str
    product_name: str
    old_status: str
    new_status: str
    timestamp: datetime
    reason: str
    triggered_by: str  # "manual", "auto", "system"
    metadata: Optional[Dict[str, Any]] = None

class ProductLifecycleManager:
    """Менеджер жизненного цикла продуктов"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.product_lines_db = os.getenv("PRODUCT_LINES_DB", "")
        self.projects_db = os.getenv("PROJECTS_DB", "")
        
        # Определяем статусы жизненного цикла
        self.lifecycle_statuses = {
            "Предпроизводство": ProductStatus(
                name="Предпроизводство",
                description="Идея, концепция, прототип, планирование",
                color="yellow",
                next_statuses=["Производство", "Архив"],
                min_duration_days=7,
                max_duration_days=90,
                auto_transition=False,
                transition_conditions={
                    "has_prototype": True,
                    "has_business_plan": True,
                    "has_funding": True
                }
            ),
            "Производство": ProductStatus(
                name="Производство",
                description="Активное производство, разработка",
                color="blue",
                next_statuses=["Продвижение", "Архив"],
                min_duration_days=30,
                max_duration_days=180,
                auto_transition=False,
                transition_conditions={
                    "has_materials": True,
                    "has_quality_control": True,
                    "production_ready": True
                }
            ),
            "Продвижение": ProductStatus(
                name="Продвижение",
                description="Маркетинг, реклама, продажи",
                color="orange",
                next_statuses=["Поддержка", "Архив"],
                min_duration_days=14,
                max_duration_days=365,
                auto_transition=False,
                transition_conditions={
                    "has_marketing_materials": True,
                    "has_sales_channel": True,
                    "stable_sales": True
                }
            ),
            "Поддержка": ProductStatus(
                name="Поддержка",
                description="Обслуживание, обновления, поддержка клиентов",
                color="green",
                next_statuses=["Архив"],
                min_duration_days=0,
                max_duration_days=730,
                auto_transition=False,
                transition_conditions={
                    "has_support_system": True,
                    "has_update_plan": True
                }
            ),
            "Архив": ProductStatus(
                name="Архив",
                description="Снят с производства, архив",
                color="gray",
                next_statuses=[],
                min_duration_days=0,
                max_duration_days=0,
                auto_transition=False
            )
        }
        
        # Статистика
        self.stats = {
            "total_products": 0,
            "products_by_status": {},
            "transitions_today": 0,
            "overdue_products": 0,
            "avg_time_in_status": {}
        }

    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Получить все продукты из базы линеек"""
        try:
            response = await self.notion.databases.query(
                database_id=self.product_lines_db,
                sorts=[{"property": "Name", "direction": "ascending"}]
            )
            
            products = []
            for page in response.get("results", []):
                product = self._parse_product_page(page)
                if product:
                    products.append(product)
            
            logger.info(f"📦 Получено {len(products)} продуктов")
            return products
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения продуктов: {e}")
            return []

    def _parse_product_page(self, page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсинг страницы продукта"""
        try:
            properties = page.get("properties", {})
            
            # Название
            name_prop = properties.get("Name", {})
            name = ""
            if name_prop.get("type") == "title":
                title = name_prop.get("title", [])
                name = " ".join([t.get("plain_text", "") for t in title]) if title else ""
            
            # Артикул
            article_prop = properties.get("Артикул", {})
            article = ""
            if article_prop.get("type") == "select":
                article = article_prop.get("select", {}).get("name", "")
            
            # Категория
            category_prop = properties.get("Категория", {})
            category = ""
            if category_prop.get("type") == "select":
                category = category_prop.get("select", {}).get("name", "")
            
            # Статус
            status_prop = properties.get("Статус", {})
            status = ""
            if status_prop.get("type") == "status":
                status = status_prop.get("status", {}).get("name", "")
            
            # Дата создания
            created_time = page.get("created_time", "")
            
            return {
                "id": page.get("id", ""),
                "name": name,
                "article": article,
                "category": category,
                "status": status,
                "created_time": created_time,
                "last_edited_time": page.get("last_edited_time", "")
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга продукта: {e}")
            return None

    async def update_product_status(self, product_id: str, new_status: str, reason: str = "", triggered_by: str = "manual") -> bool:
        """Обновить статус продукта"""
        try:
            if new_status not in self.lifecycle_statuses:
                logger.error(f"❌ Неизвестный статус: {new_status}")
                return False
            
            # Обновляем статус в Notion
            await self.notion.pages.update(
                page_id=product_id,
                properties={
                    "Статус": {
                        "status": {
                            "name": new_status
                        }
                    }
                }
            )
            
            # Логируем событие
            event = ProductLifecycleEvent(
                product_id=product_id,
                product_name="",  # Будет заполнено позже
                old_status="",    # Будет заполнено позже
                new_status=new_status,
                timestamp=datetime.now(),
                reason=reason,
                triggered_by=triggered_by
            )
            
            await self._log_lifecycle_event(event)
            
            logger.info(f"✅ Статус продукта {product_id} изменен на '{new_status}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления статуса: {e}")
            return False

    async def check_auto_transitions(self) -> Dict[str, Any]:
        """Проверить и выполнить автоматические переходы"""
        logger.info("🔄 Проверка автоматических переходов...")
        
        products = await self.get_all_products()
        transitions_made = []
        overdue_products = []
        
        for product in products:
            current_status = product.get("status", "")
            
            if current_status not in self.lifecycle_statuses:
                continue
            
            status_config = self.lifecycle_statuses[current_status]
            
            # Проверяем время в статусе
            created_time = datetime.fromisoformat(product["created_time"].replace("Z", "+00:00"))
            time_in_status = datetime.now(created_time.tzinfo) - created_time
            days_in_status = time_in_status.days
            
            # Проверяем превышение максимального времени
            if days_in_status > status_config.max_duration_days:
                overdue_products.append({
                    "product": product,
                    "days_overdue": days_in_status - status_config.max_duration_days
                })
                
                # Автоматический переход в следующий статус или архив
                if status_config.next_statuses:
                    next_status = status_config.next_statuses[0]  # Берем первый доступный
                    success = await self.update_product_status(
                        product["id"], 
                        next_status, 
                        f"Автоматический переход: превышено время в статусе '{current_status}' ({days_in_status} дней)",
                        "auto"
                    )
                    
                    if success:
                        transitions_made.append({
                            "product": product,
                            "from_status": current_status,
                            "to_status": next_status,
                            "reason": "Превышение времени"
                        })
        
        # Обновляем статистику
        self.stats["transitions_today"] += len(transitions_made)
        self.stats["overdue_products"] = len(overdue_products)
        
        logger.info(f"✅ Автоматические переходы: {len(transitions_made)} выполнено, {len(overdue_products)} просрочено")
        
        return {
            "transitions_made": transitions_made,
            "overdue_products": overdue_products,
            "total_checked": len(products)
        }

    async def get_lifecycle_analytics(self) -> Dict[str, Any]:
        """Получить аналитику жизненного цикла"""
        products = await self.get_all_products()
        
        # Статистика по статусам
        status_counts = {}
        for product in products:
            status = product.get("status", "Неизвестно")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Среднее время в статусах
        avg_time_by_status = {}
        for status in self.lifecycle_statuses:
            products_in_status = [p for p in products if p.get("status") == status]
            if products_in_status:
                total_days = 0
                for product in products_in_status:
                    created_time = datetime.fromisoformat(product["created_time"].replace("Z", "+00:00"))
                    time_in_status = datetime.now(created_time.tzinfo) - created_time
                    total_days += time_in_status.days
                
                avg_time_by_status[status] = total_days / len(products_in_status)
        
        # Продукты, требующие внимания
        attention_needed = []
        for product in products:
            status = product.get("status", "")
            if status in self.lifecycle_statuses:
                status_config = self.lifecycle_statuses[status]
                created_time = datetime.fromisoformat(product["created_time"].replace("Z", "+00:00"))
                time_in_status = datetime.now(created_time.tzinfo) - created_time
                days_in_status = time_in_status.days
                
                if days_in_status > status_config.max_duration_days * 0.8:  # 80% от максимума
                    attention_needed.append({
                        "product": product,
                        "days_in_status": days_in_status,
                        "max_days": status_config.max_duration_days
                    })
        
        return {
            "total_products": len(products),
            "status_distribution": status_counts,
            "avg_time_by_status": avg_time_by_status,
            "attention_needed": attention_needed,
            "lifecycle_efficiency": self._calculate_lifecycle_efficiency(products)
        }

    def _calculate_lifecycle_efficiency(self, products: List[Dict[str, Any]]) -> Dict[str, float]:
        """Рассчитать эффективность жизненного цикла"""
        total_products = len(products)
        if total_products == 0:
            return {}
        
        # Продукты в правильных статусах
        correct_status_count = 0
        for product in products:
            status = product.get("status", "")
            if status in self.lifecycle_statuses:
                correct_status_count += 1
        
        # Продукты без задержек
        no_delay_count = 0
        for product in products:
            status = product.get("status", "")
            if status in self.lifecycle_statuses:
                status_config = self.lifecycle_statuses[status]
                created_time = datetime.fromisoformat(product["created_time"].replace("Z", "+00:00"))
                time_in_status = datetime.now(created_time.tzinfo) - created_time
                days_in_status = time_in_status.days
                
                if days_in_status <= status_config.max_duration_days:
                    no_delay_count += 1
        
        return {
            "status_accuracy": (correct_status_count / total_products) * 100,
            "timeline_efficiency": (no_delay_count / total_products) * 100,
            "overall_efficiency": ((correct_status_count + no_delay_count) / (total_products * 2)) * 100
        }

    async def _log_lifecycle_event(self, event: ProductLifecycleEvent):
        """Логировать событие жизненного цикла"""
        try:
            log_file = "logs/product_lifecycle_events.json"
            
            # Загружаем существующие события
            events = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            # Добавляем новое событие
            event_dict = asdict(event)
            event_dict["timestamp"] = event.timestamp.isoformat()
            events.append(event_dict)
            
            # Сохраняем (оставляем последние 1000 событий)
            events = events[-1000:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Ошибка логирования события: {e}")

    async def generate_lifecycle_report(self) -> Dict[str, Any]:
        """Сгенерировать отчет по жизненному циклу"""
        analytics = await self.get_lifecycle_analytics()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_products": analytics["total_products"],
                "products_by_status": analytics["status_distribution"],
                "efficiency_metrics": analytics["lifecycle_efficiency"]
            },
            "details": {
                "avg_time_by_status": analytics["avg_time_by_status"],
                "attention_needed": analytics["attention_needed"]
            },
            "recommendations": self._generate_recommendations(analytics)
        }
        
        # Сохраняем отчет
        report_file = f"reports/lifecycle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Отчет по жизненному циклу сохранен: {report_file}")
        return report

    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Генерировать рекомендации на основе аналитики"""
        recommendations = []
        
        # Анализ распределения по статусам
        status_dist = analytics["status_distribution"]
        total = analytics["total_products"]
        
        if total > 0:
            # Проверяем заторы в статусах
            for status, count in status_dist.items():
                percentage = (count / total) * 100
                if percentage > 40:  # Больше 40% в одном статусе
                    recommendations.append(f"⚠️ Затор в статусе '{status}': {count} продуктов ({percentage:.1f}%)")
            
            # Проверяем эффективность
            efficiency = analytics["lifecycle_efficiency"]
            if efficiency.get("timeline_efficiency", 100) < 80:
                recommendations.append("🚨 Низкая эффективность временных рамок - много просроченных продуктов")
            
            if efficiency.get("status_accuracy", 100) < 90:
                recommendations.append("⚠️ Низкая точность статусов - продукты в неправильных статусах")
        
        # Рекомендации по продуктам, требующим внимания
        attention_needed = analytics["attention_needed"]
        if attention_needed:
            recommendations.append(f"📋 {len(attention_needed)} продуктов требуют внимания (близки к просрочке)")
        
        return recommendations

    async def run_daily_lifecycle_check(self) -> Dict[str, Any]:
        """Ежедневная проверка жизненного цикла"""
        logger.info("🌅 Запуск ежедневной проверки жизненного цикла...")
        
        start_time = datetime.now()
        
        # 1. Проверяем автоматические переходы
        transitions_result = await self.check_auto_transitions()
        
        # 2. Генерируем аналитику
        analytics = await self.get_lifecycle_analytics()
        
        # 3. Создаем отчет
        report = await self.generate_lifecycle_report()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "success": True,
            "execution_time": execution_time,
            "transitions": transitions_result,
            "analytics": analytics,
            "report": report
        }
        
        logger.info(f"✅ Ежедневная проверка завершена за {execution_time:.2f}с")
        return result

# Функция для запуска из командной строки
async def main():
    """Основная функция для запуска менеджера жизненного цикла"""
    manager = ProductLifecycleManager()
    
    # Запускаем ежедневную проверку
    result = await manager.run_daily_lifecycle_check()
    
    print("🎯 РЕЗУЛЬТАТ ПРОВЕРКИ ЖИЗНЕННОГО ЦИКЛА:")
    print(f"⏱️ Время выполнения: {result['execution_time']:.2f}с")
    print(f"🔄 Переходов выполнено: {len(result['transitions']['transitions_made'])}")
    print(f"⚠️ Просрочено продуктов: {len(result['transitions']['overdue_products'])}")
    print(f"📊 Всего продуктов: {result['analytics']['total_products']}")
    
    # Показываем распределение по статусам
    print("\n📈 РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ:")
    for status, count in result['analytics']['status_distribution'].items():
        print(f"  {status}: {count}")
    
    # Показываем рекомендации
    if result['report']['recommendations']:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        for rec in result['report']['recommendations']:
            print(f"  {rec}")

if __name__ == "__main__":
    asyncio.run(main()) 