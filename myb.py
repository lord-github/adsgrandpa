import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "7586200359:AAFiRlrLXt_usEmPW4J26e-qGXp6QPLOTwA"
AD_URL = "https://example.com/ad"  # Ссылка на рекламу
REWARD_AMOUNT = 10  # Сумма начисления за просмотр рекламы

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Подключение к базе данных
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)""")
conn.commit()

# Функция проверки и добавления пользователя в БД
def add_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()

# Кнопки меню
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📺 Смотреть рекламу", callback_data="watch_ad"),
        InlineKeyboardButton("💰 Баланс", callback_data="check_balance"),
        InlineKeyboardButton("📞 Служба поддержки", url="https://t.me/support")  # Замените на свою поддержку
    )
    return keyboard

@dp.message_handler(commands=["start"])
async def start(message: Message):
    user_id = message.from_user.id
    add_user(user_id)
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=get_main_keyboard())

@dp.callback_query_handler(lambda c: c.data == "watch_ad")
async def watch_ad(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, f"Просмотрите рекламу по ссылке: {AD_URL}\nПосле просмотра нажмите кнопку '✅ Готово'.",
                           reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("✅ Готово", callback_data="ad_done")))

@dp.callback_query_handler(lambda c: c.data == "ad_done")
async def ad_done(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (REWARD_AMOUNT, user_id))
    conn.commit()
    await bot.answer_callback_query(callback_query.id, "Вам начислено 10 монет!")
    await bot.send_message(user_id, f"🎉 Вы получили {REWARD_AMOUNT} монет! Ваш баланс обновлен.", reply_markup=get_main_keyboard())

@dp.callback_query_handler(lambda c: c.data == "check_balance")
async def check_balance(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, f"💰 Ваш баланс: {balance} монет", reply_markup=get_main_keyboard())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
