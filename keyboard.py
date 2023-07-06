from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def menu():
    download_button = KeyboardButton('🎬Скачать по ссылке🎬')
    search_button = KeyboardButton('🔍 Поиск')
    about_button = KeyboardButton('🔥О Нас🔥')
    menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_kb.add(download_button,search_button)
    menu_kb.add(about_button)
    return menu_kb
def back():
    button_back = KeyboardButton('Назад')
    back_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back_kb.add(button_back)
    return back_kb
def make_keyboards(url):
    inline_kb1 = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Лучшее качество до 1080p(с звуком).🏯', callback_data=f'best_with_audio|{url}')
    button2 = InlineKeyboardButton('Звук в лучшем качестве.🔊', callback_data=f'best_audio|{url}')
    button3 = InlineKeyboardButton('Отмена', callback_data=f'cancel')
    inline_kb1.add(button)
    inline_kb1.add(button2)
    inline_kb1.add(button3)
    return inline_kb1