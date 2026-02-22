import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ========== НАСТРОЙКИ ==========
API_TOKEN = '8259801608:AAEy-j1LevJ9qYfrItnmcCAjIyrEcg0Eycg'  # Ваш токен

# Словарь для хранения пола пользователей
USER_GENDERS = {}

# ========== ВОПРОСЫ ==========
QUESTIONS = [
    "В чем смысл жизни по-твоему?",
    "Что такое счастье для тебя?",
    "Веришь ли ты в судьбу?",
    "Что бы ты сказала себе через 10 лет?",
    "Что ты хочешь изменить в мире?",
    "Если бы ты была овощем, то каким?",
    "Что бы ты делала, если бы у тебя выросли крылья?",
    "Как бы ты сбежала из тюрьмы с помощью зубной щетки?",
    "Ты когда-нибудь нарушала закон?",
    "Что бы ты сделала, если бы узнала, что осталось жить неделю?",
    "Самая большая ложь, которую ты говорила?",
    "Что бы ты сделала, если бы выиграла миллиард?",
    "Твое любимое блюдо?",
    "Куда хочешь поехать?",
    "Твой любимый фильм?",
    "Чего ты боишься больше всего?",
    "Какая твоя самая большая мечта?",
    "Что такое счастье для тебя?",
    "Ты веришь в любовь с первого взгляда?",
    "Какой твой самый большой страх?",
]

print(f"✅ Загружено вопросов: {len(QUESTIONS)}")

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Принудительный сброс вебхука при запуске
async def reset_webhook():
    await asyncio.sleep(1)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Вебхук сброшен")

asyncio.create_task(reset_webhook())

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(
        "👋 Привет! Я бот для общения!\n\n"
        "Команды:\n"
        "/set_gender male/female - установить пол\n"
        "/stats - статистика\n"
        "/ask - задать случайный вопрос"
    )

@dp.message(Command("set_gender"))
async def set_gender(message: types.Message):
    try:
        gender = message.text.split()[1].lower()
        if gender in ['male', 'female']:
            USER_GENDERS[message.from_user.id] = gender
            text = "✅ Пол установлен: мужской" if gender == 'male' else "✅ Пол установлен: женский"
            await message.reply(text)
        else:
            await message.reply("❌ Используй: /set_gender male или /set_gender female")
    except:
        await message.reply("❌ Используй: /set_gender male или /set_gender female")

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    stats = f"📊 Статистика:\n"
    stats += f"Всего вопросов: {len(QUESTIONS)}\n"
    stats += f"Пользователей с полом: {len(USER_GENDERS)}"
    await message.reply(stats)

@dp.message(Command("ask"))
async def ask_now(message: types.Message):
    """Отправляет случайный вопрос в текущий чат"""
    if not QUESTIONS:
        await message.reply("❌ Вопросы закончились!")
        return
    
    question = random.choice(QUESTIONS)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выполнено", callback_data="done"),
            InlineKeyboardButton(text="❌ Не выполнено", callback_data="fail")
        ]
    ])
    
    await message.reply(
        f"🎯 <b>Вопрос:</b>\n\n{question}",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data in ['done', 'fail'])
async def process_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    gender = USER_GENDERS.get(user_id, "female")
    
    if callback.data == 'done':
        text = "✅ Выполнил! Молодец! 👍" if gender == "male" else "✅ Выполнила! Молодец! 👍"
    else:
        text = "❌ Не выполнил... В следующий раз получится! 💪" if gender == "male" else "❌ Не выполнила... В следующий раз получится! 💪"
    
    await callback.answer(text, show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=None)

async def main():
    print("🤖 Бот запущен!")
    print(f"📊 Всего вопросов: {len(QUESTIONS)}")
    print("📨 Работает только по команде /ask (КД убран)")
    print("=" * 50)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
