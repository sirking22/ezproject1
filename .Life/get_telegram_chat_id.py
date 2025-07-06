#!/usr/bin/env python3
"""
📱 ПОЛУЧЕНИЕ TELEGRAM CHAT ID
"""

import os
import requests
import time
from dotenv import load_dotenv

def get_telegram_chat_id():
    """Получает Chat ID из Telegram бота"""
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return None
    
    print("🔍 Получение Chat ID...")
    print("📱 Отправь любое сообщение боту @dotLife_bot")
    print("⏳ Ожидание сообщения...")
    
    # Ждем сообщения с таймаутом
    for attempt in range(10):
        try:
            # Получаем обновления
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok") and data.get("result"):
                    updates = data["result"]
                    
                    if updates:
                        # Берем последнее сообщение
                        latest_update = updates[-1]
                        
                        if "message" in latest_update:
                            chat = latest_update["message"]["chat"]
                            chat_id = chat["id"]
                            chat_type = chat["type"]
                            user_name = chat.get("first_name", "Unknown")
                            
                            print(f"✅ Chat ID найден!")
                            print(f"👤 Пользователь: {user_name}")
                            print(f"💬 Тип чата: {chat_type}")
                            print(f"🆔 Chat ID: {chat_id}")
                            
                            # Обновляем .env файл
                            update_env_file(chat_id)
                            
                            return chat_id
                        else:
                            print(f"⏳ Попытка {attempt + 1}/10: сообщения не найдены")
                    else:
                        print(f"⏳ Попытка {attempt + 1}/10: обновления не найдены")
                else:
                    print(f"❌ Ошибка API: {data.get('description', 'Unknown')}")
                    break
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            break
        
        # Ждем 3 секунды перед следующей попыткой
        if attempt < 9:
            print("⏳ Ждем 3 секунды...")
            time.sleep(3)
    
    print("❌ Chat ID не найден")
    print("📱 Убедись, что ты отправил сообщение боту @dotLife_bot")
    return None

def update_env_file(chat_id):
    """Обновляет .env файл с Chat ID"""
    try:
        # Читаем текущий .env
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Ищем строку с TELEGRAM_CHAT_ID
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("TELEGRAM_CHAT_ID="):
                lines[i] = f"TELEGRAM_CHAT_ID={chat_id}\n"
                updated = True
                break
        
        # Если не нашли, добавляем
        if not updated:
            lines.append(f"TELEGRAM_CHAT_ID={chat_id}\n")
        
        # Записываем обратно
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        print("✅ .env файл обновлен")
        
    except Exception as e:
        print(f"❌ Ошибка обновления .env: {e}")
        print(f"📝 Добавь вручную в .env: TELEGRAM_CHAT_ID={chat_id}")

def test_telegram_send():
    """Тестирует отправку сообщения"""
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Токен или Chat ID не настроены")
        return False
    
    try:
        message = "🧪 Тестовая отправка от Quick Voice Assistant"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Тестовое сообщение отправлено!")
                return True
            else:
                print(f"❌ Ошибка отправки: {result.get('description')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    
    return False

def send_test_message():
    """Отправляет тестовое сообщение для проверки"""
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return False
    
    try:
        # Сначала получаем информацию о боте
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_data = response.json()
            if bot_data.get("ok"):
                bot_info = bot_data["result"]
                username = bot_info.get("username")
                print(f"🤖 Бот найден: @{username}")
                print(f"📱 Отправь сообщение боту @{username}")
                return True
        else:
            print(f"❌ Ошибка получения информации о боте: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return False

def main():
    """Основная функция"""
    print("📱" + "="*50)
    print("🎯 ПОЛУЧЕНИЕ TELEGRAM CHAT ID")
    print("="*52)
    
    # Проверяем текущий Chat ID
    load_dotenv()
    current_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if current_chat_id:
        print(f"📋 Текущий Chat ID: {current_chat_id}")
        
        # Тестируем отправку
        print("\n🧪 Тестирование отправки...")
        if test_telegram_send():
            print("✅ Chat ID работает корректно!")
            return
        else:
            print("❌ Chat ID не работает, получаем новый...")
    
    # Проверяем бота
    print("\n🔍 Проверка бота...")
    if not send_test_message():
        print("❌ Проблема с ботом")
        return
    
    # Получаем новый Chat ID
    chat_id = get_telegram_chat_id()
    
    if chat_id:
        print("\n🧪 Тестирование нового Chat ID...")
        test_telegram_send()
    
    print("\n📋 Следующие шаги:")
    print("1. Запусти: python setup_real_services.py")
    print("2. Протестируй полную интеграцию")
    print("3. Установи приложение на часы")

if __name__ == "__main__":
    main() 