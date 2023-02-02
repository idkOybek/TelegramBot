import logging
import Config
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

conn = sqlite3.connect("C:/Users/oybek/OneDrive/Desktop/db/Medical.db", check_same_thread=False)
cursor = conn.cursor()

def db_table_val(user_id: int, user_name: str, name: str, number: int, problem: str):
	cursor.execute('INSERT INTO reCall (user_id, user_name, name, number, problem) VALUES (?, ?, ?, ?, ?)', (user_id, user_name, name, number,problem))
	conn.commit()

# Тут токен крч из конфига
API_TOKEN = Config.TOKEN

logging.basicConfig(level=logging.INFO)

# запуск бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    number = State()
    problem = State()
    photo = State()
    start = State()
    end = State()


# улавливает команду старт
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.answer("Как вас зовут?",reply_markup=types.ReplyKeyboardRemove())
    global us_id
    global us_name
    us_id = message.from_user.id
    us_name = message.from_user.first_name

@dp.message_handler(text="повторная запись")
async def cmd_start(message: types.Message):
    global us_id
    global us_name
    await Form.name.set()
    await message.answer("Как вас зовут?",reply_markup=types.ReplyKeyboardRemove())
    us_id = message.from_user.id
    us_name = message.from_user.first_name


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    global uName
    uName = message.text
    await message.reply(f"Здравствуйте, {message.text}", reply_markup=types.ReplyKeyboardRemove())
    await Form.number.set()
    await message.reply(f"{message.text} , отправьте свой номер телефона с кодом")

@dp.message_handler(state=Form.number)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    global uPhone
    uPhone = message.text
    await Form.problem.set()
    await message.reply("Опишите свою проблему :")



@dp.message_handler(state=Form.problem)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    global uProblem
    uProblem = message.text
    kb = [[types.KeyboardButton(text="пропустить")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на скрепку и прикрепите фото"
    )
    await Form.photo.set()
    await message.reply(f"Если есть изображения прикрепите , если нет нажмите Пропустить", reply_markup=keyboard)


@dp.message_handler(state=Form.photo)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    db_table_val(user_id=us_id, user_name=us_name, name=uName, number=uPhone, problem=uProblem)
    await Form.end.set()
    await message.reply("Спасибо с вами обязательно свяжутся",reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state='*', text='пропустить')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await Form.end.set()
    await message.reply('Спасибо с вами обязательно свяжутся',reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.end)
async def cancel_handler(message: types.Message,state : FSMContext):
    await state.finish()
    kb = [[types.KeyboardButton(text="повторная запись")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="или напишите повторная запись"
    )
    await message.answer("Желаете еще раз записаться ?", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
