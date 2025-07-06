#!/usr/bin/env python3
"""
Система учета исполнителей Notion
Автоматическое использование во всех скриптах
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Assignee:
    """Информация об исполнителе"""
    name: str
    role: str
    notion_id: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    is_designer: bool = True
    is_active: bool = True
    last_updated: Optional[datetime] = None

class AssigneesRegistry:
    """Реестр исполнителей Notion"""
    
    def __init__(self):
        self.assignees: Dict[str, Assignee] = {}
        self._load_default_assignees()
    
    def _load_default_assignees(self):
        """Загрузка исполнителей по умолчанию"""
        default_assignees = [
            Assignee(
                name="Arsentiy",
                role="арт-директор",
                is_designer=True,
                is_active=True
            ),
            Assignee(
                name="Анна Когут",
                role="дизайнер",
                notion_id="46239144-3373-45cb-9cdd-b9157fc950b3",
                email="a.n.n.69.m.a.y@gmail.com",
                is_designer=True,
                is_active=True
            ),
            Assignee(
                name="Мария Безродная",
                role="дизайнер",
                notion_id="96461d82-0b5b-4460-b129-c733a814586a",
                email="masha.bezrodnaia@gmail.com",
                is_designer=True,
                is_active=True
            ),
            Assignee(
                name="Account",
                role="аккаунт",
                is_designer=False,
                is_active=True
            )
        ]
        
        for assignee in default_assignees:
            self.add_assignee(assignee)
    
    def add_assignee(self, assignee: Assignee):
        """Добавление исполнителя"""
        self.assignees[assignee.name] = assignee
    
    def get_assignee(self, name: str) -> Optional[Assignee]:
        """Получение исполнителя по имени"""
        return self.assignees.get(name)
    
    def get_all_designers(self) -> List[Assignee]:
        """Получение всех дизайнеров"""
        return [a for a in self.assignees.values() if a.is_designer and a.is_active]
    
    def get_all_active(self) -> List[Assignee]:
        """Получение всех активных исполнителей"""
        return [a for a in self.assignees.values() if a.is_active]
    
    def get_assignee_names(self) -> List[str]:
        """Получение списка имен исполнителей"""
        return list(self.assignees.keys())
    
    def get_designer_names(self) -> List[str]:
        """Получение списка имен дизайнеров"""
        return [a.name for a in self.get_all_designers()]
    
    def is_designer(self, name: str) -> bool:
        """Проверка, является ли исполнитель дизайнером"""
        assignee = self.get_assignee(name)
        return assignee.is_designer if assignee else False
    
    def is_known_assignee(self, name: str) -> bool:
        """Проверка, известен ли исполнитель"""
        return name in self.assignees
    
    def update_from_notion_data(self, notion_assignees: List[Dict]):
        """Обновление данных из Notion"""
        for person in notion_assignees:
            if "name" in person:
                name = person["name"]
                existing = self.get_assignee(name)
                
                if existing:
                    # Обновляем существующего
                    if "id" in person:
                        existing.notion_id = person["id"]
                    if "avatar_url" in person:
                        existing.avatar_url = person["avatar_url"]
                    if "person" in person and "email" in person["person"]:
                        existing.email = person["person"]["email"]
                    existing.last_updated = datetime.now()
                else:
                    # Создаем нового
                    new_assignee = Assignee(
                        name=name,
                        role="неизвестно",
                        notion_id=person.get("id"),
                        avatar_url=person.get("avatar_url"),
                        email=person.get("person", {}).get("email"),
                        is_designer=True,  # По умолчанию считаем дизайнером
                        is_active=True,
                        last_updated=datetime.now()
                    )
                    self.add_assignee(new_assignee)
    
    def get_unknown_assignees(self, found_names: Set[str]) -> List[str]:
        """Получение неизвестных исполнителей"""
        known_names = set(self.assignees.keys())
        return list(found_names - known_names)
    
    def print_summary(self):
        """Вывод сводки по исполнителям"""
        print("\n👥 РЕЕСТР ИСПОЛНИТЕЛЕЙ")
        print("=" * 50)
        
        designers = self.get_all_designers()
        others = [a for a in self.assignees.values() if not a.is_designer]
        
        print(f"🎨 Дизайнеры ({len(designers)}):")
        for designer in designers:
            status = "✅" if designer.is_active else "❌"
            print(f"  {status} {designer.name} - {designer.role}")
            if designer.notion_id:
                print(f"    ID: {designer.notion_id}")
        
        if others:
            print(f"\n👤 Остальные ({len(others)}):")
            for other in others:
                status = "✅" if other.is_active else "❌"
                print(f"  {status} {other.name} - {other.role}")
        
        print(f"\n📊 Всего исполнителей: {len(self.assignees)}")
        print(f"📊 Активных дизайнеров: {len(designers)}")

# Глобальный экземпляр реестра
assignees_registry = AssigneesRegistry()

def get_assignees_registry() -> AssigneesRegistry:
    """Получение глобального реестра исполнителей"""
    return assignees_registry

def is_known_designer(name: str) -> bool:
    """Быстрая проверка, является ли известным дизайнером"""
    return assignees_registry.is_designer(name)

def get_all_designer_names() -> List[str]:
    """Быстрое получение всех имен дизайнеров"""
    return assignees_registry.get_designer_names()

def update_assignees_from_notion(notion_assignees: List[Dict]):
    """Обновление исполнителей из данных Notion"""
    assignees_registry.update_from_notion_data(notion_assignees)

if __name__ == "__main__":
    # Тестирование реестра
    registry = get_assignees_registry()
    registry.print_summary()
    
    print(f"\n🔍 ТЕСТЫ:")
    print(f"Arsentiy - дизайнер: {is_known_designer('Arsentiy')}")
    print(f"Account - дизайнер: {is_known_designer('Account')}")
    print(f"Неизвестный - известен: {registry.is_known_assignee('Неизвестный')}")
    
    print(f"\n📋 Все дизайнеры: {get_all_designer_names()}") 