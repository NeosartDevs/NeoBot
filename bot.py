import asyncio
import os
import random
import sqlite3
import re
import aiogram
from random import choice
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
import datetime
from datetime import datetime, timedelta


# Объект бота
bot = Bot(token="bot_token")
# Диспетчер
dp = Dispatcher()
print("Бот запущен")

dp = Dispatcher()

# Подключиться к базе данных SQLite
conn1 = sqlite3.connect("jokes.db")
cursor1 = conn1.cursor()

# Создать таблицу для хранения анекдотов, если она еще не существует
cursor1.execute("CREATE TABLE IF NOT EXISTS jokes (id INTEGER PRIMARY KEY, joke TEXT)")
conn1.commit()

conn5 = sqlite3.connect("ignor.db")
cursor5 = conn5.cursor()
cursor5.execute("""CREATE TABLE IF NOT EXISTS ignor (user_id INTEGER PRIMARY KEY)""")
conn5.commit()


@dp.message(Command("ignor"))
async def ignor_user(message: types.Message, state: FSMContext):
    if message.from_user.id != 6881556719:
        await message.reply("У вас нет прав для использования этой команды.")
        return
    
    user_id = int(message.text[len("/ignor "):])
    cursor5.execute("INSERT INTO ignor (user_id) VALUES (?)", (user_id,))
    conn5.commit()
    await message.reply("Пользователь добавлен в черный список.")

@dp.message(Command("deleteignor"))
async def delete_ignor_user(message: types.Message, state: FSMContext):
    if message.from_user.id != 6881556719:
        await message.reply("У вас нет прав для использования этой команды.")
        return

    user_id = int(message.text[len("/deleteignor "):])
    cursor5.execute("DELETE FROM ignor WHERE user_id = ?", (user_id,))
    conn5.commit()
    await message.reply("Пользователь удален из черного списка.")


# Обработчик команды /monetka
@dp.message(Command("monetka"))
async def monetka(message: aiogram.types.Message):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        # Выбор случайного значения (0 или 1)
        resut = random.randint(0, 1)

        # Отправка сообщения "орел" или "решка" в зависимости от результата
        if resut == 0:
            await message.answer("Вы подбросили монетку и вам выпал орел.")
        else:
            await message.answer("Вы подбросили монетку и вам выпала решка.")

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: aiogram.types.Message):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        await message.answer("Бот запущен. Текст старта в разработке.")


# Проверить, является ли пользователь создателем бота
def is_creator(user_id):
    return user_id in [7178621498, 6881556719]

# Обработчик команды /addanekdot
@dp.message(Command("addanekdot"))
async def add_anekdot(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Извлечь анекдот из сообщения
    joke = message.text[len("/addanekdot "):].strip()

    # Добавить анекдот в базу данных
    cursor1.execute("INSERT INTO jokes (joke) VALUES (?)", (joke,))
    conn1.commit()

    # Отправить ответное сообщение
    await message.answer("Анекдот успешно добавлен.")


# Обработчик команды /anekdot
@dp.message(Command("anekdot"))
async def get_anekdot(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        # Выбрать случайный анекдот из базы данных
        cursor1.execute("SELECT joke FROM jokes ORDER BY RANDOM() LIMIT 1")
        joke = cursor1.fetchone()[0]

        # Отправить ответное сообщение с анекдотом
        await message.answer(joke)

# Обработчик команды /anekdotlist
@dp.message(Command("anekdotlist"))
async def get_anekdot_list(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Получить все анекдоты из базы данных
    cursor1.execute("SELECT * FROM jokes")
    jokes = cursor1.fetchall()

    # Отправить ответное сообщение со списком анекдотов
    message_text = "**Список анекдотов:**\n"
    for joke in jokes:
        message_text += f"{joke[0]}. {joke[1]}\n"

    await message.answer(message_text)


# Обработчик команды /deleteanekdot
@dp.message(Command("deleteanekdot"))
async def delete_anekdot(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Извлечь идентификатор анекдота из сообщения
    match = re.match(r"/deleteanekdot (\d+)", message.text)
    if not match:
        await message.answer("Неправильный формат команды. Правильный формат: /deleteanekdot <id анекдота>")
        return

    anekdot_id = int(match.group(1))

    # Удалить анекдот из базы данных
    cursor1.execute("DELETE FROM jokes WHERE id = ?", (anekdot_id,))
    conn1.commit()

    # Отправить ответное сообщение
    await message.answer("Анекдот успешно удален.")


# Подключиться к базе данных SQLite
conn2 = sqlite3.connect("facts.db")
cursor2 = conn2.cursor()

# Создать таблицу для хранения фактов, если она еще не существует
cursor2.execute("""CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY,
    fact TEXT
)""")
conn2.commit()


# Обработчик команды /addfact
@dp.message(Command("addfact"))
async def add_fact(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Извлечь факт из сообщения
    fact = message.text[len("/addfact "):].strip()

    # Добавить факт в базу данных
    cursor2.execute("INSERT INTO facts (fact) VALUES (?)", (fact,))
    conn2.commit()

    # Отправить ответное сообщение
    await message.answer("Факт успешно добавлен.")


# Обработчик команды /fact
@dp.message(Command("fact"))
async def get_fact(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        # Выбрать случайный факт из базы данных
        cursor2.execute("SELECT fact FROM facts ORDER BY RANDOM() LIMIT 1")
        fact = cursor2.fetchone()[0]

        # Отправить ответное сообщение с фактом
        await message.answer(fact)

# Обработчик команды /factlist
@dp.message(Command("factlist"))
async def get_fact_list(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Получить все факты из базы данных
    cursor2.execute("SELECT * FROM facts")
    facts = cursor2.fetchall()

    # Отправить ответное сообщение со списком фактов
    message_text = "**Список фактов:**\n"
    for fact in facts:
        message_text += f"{fact[0]}. {fact[1]}\n"

    await message.answer(message_text)


# Обработчик команды /deletefact
@dp.message(Command("deletefact"))
async def delete_fact(message: types.Message, state: FSMContext):
    # Проверить, является ли пользователь создателем бота
    if not is_creator(message.from_user.id):
        await message.answer("Вы не можете использовать эту команду.")
        return

    # Извлечь идентификатор факта из сообщения
    match = re.match(r"/deletefact (\d+)", message.text)
    if not match:
        await message.answer("Неправильный формат команды. Правильный формат: /deletefact <id факта>")
        return

    fact_id = int(match.group(1))

    # Удалить факт из базы данных
    cursor2.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
    conn2.commit()

    # Отправить ответное сообщение
    await message.answer("Факт успешно удален.")

# Подключиться к базе данных SQLite
conn = sqlite3.connect("birthdays.db")
cursor = conn.cursor()

# Создать таблицу для хранения дней рождения, если она еще не существует
cursor.execute("CREATE TABLE IF NOT EXISTS birthdays (user_id INTEGER PRIMARY KEY, birthdate TEXT)")
conn.commit()


# Обработчик команды /addbirthdays
@dp.message(Command("addbirthdays"))
async def add_birthdays(message: types.Message, state: FSMContext):
    # Проверить, указана ли дата рождения в сообщении
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        if not message.text[len("/addbirthdays "):].strip():
            await message.answer("Укажите дату своего рождения в формате дд.мм.гггг.")
            return

        # Извлечь дату рождения из сообщения
        try:
            birthdate = datetime.strptime(message.text[len("/addbirthdays "):].strip(), "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат даты. Укажите дату в формате дд.мм.гггг.")
            return

        # Добавить дату рождения в базу данных
        cursor.execute("INSERT INTO birthdays (user_id, birthdate) VALUES (?, ?)", (message.from_user.id, birthdate.strftime("%d.%m.%Y")))
        conn.commit()

        # Отправить ответное сообщение
        await message.answer("Ваша дата рождения успешно добавлена.")


# Обработчик команды /birthdays
@dp.message(Command("birthdays"))
async def get_birthdays(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        # Проверить, есть ли дата рождения пользователя в базе данных
        cursor.execute("SELECT birthdate FROM birthdays WHERE user_id = ?", (message.from_user.id,))
        birthdate = cursor.fetchone()
        if not birthdate:
            await message.answer("Вы еще не добавили свою дату рождения. Добавьте ее с помощью команды /addbirthdays.")
            return

        # Рассчитать количество дней до дня рождения
        birthdate = datetime.strptime(birthdate[0], "%d.%m.%Y")
        today = datetime.now()
        next_birthdate = birthdate.replace(year=today.year)
        if next_birthdate < today:
            next_birthdate = next_birthdate.replace(year=today.year + 1)
        days_to_birthday = (next_birthdate - today).days

        # Отправить ответное сообщение
        await message.answer(f"До вашего дня рождения осталось {days_to_birthday} дней.")
       
# Обработчик команды /deletebirthdays
@dp.message(Command("deletebirthdays"))
async def delete_birthdays(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor5.execute("SELECT * FROM ignor WHERE user_id = ?", (user_id,))
    result = cursor5.fetchone()
    if result:
        await message.reply("Вы находитесь в черном списке бота.")
    else:
        # Удалить дату рождения пользователя из базы данных
        cursor.execute("DELETE FROM birthdays WHERE user_id = ?", (message.from_user.id,))
        conn.commit()

        # Отправить ответное сообщение
        await message.answer("Ваша дата рождения успешно удалена.")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

