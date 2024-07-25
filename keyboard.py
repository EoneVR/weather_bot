from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from langs import langs


def generate_lang_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='🇺🇸 English')],
        [KeyboardButton(text='🇷🇺 Русский')],
    ], resize_keyboard=True)


def generate_period_button(lang):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(text=langs[lang]['day'], callback_data='today'),
        InlineKeyboardButton(text=langs[lang]['three'], callback_data='three_days')
    )
    return markup
