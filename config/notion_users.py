# Реестр гостевых пользователей и их идентификаторов
GUEST_USERS = {
    "Александр Трусов": {
        "id": None,  # Будет заполнено после получения ID
        "email": "1902altrusov@gmail.com",
        "role": "guest",
        "name_variants": ["Александр", "Саша", "Alex"]
    },
    "Анна Когут": {
        "id": None,
        "email": "a.n.n.69.m.a.y@gmail.com",
        "role": "guest",
        "name_variants": ["Анна", "Аня", "Anna"]
    },
    "Виктория Владимировна": {
        "id": None,
        "email": "vivi.ka.lvov@gmail.com",
        "role": "guest",
        "name_variants": ["Виктория", "Вика", "Victoria"]
    },
    "Мария Безродная": {
        "id": None,
        "email": "masha.bezrodnaia@gmail.com",
        "role": "guest",
        "name_variants": ["Мария", "Маша", "Maria"]
    },
    "Arsentiy": {
        "id": None,
        "email": "ezmail2222@gmail.com",
        "role": "guest",
        "name_variants": ["Арсений", "Арсентий", "Арсен", "Arseniy", "Arseny", "Arsen"]
    }
}

# Функция для получения информации о госте по имени
def get_guest_by_name(name: str, check_variants: bool = False) -> dict:
    """
    Получить информацию о госте по имени
    Args:
        name: Имя гостя
        check_variants: Проверять ли варианты имени
    Returns:
        dict: Информация о госте или None, если не найден
    """
    # Сначала проверяем точное совпадение
    if name in GUEST_USERS:
        return GUEST_USERS[name]
    
    # Если нужно, проверяем варианты имени
    if check_variants:
        name_lower = name.lower()
        for guest_name, guest_info in GUEST_USERS.items():
            # Проверяем основное имя
            if guest_name.lower() == name_lower:
                return guest_info
            # Проверяем варианты имени
            if any(variant.lower() == name_lower for variant in guest_info.get("name_variants", [])):
                return guest_info
    
    return None

# Функция для получения всех вариантов имени гостя
def get_guest_name_variants(name: str) -> list:
    """
    Получить все варианты имени гостя
    Args:
        name: Основное имя гостя
    Returns:
        list: Список всех вариантов имени или пустой список, если гость не найден
    """
    guest = get_guest_by_name(name)
    if guest:
        variants = [name]  # Добавляем основное имя
        variants.extend(guest.get("name_variants", []))
        return variants
    return []

# Функция для получения информации о госте по email
def get_guest_by_email(email: str) -> dict:
    """
    Получить информацию о госте по email
    Args:
        email: Email гостя
    Returns:
        dict: Информация о госте или None, если не найден
    """
    for user in GUEST_USERS.values():
        if user["email"].lower() == email.lower():
            return user
    return None

# Функция для обновления ID гостя
def update_guest_id(name: str, user_id: str) -> bool:
    """
    Обновить ID гостя
    Args:
        name: Имя гостя
        user_id: Notion User ID
    Returns:
        bool: True если обновление успешно, False если гость не найден
    """
    if name in GUEST_USERS:
        GUEST_USERS[name]["id"] = user_id
        return True
    return False

def sync_guest_uuids_from_tasks(server, tasks_db_id):
    """Автоматически обновляет UUID всех гостей из задач Notion"""
    import asyncio
    filter_dict = {
        "property": "Участники",
        "people": {"is_not_empty": True}
    }
    async def _sync():
        tasks = await server.get_pages(tasks_db_id, filter_dict)
        found = set()
        for task in tasks:
            properties = task.get('properties', {})
            participants = properties.get('Участники', {})
            people = participants.get('people', []) if isinstance(participants, dict) else []
            for person in people:
                name = person.get('name', '')
                user_id = person.get('id')
                guest = get_guest_by_name(name, check_variants=True)
                if guest and (not guest['id'] or guest['id'] != user_id):
                    guest['id'] = user_id
                    found.add(name)
        if found:
            print(f"Обновлены UUID для: {', '.join(found)}")
        else:
            print("UUID гостей актуальны.")
    asyncio.run(_sync()) 