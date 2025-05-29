import os
import logging
import requests
from dotenv import load_dotenv  # Явный импорт
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
try:
    load_dotenv()  # Загружаем из файла .env в той же директории
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    OMDB_KEY = os.getenv('OMDB_API_KEY')
    
    if not TOKEN or not OMDB_KEY:
        raise ValueError("Не найдены необходимые переменные в .env файле!")
except Exception as e:
    logger.error(f"Ошибка загрузки .env: {e}")
    raise

def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    buttons = [
        [InlineKeyboardButton("🎬 Найти фильм", callback_data="search_movie")],
        [InlineKeyboardButton("📚 Найти книгу", callback_data="search_book")],
    ]
    update.message.reply_text(
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def button_handler(update: Update, context: CallbackContext):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    query.answer()
    
    if query.data == "search_movie":
        query.edit_message_text("Введите название фильма:")
        context.user_data["mode"] = "movie"
    elif query.data == "search_book":
        query.edit_message_text("Введите название книги:")
        context.user_data["mode"] = "book"

def search_movie(update: Update, context: CallbackContext):
    """Поиск фильма через OMDB API"""
    query = update.message.text
    
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_KEY}&t={query}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("Response") == "True":
            message = (
                f"🎬 {data['Title']} ({data['Year']})\n"
                f"⭐ Рейтинг: {data['imdbRating']}/10\n"
                f"📖 Сюжет: {data['Plot']}\n"
                f"🎭 Жанр: {data['Genre']}"
            )
            update.message.reply_text(message)
        else:
            update.message.reply_text("Фильм не найден. Попробуйте другое название.")
            
    except Exception as e:
        logger.error(f"Ошибка поиска фильма: {e}")
        update.message.reply_text("Произошла ошибка при поиске.")

def main():
    """Запуск бота"""
    try:
        updater = Updater(TOKEN)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CallbackQueryHandler(button_handler))
        dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

        logger.info("Бот запущен")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()