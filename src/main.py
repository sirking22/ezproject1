"""Main entry point for the Telegram bot."""
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared_code')))

from integrations.notion import NotionClient
from integrations.yandex_cloud import YandexCloudClient
from utils.logging_utils import get_logger

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout
)

logger = get_logger("life_bot")

# Load settings
settings = Settings(
    TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
    OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", "")
)

notion = NotionClient()
yandex = YandexCloudClient()

def main() -> None:
    """Start the bot."""
    try:
        # Validate required settings
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set")
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")
            
        # Create and run bot
        bot = TelegramBot(settings)
        logger.info("Starting bot...")
        bot.run()
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Пример использования клиентов
    logger.info("Notion и YandexCloud клиенты инициализированы.")
    # Здесь должен быть запуск твоего life_bot