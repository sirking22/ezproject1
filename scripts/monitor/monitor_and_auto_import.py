#!/usr/bin/env python3
"""
Автоматический мониторинг и запуск импорта в Notion
Следит за загрузкой файлов на Яндекс.Диск и автоматически запускает импорт в Notion
"""

import os
import time
import asyncio
import subprocess
import yadisk
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoImportMonitor:
    """Автоматический мониторинг и импорт"""
    
    def __init__(self):
        self.target_folder = "/TelegramImport_20250621_025209"
        self.expected_groups = 282  # Групп с файлами
        self.expected_files = 599   # Всего файлов
        self.groups_file = "telegram_groups_20250621_024246.json"
        
        # Инициализируем Яндекс.Диск
        ya_token = os.getenv('YA_ACCESS_TOKEN')
        self.yadisk = yadisk.YaDisk(token=ya_token) if ya_token else None
        
        if self.yadisk and self.yadisk.check_token():
            logger.info("✅ Подключение к Яндекс.Диску установлено")
        else:
            logger.error("❌ Не удалось подключиться к Яндекс.Диску")
    
    def check_upload_progress(self):
        """Проверяет прогресс загрузки файлов"""
        if not self.yadisk:
            return None
        
        try:
            total_files = 0
            total_groups = 0
            recent_activity = False
            current_time = datetime.now()
            
            for item in self.yadisk.listdir(self.target_folder):
                if item.type == 'dir':
                    total_groups += 1
                    try:
                        group_folder = f"{self.target_folder}/{item.name}"
                        for file_item in self.yadisk.listdir(group_folder):
                            if file_item.type == 'file':
                                total_files += 1
                                
                                # Проверяем недавнюю активность (последние 10 минут)
                                if file_item.modified:
                                    time_diff = current_time - file_item.modified.replace(tzinfo=None)
                                    if time_diff.total_seconds() < 600:  # 10 минут
                                        recent_activity = True
                    except Exception as e:
                        logger.warning(f"Ошибка сканирования папки {item.name}: {e}")
            
            progress_percent = (total_files / self.expected_files * 100) if self.expected_files > 0 else 0
            
            return {
                'total_files': total_files,
                'total_groups': total_groups,
                'progress_percent': progress_percent,
                'recent_activity': recent_activity,
                'is_complete': total_files >= self.expected_files and not recent_activity
            }
            
        except Exception as e:
            logger.error(f"Ошибка проверки прогресса: {e}")
            return None
    
    def run_notion_import(self):
        """Запускает импорт в Notion"""
        try:
            logger.info("🚀 Запускаем автоматический импорт в Notion...")
            
            # Команда для запуска импорта в Notion
            cmd = [
                "python", 
                "notion_only_importer.py",
                self.groups_file,
                self.target_folder
            ]
            
            # Запускаем процесс с автоматическим подтверждением
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            # Отправляем 'y' для подтверждения
            stdout, stderr = process.communicate(input='y\n')
            
            if process.returncode == 0:
                logger.info("✅ Импорт в Notion завершен успешно!")
                logger.info(f"Вывод: {stdout}")
                return True
            else:
                logger.error(f"❌ Ошибка импорта в Notion: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка запуска импорта: {e}")
            return False
    
    async def monitor_and_import(self):
        """Основной цикл мониторинга"""
        logger.info("🔄 Начинаем мониторинг загрузки файлов...")
        logger.info(f"🎯 Ожидаем: {self.expected_files} файлов в {self.expected_groups} группах")
        
        check_interval = 60  # Проверяем каждую минуту
        max_wait_time = 3600  # Максимум 1 час ожидания
        start_time = time.time()
        
        last_file_count = 0
        stable_count = 0  # Счетчик стабильных проверок
        
        while True:
            # Проверяем прогресс
            progress = self.check_upload_progress()
            
            if not progress:
                logger.error("❌ Не удалось проверить прогресс")
                await asyncio.sleep(check_interval)
                continue
            
            current_time = datetime.now().strftime('%H:%M:%S')
            logger.info(f"⏰ {current_time} | 📊 {progress['total_files']}/{self.expected_files} файлов ({progress['progress_percent']:.1f}%) | 📂 {progress['total_groups']} групп")
            
            # Проверяем стабильность (нет новых файлов)
            if progress['total_files'] == last_file_count:
                stable_count += 1
            else:
                stable_count = 0
                last_file_count = progress['total_files']
            
            # Условия для запуска импорта
            should_import = False
            reason = ""
            
            if progress['is_complete']:
                should_import = True
                reason = "Все файлы загружены и нет активности"
            elif stable_count >= 5 and progress['total_files'] > 0:
                should_import = True
                reason = f"Стабильность 5 минут, есть {progress['total_files']} файлов"
            elif time.time() - start_time > max_wait_time:
                should_import = True
                reason = "Превышено время ожидания (1 час)"
            
            if should_import:
                logger.info(f"🎯 Условие выполнено: {reason}")
                logger.info(f"📊 Финальная статистика:")
                logger.info(f"   📄 Файлов загружено: {progress['total_files']}")
                logger.info(f"   📂 Групп обработано: {progress['total_groups']}")
                logger.info(f"   📈 Прогресс: {progress['progress_percent']:.1f}%")
                
                # Запускаем импорт в Notion
                success = self.run_notion_import()
                
                if success:
                    logger.info("🎉 АВТОМАТИЧЕСКИЙ ИМПОРТ ЗАВЕРШЕН УСПЕШНО!")
                else:
                    logger.error("❌ Импорт завершился с ошибками")
                
                break
            
            # Ждем следующую проверку
            await asyncio.sleep(check_interval)
        
        logger.info("🏁 Мониторинг завершен")

async def main():
    """Основная функция"""
    print("🤖 АВТОМАТИЧЕСКИЙ МОНИТОРИНГ И ИМПОРТ")
    print("=" * 50)
    print("🔄 Слежу за загрузкой файлов на Яндекс.Диск")
    print("📝 Автоматически запущу импорт в Notion когда все загрузится")
    print("⏰ Проверка каждую минуту")
    print("🛑 Для остановки нажмите Ctrl+C")
    print()
    
    monitor = AutoImportMonitor()
    
    try:
        await monitor.monitor_and_import()
    except KeyboardInterrupt:
        print("\n⚠️ Мониторинг прерван пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 