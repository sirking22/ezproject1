#!/usr/bin/env python3
"""
Аудит всех гостей в системе Notion
Выявляет проблемы с доступом к данным через API
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class GuestUser:
    """Информация о госте в системе"""
    name: str
    email: Optional[str]
    role: str
    databases: List[str]
    tasks_count: int = 0
    subtasks_count: int = 0
    status: str = "guest"
    uuid: Optional[str] = None

class NotionGuestAuditor:
    """Аудитор гостей в системе Notion"""
    
    def __init__(self):
        """Инициализация аудитора"""
        self.guests: Dict[str, GuestUser] = {}
        
        # Критические базы для проверки
        self.critical_databases = {
            "tasks": "d09df250ce7e4e0d9fbe4e036d320def",
            "subtasks": "9c5f4269d61449b6a7485579a3c21da3",
            "projects": "342f18c67a5e41fead73dcec00770f4e",
            "materials": "1d9ace03d9ff804191a4d35aeedcbbd4"
        }
        
        # Известные гости (из предыдущего анализа)
        self.known_guests = {
            "arsentiy": {
                "name": "Арсентий",
                "role": "Арт-директор",
                "email": None
            }
        }
    
    def audit_all_guests(self) -> Dict[str, GuestUser]:
        """Полный аудит всех гостей в системе"""
        logger.info("🔍 Начинаем полный аудит гостей в системе Notion")
        
        # 1. Проверяем известных гостей
        for guest_id, guest_info in self.known_guests.items():
            self._audit_known_guest(guest_id, guest_info)
        
        # 2. Генерируем отчет
        self._generate_report()
        
        return self.guests
    
    def _audit_known_guest(self, guest_id: str, guest_info: Dict):
        """Аудит известного гостя"""
        logger.info(f"🔍 Аудит известного гостя: {guest_info['name']}")
        
        # Создаем объект гостя
        guest = GuestUser(
            name=guest_info["name"],
            email=guest_info.get("email"),
            role=guest_info["role"],
            databases=[],
            status="guest"  # По умолчанию гость
        )
        
        # Подсчитываем задачи (используем MCP)
        guest.tasks_count = self._count_tasks_for_user_mcp(guest_info["name"])
        guest.subtasks_count = self._count_subtasks_for_user_mcp(guest_info["name"])
        
        # Определяем базы данных
        if guest.tasks_count > 0:
            guest.databases.append("tasks")
        if guest.subtasks_count > 0:
            guest.databases.append("subtasks")
        
        self.guests[guest_id] = guest
        
        logger.info(f"📊 {guest.name}: {guest.tasks_count} задач, {guest.subtasks_count} подзадач, статус: {guest.status}")
    
    def _count_tasks_for_user_mcp(self, user_name: str) -> int:
        """Подсчитываем задачи для пользователя через MCP"""
        try:
            # Используем MCP для подсчета задач
            import subprocess
            import json
            
            # Создаем временный скрипт для MCP
            mcp_script = f"""
import sys
sys.path.append('.')

from notion_mcp_server import NotionMCPServer

server = NotionMCPServer()
result = server.query_database(
    database_id="d09df250ce7e4e0d9fbe4e036d320def",
    filter_condition={{
        "property": "Участники",
        "people": {{
            "contains": "{user_name}"
        }}
    }}
)

print(len(result.get("results", [])))
"""
            
            # Запускаем скрипт
            result = subprocess.run(
                [sys.executable, "-c", mcp_script],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                return int(result.stdout.strip())
            else:
                logger.error(f"Ошибка MCP для {user_name}: {result.stderr}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка при подсчете задач для {user_name}: {e}")
            return 0
    
    def _count_subtasks_for_user_mcp(self, user_name: str) -> int:
        """Подсчитываем подзадачи для пользователя через MCP"""
        try:
            # Используем MCP для подсчета подзадач
            import subprocess
            import json
            
            # Создаем временный скрипт для MCP
            mcp_script = f"""
import sys
sys.path.append('.')

from notion_mcp_server import NotionMCPServer

server = NotionMCPServer()
result = server.query_database(
    database_id="9c5f4269d61449b6a7485579a3c21da3",
    filter_condition={{
        "property": "Исполнитель",
        "people": {{
            "contains": "{user_name}"
        }}
    }}
)

print(len(result.get("results", [])))
"""
            
            # Запускаем скрипт
            result = subprocess.run(
                [sys.executable, "-c", mcp_script],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                return int(result.stdout.strip())
            else:
                logger.error(f"Ошибка MCP для {user_name}: {result.stderr}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка при подсчете подзадач для {user_name}: {e}")
            return 0
    
    def _generate_report(self):
        """Генерируем отчет по аудиту"""
        logger.info("📊 ГЕНЕРАЦИЯ ОТЧЕТА ПО АУДИТУ ГОСТЕЙ")
        
        total_guests = len(self.guests)
        full_users = sum(1 for g in self.guests.values() if g.status == "full_user")
        guests_only = sum(1 for g in self.guests.values() if g.status == "guest")
        
        logger.info(f"📈 ОБЩАЯ СТАТИСТИКА:")
        logger.info(f"   Всего пользователей: {total_guests}")
        logger.info(f"   Полных пользователей: {full_users}")
        logger.info(f"   Только гостей: {guests_only}")
        
        # Детальный отчет по каждому гостю
        logger.info(f"🔍 ДЕТАЛЬНЫЙ ОТЧЕТ:")
        for guest_id, guest in self.guests.items():
            logger.info(f"   {guest.name} ({guest.role}):")
            logger.info(f"     Статус: {guest.status}")
            logger.info(f"     Задачи: {guest.tasks_count}")
            logger.info(f"     Подзадачи: {guest.subtasks_count}")
            logger.info(f"     Базы: {', '.join(guest.databases)}")
            logger.info(f"     UUID: {guest.uuid or 'НЕ НАЙДЕН'}")
        
        # Сохраняем отчет в файл
        self._save_report_to_file()
    
    def _save_report_to_file(self):
        """Сохраняем отчет в файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"reports/notion_guests_audit_{timestamp}.md"
        
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Аудит гостей Notion - {timestamp}\n\n")
            
            f.write("## Общая статистика\n")
            total_guests = len(self.guests)
            full_users = sum(1 for g in self.guests.values() if g.status == "full_user")
            guests_only = sum(1 for g in self.guests.values() if g.status == "guest")
            
            f.write(f"- Всего пользователей: {total_guests}\n")
            f.write(f"- Полных пользователей: {full_users}\n")
            f.write(f"- Только гостей: {guests_only}\n\n")
            
            f.write("## Детальный отчет\n\n")
            for guest_id, guest in self.guests.items():
                f.write(f"### {guest.name}\n")
                f.write(f"- **Роль**: {guest.role}\n")
                f.write(f"- **Статус**: {guest.status}\n")
                f.write(f"- **Email**: {guest.email or 'Не указан'}\n")
                f.write(f"- **Задачи**: {guest.tasks_count}\n")
                f.write(f"- **Подзадачи**: {guest.subtasks_count}\n")
                f.write(f"- **Базы данных**: {', '.join(guest.databases)}\n")
                f.write(f"- **UUID**: {guest.uuid or 'Не найден'}\n\n")
            
            f.write("## Рекомендации\n\n")
            if guests_only > 0:
                f.write("### Критические действия:\n")
                f.write("1. Пригласить всех гостей в команду Notion\n")
                f.write("2. Настроить права доступа для каждого гостя\n")
                f.write("3. Протестировать API доступ после миграции\n")
                f.write("4. Обновить все скрипты для работы с новыми UUID\n\n")
            
            f.write("### Долгосрочные меры:\n")
            f.write("1. Создать систему автоматического управления пользователями\n")
            f.write("2. Реализовать мониторинг новых гостей\n")
            f.write("3. Настроить автоматические уведомления о новых гостях\n")
        
        logger.info(f"💾 Отчет сохранен в файл: {filename}")

def main():
    """Основная функция"""
    logger.info("🚀 Запуск аудита гостей Notion")
    
    try:
        auditor = NotionGuestAuditor()
        guests = auditor.audit_all_guests()
        
        logger.info("✅ Аудит завершен успешно")
        return guests
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при аудите: {e}")
        return {}

if __name__ == "__main__":
    main() 