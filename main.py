import os
from dotenv import load_dotenv
from shazamio import Shazam

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, FSInputFile, ContentType)

from request import find_track, download_track

load_dotenv() # Загрузка переменных среды

TOKEN = os.getenv('TOKEN') # Зпись токена из виртуальной среды в переменную

bot = Bot(token=TOKEN)
dp = Dispatcher() # Создание объекта диспетчера, который управляет ботом

shazam = Shazam() # Создание объекта шазама, чтобы распознавать голосовые

storage = MemoryStorage() # Создания хранилища в оперативной памяти для хранения состояния

user_dict: dict[int, dict[str, str | int | bool]] = {} # Создание "базы данных"


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM при поиске трека
class FSMFindTrack(StatesGroup):
    enter_name = State()
    choose_track = State()


# Хэндлер реагирует на голосовые сообщения и сразу начинает распознавать музыку
@dp.message(F.content_type == ContentType.VOICE)
async def voice_message_handler(message: Message, state: FSMContext):
    voice = message.voice
    file_info = await bot.get_file(voice.file_id)
    file = await bot.download_file(file_info.file_path)

    # Сохраняем файл на диск
    with open(f'voices/voice_{message.message_id}.ogg', 'wb') as f:
        f.write(file.read())

    # await message.answer("Голосовое сообщение сохранено!")

    # Сохраняем в переменную результат распознавания трека
    recognition = await shazam.recognize(f"voices/voice_{message.message_id}.ogg")

    # print(recognition)

    # Если никакого трека не распозналось, пишем, что треки не найдены
    if not recognition["matches"]:
        await message.answer(text="К сожалению, ничего не найдено")
        return

    # Записываем название распознанного трека и ссылку на его обложку
    track_name = f'{recognition["track"]["title"]} - {recognition["track"]["subtitle"]}'
    coverart_url = recognition["track"]["images"]["coverart"]

    # Отправляем обложку с подписью трека
    await message.answer_photo(photo=coverart_url, caption=track_name)

    # print(coverart)

    # print(update.message.chat, track_name)
    # print(type(recognition))
    # print(recognition.keys())
    # pprint(recognition["track"])
    # print(recognition["track"].keys())
    # print(recognition["track"]["title"], recognition["track"]["subtitle"])
    # print(recognition["track"]["images"]["coverart"])

    # Сбрасываем состояние машины состояний
    await state.clear()


# Срабатывает при вводе команды /start
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Это бот для скачавания музыки. Введите /find для поиска песни или отправьте голосовое сообщение для распознавания на нем музыки.")


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего.\n'
             'Чтобы перейти к поиску - '
             'отправьте команду /find'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из режима поиска\n\n'
             'Чтобы снова перейти к поиску - '
             'отправьте команду /find'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Срабатывает при вводе команды /find. Проводит поиск трека по названию или по исполнителю
@dp.message(Command(commands="find"), StateFilter(default_state))
async def find_track_command(message: Message, state: FSMContext):
    await message.answer(text="Введите название трека или исполнителя, которого хотите найти")

    await state.set_state(FSMFindTrack.enter_name) # Обновляем состояние на "ввод названия трека"


# Срабатывает после команды /find, когда пользователь вводит название трека (Любой набор символов)
@dp.message(StateFilter(FSMFindTrack.enter_name))
async def enter_track_name(message: Message, state: FSMContext):
    query = message.text # Текст, введенный пользователем

    tracks = find_track(query) # Поиск треков

    # Если треки не найдены, сообщаем об этом 
    if not tracks:
        message.answer("Ничего не найдено")
        await state.clear()
        return

    # Формируем список треков для красивого вывода
    response = "\n".join([f"{i + 1}: {data[0]} | {data[1][1]}" for i, data in enumerate(tracks.items())])

    await message.answer(text=response) # Выводим список

    await state.update_data(tracks=tracks.items()) # Добавляем список треков в "базу данных"

    # first_button = InlineKeyboardButton(
    #     text='1',
    #     callback_data=1
    # )
    # second_button = InlineKeyboardButton(
    #     text='2',
    #     callback_data=2
    # )
    # third_button = InlineKeyboardButton(
    #     text='3',
    #     callback_data=3
    # )
    # fourth_button = InlineKeyboardButton(
    #     text='4',
    #     callback_data=4
    # )
    # fith_button = InlineKeyboardButton(
    #     text='5',
    #     callback_data=5
    # )                 
    # 
    # keyboard: list[list[InlineKeyboardButton]] = [
    #   [first_button, second_button, third_button, fourth_button, fith_button]
    # ]
    # 
    #                            ^
    #                            |
    # Это выражение эквивалентно этому фрагменту кода: формирование клавиатуры
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, len(tracks.items()) + 1)]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text="Выберете номер трека, который хотите скачать", reply_markup=markup) # Вывод сообщения с клавиатурой под ним
    await state.set_state(FSMFindTrack.choose_track) # Обновление состояния машины на "Выбор трека"


# Срабатывает, когда пользователь нажимает на клавиатуру под сообщением.
@dp.callback_query(StateFilter(FSMFindTrack.choose_track))
async def process_track_num(callback: CallbackQuery, state: FSMContext):
    # Удаляем сообщение с кнопками, чтобы у пользователя не было желания тыкать их
    await callback.message.delete()

    data = await state.get_data() # Вытаскиваем данные о найденных треках из БД

    track_url = list(data['tracks'])[int(callback.data) - 1][1][0] # Сохранение ссылки на скачивание трека
    track_name = list(data['tracks'])[int(callback.data) - 1][0] # Созранение названия трека

    path = download_track(track_url, track_name) # Скачивание трека и созранение пути к файлу в переменную

    audio_file = FSInputFile(path=path) # Создание объекта файла, чтобы его можно было отправить

    # Отправка файла и очистка состояния, так как итерация скачивания завершена
    await callback.message.answer_audio(audio=audio_file)
    print("Отправлено")

    await state.clear()


# Срабатывает, если ни одно сообщение не подошло по фильтрам. Расчитано на то, что пользователь не понял, что делать
@dp.message(StateFilter(default_state))
async def finally_message(message: Message):
    await message.answer("Я вас не понимаю. Введите /find для поиска или отправьте голосовое сообщение, чтобы его зашазамить")


if __name__ == "__main__":
    dp.run_polling(bot)
