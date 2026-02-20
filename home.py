import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

import os
import logging
import sqlite3

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()

def create_database_and_table():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

create_database_and_table()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Давай начнем заполнять твои данные. Как тебя зовут?")
    await state.set_state(StudentForm.name)

@dp.message(StudentForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Какой у тебя возраст?")
    await state.set_state(StudentForm.age)

@dp.message(StudentForm.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        await state.update_data(age=age)
        await message.answer("В каком классе ты учишься?")
        await state.set_state(StudentForm.grade)
    except ValueError:
        await message.answer("Возраст введен некорректно. Повторите попытку.")

@dp.message(StudentForm.grade)
async def process_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text.strip())
    student_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)', (student_data['name'], student_data['age'], student_data['grade']))
    conn.commit()
    conn.close()

    await message.answer(f"Данные успешно сохранены!\nИмя: {student_data['name']},\nВозраст: {student_data['age']},\nКласс: {student_data['grade']}.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())