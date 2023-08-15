from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import MENU, PAGE

'''Изначальное меню'''


async def main_menu():
    inline_markup: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text='🥅Команда',
        callback_data='commands'
    ), InlineKeyboardButton(
        text='📈Рейтинг',
        callback_data='rating'
    ), InlineKeyboardButton(
        text='🏒Игроки',
        callback_data='players'
    ), InlineKeyboardButton(
        text='🏆Турниры',
        callback_data='tournaments'
    ), InlineKeyboardButton(
        text='🎲Ставки',
        callback_data='bet'
    ), InlineKeyboardButton(
        text='🏪Магазин',
        callback_data='shop'
    )
    ]

    inline_markup.row(*buttons, width=2)
    return inline_markup.as_markup()

'''Генератор инлайн клавиатуры (Количество в строке, префикс, название кнопок)'''
def create_inline_kb(width: int,
                     pref: str,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=pref + button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=pref + button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура страниц'''
def create_pg_kb_command(pref: str, *buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.row(*[InlineKeyboardButton(
        text=PAGE[button] if button in PAGE else button,
        callback_data=f'{pref}_{button}') for button in buttons]).row(InlineKeyboardButton(text='✅Выбрать', callback_data=f'choice_player'))
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

'''Клавиатура листания игроков'''
def create_pg_kb_players(pref: str, price: str, *buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.row(*[InlineKeyboardButton(
        text=PAGE[button] if button in PAGE else button,
        callback_data=f'{pref}_{button}') for button in buttons]).\
        row(InlineKeyboardButton(text=f'{price}', callback_data=f'price_{price.split(":")[0]}_{pref.split("_")[2]}_{pref.split("_")[3]}')).\
        row(InlineKeyboardButton(text=PAGE['back'], callback_data=f'{pref}_players'))
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура листания игроков с выбором в команду'''
def create_pg_choice_players(pref: str, price: str, *buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.row(*[InlineKeyboardButton(
        text=PAGE[button] if button in PAGE else button,
        callback_data=f'{pref}_{button}') for button in buttons]).\
        row(InlineKeyboardButton(text=f'{price}', callback_data=f'{pref}_choice')).\
        row(InlineKeyboardButton(text=PAGE['back'], callback_data=f'{pref}_team'))
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

'''Обычное меню внизу'''
btn_menu: KeyboardButton = KeyboardButton(text='⚙️МЕНЮ')
btn_game: KeyboardButton = KeyboardButton(text='🏒🥅ИГРА')
btn_command: KeyboardButton = KeyboardButton(text='🥅Команда')
btn_bet: KeyboardButton = KeyboardButton(text='🎲Cтавки')
btn_tournament: KeyboardButton = KeyboardButton(text='🏆Добавить турнир')
btn_players_add: KeyboardButton = KeyboardButton(text=MENU['add_player'])
menu_user_private: ReplyKeyboardMarkup = ReplyKeyboardMarkup(width=1, keyboard=[[btn_menu], [btn_game]],
                                                    resize_keyboard=True)
menu_admin: ReplyKeyboardMarkup = ReplyKeyboardMarkup(width=2, keyboard=[[btn_menu], [btn_game], [btn_bet],
                                                                         [btn_tournament], [btn_players_add]],
                                                    resize_keyboard=True)
menu_user: ReplyKeyboardMarkup = ReplyKeyboardMarkup(width=1, keyboard=[[btn_command],[btn_game]],
                                                    resize_keyboard=True)


'''Меню для команды'''
def kb_team(pref: str, name_pos: str, *buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.row(InlineKeyboardButton(text=f'{name_pos}', callback_data=f'my_team_{name_pos}')).\
        row(*[InlineKeyboardButton(
        text=PAGE[button] if button in PAGE else button,
        callback_data=f'{pref}_{name_pos}_{button}') for button in buttons])
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()
