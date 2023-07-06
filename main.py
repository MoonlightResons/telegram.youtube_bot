import tracemalloc
tracemalloc.start()
import os, re, configparser, pafy, random
from googleapiclient.discovery import build
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keyboard import menu, back, make_keyboards
from models import Video
config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["tgbot"]["token"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def get_title(url):
    yVideo = pafy.new(url)
    title = yVideo.title
    return title

def get_author(url):
    yVideo = pafy.new(url)
    author = yVideo.author
    return author

def get_url(call):
    url = call.split('|') 
    video_url = url[1]
    return video_url

def get_download_url_with_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbest()
    return video.url_https

def get_download_url_best_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbestaudio()
    return video.url_https

class Info(StatesGroup):
    video = State()
    search = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=' Привет, я помогу тебе скачать видео с YouTube.', reply_markup = menu())

@dp.message_handler(text="🔥О Нас🔥")
async def about_info(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Привет данный бот создан мной(Нурбеком), как первый проект для Ogogo Academy. Он будет тебе полезен для скачивания видео и аудио из ютуба в высоком качестве. Приятного использования!!', reply_markup = menu())

@dp.message_handler(text="🎬Скачать по ссылке🎬")
async def save_video(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=' Введи ссылку на видео: ', reply_markup=back())
    await Info.video.set()

@dp.message_handler(state=Info.video, content_types=types.ContentTypes.TEXT)
async def edit_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся в главное меню.', reply_markup=menu())
        await state.finish()
    elif message.text.lower() == '🔍 Поиск по названию':
        await bot.send_message(chat_id=message.chat.id, text='Введите название видео для поиска:', reply_markup=back())
        await Info.search.set()
    else:
        if message.text.startswith('https://www.youtube.com/watch?v='):
            try:
                video_url = message.text
                await bot.send_message(chat_id=message.chat.id, text=f'Название видео: {get_title(video_url)}\nАвтор: {get_author(video_url)}\n\nВыберите качество загрузки:', reply_markup = make_keyboards(video_url))
                await state.finish()
            except OSError:
                await bot.send_message(chat_id=message.chat.id, text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
            except ValueError:
                await bot.send_message(chat_id=message.chat.id, text=f'Значение Ссылки неверное, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```', reply_markup = back(), parse_mode="Markdown")


@dp.message_handler(text="🔍 Поиск")
async def search_videos(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Введите название видео для поиска:', reply_markup=back())
    await Info.search.set()

@dp.message_handler(state=Info.search, content_types=types.ContentTypes.TEXT)
async def search_videos_by_title(message: types.Message, state: FSMContext):
    if message.text.lower() == "назад":
        await bot.send_message(
            chat_id=message.chat.id,
            text="Ты вернулся в главное меню.",
            reply_markup=menu())
        await state.finish()
    else:
        query = message.text
        search_results = await perform_search(query)
        
    if search_results:
        await bot.send_message(
        chat_id=message.chat.id,
        text="Результаты поиска:"
    )
    for video in search_results:
        video_url = video.url
        video_info = f"Название: {get_title(video_url)}\nАвтор: {get_author(video_url)}\nСсылка: {video_url}"
        await bot.send_message(
            chat_id=message.chat.id,
            text=video_info,
            reply_markup=make_keyboards(video_url)
        )
    else:
            await bot.send_message(
                chat_id=message.chat.id,
                text="По вашему запросу ничего не найдено.")

    await state.finish()

async def perform_search(query):
    search_results = []
    api_key = "AIzaSyCJMlBLGPTaLKoYTat_k0mQ_x38Z-E3g2A"

    youtube = build('youtube', 'v3', developerKey=api_key)

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=5
    ).execute()

    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        video = Video(title=video_title,author=video_url, url=video_url)
        search_results.append(video)

    return search_results

@dp.callback_query_handler()
async def handler_call(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    if call.data.startswith('best_with_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_with_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание видео: {download_link}', reply_markup = menu())
    elif call.data.startswith('best_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_best_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание аудио: {download_link}', reply_markup = menu())
    elif call.data == 'cancel':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(chat_id=chat_id, text='Ты вернулся в главное меню.', reply_markup=menu())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
