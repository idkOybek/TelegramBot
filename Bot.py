import gspread
import logging
import Config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

sa = gspread.service_account(filename="acount.json")
sh = sa.open("Medicaltgbot")

global row
row = 2
wks = sh.worksheet("CallBack")


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
    wks.update('A'+str(row), message.from_user.id)

@dp.message_handler(text="повторная запись")
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.answer("Как вас зовут?",reply_markup=types.ReplyKeyboardRemove())
    wks.update('A'+str(row), message.from_user.id)


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    wks.update('B'+str(row), message.text)
    await message.reply(f"Здравствуйте, {message.text}", reply_markup=types.ReplyKeyboardRemove())
    await Form.number.set()
    await message.reply(f"{message.text} , отправьте свой номер телефона с кодом")


@dp.message_handler(state=Form.number)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    wks.update('C' + str(row), message.text)
    await Form.problem.set()
    await message.reply("Опишите свою проблему :")


@dp.message_handler(state=Form.problem)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    kb = [[types.KeyboardButton(text="пропустить")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на скрепку и прикрепите фото"
    )
    await Form.photo.set()
    wks.update('D' + str(row), message.text)
    await message.reply(f"Если есть изображения прикрепите , если нет нажмите Пропустить", reply_markup=keyboard)


@dp.message_handler(state=Form.photo)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    wks.update('E' + str(row), message.text)
    await Form.end.set()
    await message.reply("Спасибо с вами обязательно свяжутся",reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state='*', text='пропустить')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    wks.update('E' + str(row), message.text)
    await state.finish()
    await Form.end.set()
    await message.reply('Спасибо с вами обязательно свяжутся',reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.end)
async def cancel_handler(message: types.Message,state : FSMContext):
    global row
    await state.finish()
    kb = [[types.KeyboardButton(text="повторная запись")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="или напишите повторная запись"
    )
    row += 1
    await message.answer("Желаете еще раз записаться ?", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
