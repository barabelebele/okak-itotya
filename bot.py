import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8376965944:AAEVAn5XOKi9Cy-m_TR7Jik-z12M2uEsaPU"
MANAGER_ID = 8527700575  
CARD_NUMBER = "2204320900008568"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для связи: ID_менеджера -> ID_активного_юзера
active_chats = {}

class ShopState(StatesGroup):
    wait_nickname = State()
    wait_receipt = State()
    in_support = State() # Состояние чата поддержки

# --- КЛАВИАТУРЫ ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💎 Донаты", callback_data="cat_donate"))
    builder.row(types.InlineKeyboardButton(text="📦 Кейсы", callback_data="cat_cases"))
    builder.row(types.InlineKeyboardButton(text="🔓 Разбан — 70₽", callback_data="pay_Разбан_70"))
    builder.row(types.InlineKeyboardButton(text="🆘 Тех. поддержка", callback_data="start_support"))
    return builder.as_markup()

# --- ЛОГИКА МАГАЗИНА (БЕЗ ИЗМЕНЕНИЙ) ---

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Привет! Это магазин сервера **Minecraft**.\nВыберите раздел:", reply_markup=main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите категорию:", reply_markup=main_menu())

@dp.callback_query(F.data == "cat_donate")
async def donate_list(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    items = [("Элита", 19), ("Страж", 39), ("Герой", 79), ("Князь", 149), ("Шторм", 249), ("Эндер", 449), ("Блейз", 579), ("Визер", 749), ("Фантом", 999), ("Д.Хелпер", 1249), ("Д.Модер", 2790), ("Д.Админ", 3649)]
    for name, price in items: builder.button(text=f"{name} {price}₽", callback_data=f"pay_{name}_{price}")
    builder.adjust(2).row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    await callback.message.edit_text("✨ **Выберите привилегию:**", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "cat_cases")
async def cases_list(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    items = [("Кейс Донат", 99), ("Кейс Жетон", 49), ("Кейс Префикс", 10), ("Кейс Титул", 29), ("Кейс Монеты", 10)]
    for name, price in items: builder.button(text=f"{name} {price}₽", callback_data=f"pay_{name}_{price}")
    builder.adjust(1).row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    await callback.message.edit_text("📦 **Выберите кейс:**", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("pay_"))
async def start_buy(callback: types.CallbackQuery, state: FSMContext):
    _, item, price = callback.data.split("_")
    await state.update_data(item=item, price=price)
    await callback.message.edit_text(f"🛒 Вы выбрали: **{item}**\n\n⌨️ Введите ваш **игровой ник**:", parse_mode="Markdown")
    await state.set_state(ShopState.wait_nickname)

@dp.message(ShopState.wait_nickname)
async def get_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    data = await state.get_data()
    await message.answer(f"✅ Ник: `{data['nickname']}`\n💰 Сумма: `{data['price']}₽`\n💳 Карта: `{CARD_NUMBER}`\n\n📸 Пришлите фото чека.", parse_mode="Markdown")
    await state.set_state(ShopState.wait_receipt)

@dp.message(ShopState.wait_receipt, F.photo)
async def get_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"✅ **Спасибо!**\nВ течении 15-30 мин будет выдан(а) **{data['item']}**.\nМы работаем с **8:00 по 20:00 МСК**.", parse_mode="Markdown")
    caption = f"⚠️ **НОВЫЙ ЗАКАЗ**\n\n👤 Юзер: @{message.from_user.username}\n🎮 Ник: `{data['nickname']}`\n📦 Товар: {data['item']}\n💵 Сумма: {data['price']}₽"
    await bot.send_photo(MANAGER_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
    await state.clear()

# --- ЛОГИКА ПОДДЕРЖКИ (АНОНИМНЫЙ ЧАТ) ---

@dp.callback_query(F.data == "start_support")
async def open_support(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("💬 Вы подключились к поддержке. Напишите ваш вопрос ниже 👇\n(Админ увидит ваше сообщение, но не ваш профиль)")
    await state.set_state(ShopState.in_support)
    # Уведомляем админа
    await bot.send_message(MANAGER_ID, f"🔔 Юзер @{callback.from_user.username} (ID: `{callback.from_user.id}`) начал чат!")
    active_chats[MANAGER_ID] = callback.from_user.id

# Если пишет юзер в поддержку -> летит админу
@dp.message(ShopState.in_support)
async def support_to_admin(message: types.Message):
    if message.text == "/Стоп":
        await message.answer("❌ Чат завершен.", reply_markup=main_menu())
        await bot.send_message(MANAGER_ID, "❌ Пользователь завершил чат.")
        return
    
    await bot.send_message(MANAGER_ID, f"📩 **Сообщение от юзера:**\n{message.text}")

# Если пишет админ (ты) -> летит юзеру
@dp.message(F.from_user.id == MANAGER_ID)
async def admin_to_user(message: types.Message):
    user_id = active_chats.get(MANAGER_ID)
    
    if message.text == "/Стоп":
        if user_id:
            await bot.send_message(user_id, "⚠️ Администратор завершил диалог.", reply_markup=main_menu())
            await bot.send_message(MANAGER_ID, "✅ Вы завершили чат.")
            active_chats.pop(MANAGER_ID, None)
        return

    if user_id:
        try:
            await bot.send_message(user_id, f"👨‍💻 **Ответ поддержки:**\n{message.text}")
        except:
            await message.answer("Ошибка: пользователь заблокировал бота или чат не найден.")
    else:
        await message.answer("Сначала кто-то должен написать в поддержку!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
