from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from bot_menu.menu import main_menu, menu_user_private, menu_admin, create_pg_kb_command
from create_bot import bot
from database.orm import get_user, add_users, get_goalkeepers, get_name_commands, get_name_commands_id, get_players, \
    add_card_user, add_command
from lexicon.lexicon_ru import Attributes_goalkeepers, PLAYERS, Attributes_players

router: Router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


'''FSM для создания команды'''


class FSMname_command(StatesGroup):
    name = State()
    goalkeepers = State()
    forward_1 = State()
    forward_2 = State()
    forward_3 = State()
    defender_1 = State()
    defender_2 = State()


'''FSM для страниц'''


class FSMpage(StatesGroup):
    page = State()


'''Команда старт'''


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    users = await get_user(message.from_user.id)
    commands = await get_name_commands_id(message.from_user.id)
    if users and commands:
        await message.answer(text=f'🤝Приветствую тебя, {message.from_user.username}!',
                                 reply_markup=menu_user_private)
    else:
        if not users:
            await add_users(message.from_user.id, message.from_user.username)
        await message.answer(text=f'🤝Приветствую тебя, {message.from_user.username}!\n'
                                  '🥅Давай придумаем название, которое будет идеально подходить для '
                                  'твоей хоккейной команды и вызывать восхищение у фанатов.')
        await state.set_state(FSMname_command.name)


'''Ввод названия команды'''


@router.message(StateFilter(FSMname_command.name))
async def add_name_command(message: Message, state: FSMContext):
    commands = await get_name_commands(message.text)
    if not commands:
        await state.update_data(name=message.text)
        goalkeepers = await get_goalkeepers()
        await state.set_state(FSMpage.page)
        await state.update_data(page=0)
        await state.set_state(FSMname_command.goalkeepers)
        pg = await state.get_data()
        pg = pg['page']
        await message.answer(text='Давайте сформируем состав команды, который будет состоять из одного вратаря🥅, '
                                  'трех нападающих⚡️ и двух защитников🛡️')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=goalkeepers[pg]['img'],
                             caption=caption_players(0, pg, goalkeepers),
                             reply_markup=create_pg_kb_command('goalkeepers',
                                                               'backward', f'{pg + 1} / {len(goalkeepers)}', 'forward'))
    else:
        await message.answer(text='Такая команда уже существует.\n'
                                  'Попробуй другое имя')



'''Выбор карточки'''


@router.callback_query(F.data == 'choice_player')
async def choice_player(callback: CallbackQuery, state: FSMContext):
    q = await state.get_state()
    pg = await state.get_data()
    pg = pg['page']
    if q.split(':')[-1] == 'goalkeepers':
        goalkeepers = await get_goalkeepers()
        await state.update_data(goalkeepers=goalkeepers[pg]['goalkeeper_id'])
        await add_card_user(callback.from_user.id, goalkeepers[pg]['goalkeeper_id'], PLAYERS['goalkeeper'])
        await state.update_data(page=0)
        pg = await state.get_data()
        pg = pg['page']
        await state.set_state(FSMname_command.forward_1)
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=players[pg]['img'],
                                                           caption=caption_players(1, pg, players)),
                                     reply_markup=create_pg_kb_command(PLAYERS['forward'], 'backward',
                                                                       f'{pg + 1} / {len(players)}',
                                                                       'forward'))
    elif q.split(':')[-1] == 'forward_1':
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await add_card_user(callback.from_user.id, players[pg]['player_id'], PLAYERS['forward'])
        await state.update_data(forward_1=players[pg]['player_id'])
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await state.update_data(page=0)
        pg = await state.get_data()
        pg = pg['page']
        await state.set_state(FSMname_command.forward_2)
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=players[pg]['img'],
                                                           caption=caption_players(1, pg, players)),
                                     reply_markup=create_pg_kb_command(PLAYERS['forward'], 'backward',
                                                                       f'{pg + 1} / {len(players)}',
                                                                       'forward'))
    elif q.split(':')[-1] == 'forward_2':
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await add_card_user(callback.from_user.id, players[pg]['player_id'], PLAYERS['forward'])
        await state.update_data(forward_2=players[pg]['player_id'])
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await state.update_data(page=0)
        pg = await state.get_data()
        pg = pg['page']
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=players[pg]['img'],
                                                           caption=caption_players(1, pg, players)),
                                     reply_markup=create_pg_kb_command(PLAYERS['forward'], 'backward',
                                                                       f'{pg + 1} / {len(players)}',
                                                                       'forward'))
        await state.set_state(FSMname_command.forward_3)
    elif q.split(':')[-1] == 'forward_3':
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        await add_card_user(callback.from_user.id, players[pg]['player_id'], PLAYERS['forward'])
        await state.update_data(forward_3=players[pg]['player_id'])
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        await state.update_data(page=0)
        pg = await state.get_data()
        pg = pg['page']
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=players[pg]['img'],
                                                           caption=caption_players(1, pg, players)),
                                     reply_markup=create_pg_kb_command(PLAYERS['defender'], 'backward',
                                                                       f'{pg + 1} / {len(players)}',
                                                                       'forward'))
        await state.set_state(FSMname_command.defender_1)
    elif q.split(':')[-1] == 'defender_1':
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        await add_card_user(callback.from_user.id, players[pg]['player_id'], PLAYERS['defender'])
        await state.update_data(defender_1=players[pg]['player_id'])
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        await state.update_data(page=0)
        pg = await state.get_data()
        pg = pg['page']
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=players[pg]['img'],
                                                           caption=caption_players(1, pg, players)),
                                     reply_markup=create_pg_kb_command(PLAYERS['defender'], 'backward',
                                                                       f'{pg + 1} / {len(players)}',
                                                                       'forward'))
        await state.set_state(FSMname_command.defender_2)
    else:
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        await add_card_user(callback.from_user.id, players[pg]['player_id'], PLAYERS['defender'])
        await state.update_data(defender_2=players[pg]['player_id'])
        new_commands = await state.get_data()
        await add_command(new_commands, callback.from_user.id)
        await state.clear()
        await callback.message.answer(text='✅Команда успешно собрана✅')
        await callback.message.answer(text=f'🤝Приветствую тебя, {callback.from_user.username}!',
                                      reply_markup=await main_menu())
    await callback.answer()


'''Кнопка вперед'''


@router.callback_query(F.data.endswith('forward'))
async def forward_command(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    if callback.data.split('_')[0] == 'goalkeepers':
        goalkeepers = await get_goalkeepers()
        pg = await state.get_data()
        pg = pg['page']
        if pg + 1 < len(goalkeepers):
            await state.update_data(page=pg + 1)
            pg += 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=goalkeepers[pg]['img'],
                                                               caption=caption_players(0, pg, goalkeepers)),
                                         reply_markup=create_pg_kb_command('goalkeepers', 'backward',
                                                                           f'{pg + 1} / {len(goalkeepers)}',
                                                                           'forward'))
    elif callback.data.split('_')[0] == PLAYERS['forward']:
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        pg = await state.get_data()
        pg = pg['page']
        if pg + 1 < len(players):
            await state.update_data(page=pg + 1)
            pg += 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=players[pg]['img'],
                                                               caption=caption_players(1, pg, players)),
                                         reply_markup=create_pg_kb_command(PLAYERS['forward'], 'backward',
                                                                           f'{pg + 1} / {len(players)}',
                                                                           'forward'))
    else:
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        pg = await state.get_data()
        pg = pg['page']
        if pg + 1 < len(players):
            await state.update_data(page=pg + 1)
            pg += 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=players[pg]['img'],
                                                               caption=caption_players(1, pg, players)),
                                         reply_markup=create_pg_kb_command(PLAYERS['defender'], 'backward',
                                                                           f'{pg + 1} / {len(players)}',
                                                                           'forward'))
    await callback.answer()


'''Кнопка назад'''


@router.callback_query(F.data.endswith('backward'), )
async def forward_command(callback: CallbackQuery, state: FSMContext):
    if callback.data.split('_')[0] == 'goalkeepers':
        goalkeepers = await get_goalkeepers()
        pg = await state.get_data()
        pg = pg['page']
        if pg > 0:
            await state.update_data(page=pg - 1)
            pg -= 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=goalkeepers[pg]['img'],
                                                               caption=caption_players(0, pg, goalkeepers)),
                                         reply_markup=create_pg_kb_command('goalkeepers', 'backward',
                                                                           f'{pg + 1} / {len(goalkeepers)}',
                                                                           'forward'))
    elif callback.data.split('_')[0] == PLAYERS['forward']:
        players = await get_players(PLAYERS['forward'], callback.from_user.id)
        pg = await state.get_data()
        pg = pg['page']
        if pg > 0:
            await state.update_data(page=pg - 1)
            pg -= 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=players[pg]['img'],
                                                               caption=caption_players(1, pg, players)),
                                         reply_markup=create_pg_kb_command(PLAYERS['forward'], 'backward',
                                                                           f'{pg + 1} / {len(players)}',
                                                                           'forward'))
    else:
        players = await get_players(PLAYERS['defender'], callback.from_user.id)
        pg = await state.get_data()
        pg = pg['page']
        if pg > 0:
            await state.update_data(page=pg - 1)
            pg -= 1
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=players[pg]['img'],
                                                               caption=caption_players(1, pg, players)),
                                         reply_markup=create_pg_kb_command(PLAYERS['defender'], 'backward',
                                                                           f'{pg + 1} / {len(players)}',
                                                                           'forward'))
    await callback.answer()


'''Функция вывода информации о игроке'''


def caption_players(N, pg, player):
    if N:
        text = f'👤{player[pg]["name"]}\n' \
               f'{Attributes_players["attack"]}: {player[pg]["attack"]}\n' \
               f'{Attributes_players["endurance"]}: {player[pg]["endurance"]}\n' \
               f'{Attributes_players["power"]}: {player[pg]["power"]}\n' \
               f'{Attributes_players["defense"]}: {player[pg]["defense"]}'
    else:
        text = f'👤{player[pg]["name"]}\n' \
               f'{Attributes_goalkeepers["reliability"]}:{"{:.1f}".format(player[pg]["reliability"])}\n' \
               f'{Attributes_goalkeepers["endurance"]}: {player[pg]["endurance"]}\n' \
               f'{Attributes_goalkeepers["defense"]}: {player[pg]["defense"]}'
    return text


'''Кнопка меню'''
@router.message(F.text == '⚙️МЕНЮ')
async def menu_commands(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    command = await get_name_commands_id(message.from_user.id)
    text = f"🌟<b><u>{command['name']}</u></b>🌟\n" \
           f"🎮Игр: {command['count']}\n" \
           f"🏒Шайбы: {command['pucks_scored']}-{command['missed_pucks']}\n" \
           f"📊Очки: {command['points']}"
    await message.answer(text=text, reply_markup=await main_menu())