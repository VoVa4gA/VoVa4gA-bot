from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os

# Получаем токен из переменных окружения
TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8080))

# === ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ АНЕКДОТОВ ИЗ ИНТЕРНЕТА ===
async def get_joke_from_anekdot_ru():
    """Получает анекдот с сайта anekdot.ru"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with session.get('https://www.anekdot.ru/random/anekdot/', headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    jokes_divs = soup.find_all('div', class_='text')
                    if jokes_divs:
                        joke = jokes_divs[0].get_text().strip()
                        if joke and len(joke) > 10 and len(joke) < 1000 and 'anekdot.ru' not in joke.lower():
                            return joke
    except Exception as e:
        print(f"Ошибка при получении анекдота с anekdot.ru: {e}")
    return None

async def get_joke_from_backup_list():
    """Резервный список анекдотов"""
    backup_jokes = [
        "Почему программисты предпочитают темные режимы? Потому что свет от экрана лучше сочетается с кофе!",
        "Что сказал программист жене? 'Ты у меня в сердце, как баг в коде - постоянно на мысли!'",
        "Почему программисты не ходят в лес? Там слишком много багов!",
        "Что общего у программиста и шамана? Оба говорят с невидимыми сущностями и оба это называют 'дебаг'!",
        "Почему программисты не любят ходить на рыбалку? Потому что лучше ловить баги, чем рыб!",
        "Что делает программист на свидании? Пытается найти общий язык... и общий баг!",
        "Почему программисты всегда спокойны? Потому что знают: если что-то не работает, это можно перезапустить!",
        "Что сказал программист, когда его уволили? 'Ну что ж, теперь я точно свободный open source разработчик!'"
    ]
    return random.choice(backup_jokes)

async def get_random_joke_from_internet():
    """Получает случайный анекдот из интернета"""
    try:
        joke = await get_joke_from_anekdot_ru()
        if joke:
            return joke
    except Exception as e:
        print(f"Ошибка при получении анекдота из интернета: {e}")
    return await get_joke_from_backup_list()

# === ФУНКЦИИ КОМАНД ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name or "друг"
    welcome_text = f"""
Привет, {user_name}! 👋 
Я твой новый веселый бот! 

Могу рассказать анекдот, поговорить о погоде, времени или просто поболтать. 
Выбери, что тебе интересно:
"""
    
    keyboard = [['Анекдот', 'Время'], ['Погода', 'Помощь']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 Меня зовут Вова-бот! 

Вот что я умею:
🔹 /start - Начать общение со мной
🔹 /help - Показать эту помощь
🔹 /time - Узнать текущее время
🔹 /joke - Рассказать анекдот

Или просто нажимай на кнопки:
🔘 Анекдот - расскажу шутку
🔘 Время - скажу который час
🔘 Погода - поговорим о погоде
🔘 Помощь - покажу это сообщение

Можно просто писать мне обычные сообщения - я люблю болтать! 😊
"""
    await update.message.reply_text(help_text)

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_responses = [
        f"Сейчас {current_time}. Время летит незаметно!",
        f"Точное время: {current_time}. Не опаздывай никуда!",
        f"По моим часам сейчас {current_time}. Время для разговора!",
        f"Время: {current_time}. Идеальное время для анекдота!"
    ]
    await update.message.reply_text(random.choice(time_responses))

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /joke - выдаёт случайный анекдот"""
    await update.message.reply_text("Секундочку, ищу свежий анекдот в интернете... 🌐")
    
    try:
        joke = await get_random_joke_from_internet()
        await update.message.reply_text(f"Вот анекдот, который я нашел:\n\n{joke}")
    except Exception as e:
        backup_jokes = [
            "Интернет медленный, но я нашел анекдот для вас: Почему программисты не любят ходить в лес? Потому что там много багов!",
            "Сайт с анекдотами временно недоступен, но вот вам шутка: Что сказал программист, когда его уволили? Ну, теперь я точно свободный фрилансер!",
            "Не удалось загрузить анекдот из интернета, но вот вам загадка: Что общего между ботом и кофе? Оба работают 24/7!"
        ]
        await update.message.reply_text(random.choice(backup_jokes))

# === ФУНКЦИИ ДЛЯ РАЗГОВОРА ===
async def handle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка приветствий"""
    user_name = update.message.from_user.first_name or "друг"
    greetings_responses = [
        f"Привет, {user_name}! Рад тебя видеть! 😊",
        f"Здравствуй, {user_name}! Как дела?",
        f"Приветики! {user_name}, как настроение?",
        f"Хэллоу, {user_name}! Что нового?",
        f"Привет-привет! {user_name}, рад общению с тобой!",
        f"Здравия желаю, {user_name}! Готов поболтать?"
    ]
    await update.message.reply_text(random.choice(greetings_responses))

async def handle_farewells(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка прощаний"""
    user_name = update.message.from_user.first_name or "друг"
    farewells_responses = [
        f"Пока, {user_name}! Возвращайся скорее! 👋",
        f"До скорой встречи, {user_name}! Было приятно пообщаться!",
        f"Прощай, {user_name}! Удачи тебе!",
        f"До свидания, {user_name}! Хорошего дня!",
        f"Пока-пока, {user_name}! Жду тебя снова!",
        f"Удачи, {user_name}! Не забывай улыбаться!"
    ]
    await update.message.reply_text(random.choice(farewells_responses))

async def handle_how_are_you(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка вопросов о самочувствии"""
    how_are_you_responses = [
        "У меня отлично! Работаю, общаюсь, радую людей анекдотами 😊",
        "Все хорошо, спасибо! А у тебя как дела?",
        "Отлично! Люблю общаться с новыми друзьями!",
        "Прекрасно! Готов рассказать анекдот или поговорить о погоде!",
        "Супер! А ты как?",
        "Отлично, как и всегда! Рад, что ты спросил!"
    ]
    await update.message.reply_text(random.choice(how_are_you_responses))

async def handle_weather_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Общение о погоде"""
    weather_responses = [
        "Погода сегодня замечательная для разговора! 🌤️",
        "Не знаю, какая там погода у тебя, но у меня в серверной комнате всегда тепло! 😊",
        "Погода - это тема для бесконечных разговоров! У тебя какая погода?",
        "Люблю, когда солнечно - так интереснее болтать!",
        "Погода может быть разной, но хорошее настроение всегда в моде!",
        "У меня в базе данных есть информация о погоде во всех городах мира!"
    ]
    await update.message.reply_text(random.choice(weather_responses))

# === ОБРАБОТЧИКИ СООБЩЕНИЙ ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_name = update.message.from_user.first_name or "друг"
    
    # Обработка кнопок
    if text == 'анекдот':
        await update.message.reply_text("Секундочку, ищу свежий анекдот в интернете... 🌐")
        try:
            joke = await get_random_joke_from_internet()
            await update.message.reply_text(f"Вот анекдот, который я нашел:\n\n{joke}")
        except Exception as e:
            backup_jokes = [
                "Интернет медленный, но я нашел анекдот для вас: Почему программисты не любят ходить в лес? Потому что там много багов!",
                "Сайт с анекдотами временно недоступен, но вот вам шутка: Что сказал программист, когда его уволили? Ну, теперь я точно свободный фрилансер!",
                "Не удалось загрузить анекдот из интернета, но вот вам загадка: Что общего между ботом и кофе? Оба работают 24/7!"
            ]
            await update.message.reply_text(random.choice(backup_jokes))
        
    elif text == 'время':
        await time_command(update, context)
        
    elif text == 'погода':
        await handle_weather_talk(update, context)
        
    elif text == 'помощь':
        await help_command(update, context)
        
    else:
        # Интеллектуальный анализ текста
        if any(word in text for word in ['привет', 'здравствуй', 'хай', 'hello', 'hi']):
            await handle_greetings(update, context)
            
        elif any(word in text for word in ['пока', 'до свидания', 'прощай', 'удачи', 'bye']):
            await handle_farewells(update, context)
            
        elif any(word in text for word in ['как дела', 'как ты', 'что нового', 'как жизнь']):
            await handle_how_are_you(update, context)
            
        elif any(word in text for word in ['погода', 'холодно', 'тепло', 'дождь', 'солнце']):
            await handle_weather_talk(update, context)
            
        elif any(word in text for word in ['анекдот', 'шутк', 'пошути', 'смешн']):
            await update.message.reply_text("Секундочку, ищу свежий анекдот в интернете... 🌐")
            try:
                joke = await get_random_joke_from_internet()
                await update.message.reply_text(f"Вот анекдот, который я нашел:\n\n{joke}")
            except Exception as e:
                backup_jokes = [
                    "Интернет медленный, но я нашел анекдот для вас: Почему программисты не любят ходить в лес? Потому что там много багов!",
                    "Сайт с анекдотами временно недоступен, но вот вам шутка: Что сказал программист, когда его уволили? Ну, теперь я точно свободный фрилансер!",
                    "Не удалось загрузить анекдот из интернета, но вот вам загадка: Что общего между ботом и кофе? Оба работают 24/7!"
                ]
                await update.message.reply_text(random.choice(backup_jokes))
            
        elif any(word in text for word in ['время', 'который час', 'часы']):
            await time_command(update, context)
            
        elif any(word in text for word in ['спасибо', 'благодарю', 'мерси', 'thanks']):
            thanks_responses = [
                "Пожалуйста! 😊",
                "Всегда рад помочь!",
                f"Не за что, {user_name}!",
                "Обращайся!",
                "Рад был помочь!"
            ]
            await update.message.reply_text(random.choice(thanks_responses))
            
        elif any(word in text for word in ['имя', 'зовут', 'тебя']):
            await update.message.reply_text("Меня зовут Вова-бот! Приятно с тобой общаться! 😊")
            
        else:
            # Стандартные ответы на разные темы
            general_responses = [
                f"Интересно, {user_name}! Расскажи мне больше об этом!",
                "Звучит занимательно! А что еще ты можешь рассказать?",
                f"{user_name}, ты такой интересный собеседник!",
                "Очень познавательно! Продолжай!",
                "Как здорово, что мы можем поговорить об этом!",
                f"{user_name}, ты заставил меня задуматься!",
                "Удивительная история! Спасибо, что поделился!",
                "Ты знаешь, мне нравится, как ты рассказываешь!"
            ]
            await update.message.reply_text(random.choice(general_responses))

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    print("Запуск бота на веб-сервере...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('time', time_command))
    app.add_handler(CommandHandler('joke', joke_command))
    
    # Добавляем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    
    print('Бот запущен и работает...')
    
    # Запускаем вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://ваш-домен.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    main()
