from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from bot_menu.menu import kb_team, create_pg_choice_players
from create_bot import bot
from database.orm import get_my_commands, get_players_team, \
    update_team
from lexicon.lexicon_ru import PLAYERS, PAGE

router: Router = Router()


'''Кнопка команда в боте'''
@router.callback_query(F.data == 'commands')
async def choice_menu(callback: CallbackQuery):
    pg = 0
    my_commands = await get_my_commands(callback.from_user.id)
    print(my_commands)
    await bot.send_photo(chat_id=callback.from_user.id,
                         photo=my_commands[pg]['g_img'],
                         reply_markup=kb_team(
                             f"my_team_{pg}", PLAYERS['goalkeeper'],
                             'backward', PAGE['replace'], 'forward'))
    await callback.answer()


'''Кнопка вперед, назад и заменить'''
@router.callback_query(F.data.startswith('my_team_'))
async def my_team_page(callback: CallbackQuery):
    my_commands = await get_my_commands(callback.from_user.id)
    if callback.data.split("_")[-1] == 'forward':
        pg = int(callback.data.split("_")[2])
        if pg+1 <= len(my_commands):
            pg += 1
            if pg > 3:
                pg_b = pg -1
                pos = PLAYERS['defender']
                img = my_commands[pg_b]['p_img']
            elif pg > 0:
                pg_b = pg -1
                pos = PLAYERS['forward']
                img = my_commands[pg_b]['p_img']
            else:
                pg_b = 0
                pos = PLAYERS['goalkeeper']
                img = my_commands[pg_b]['g_img']

            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=img),
                                         reply_markup=kb_team(f"my_team_{pg}", pos,
                                                             'backward', PAGE['replace'], 'forward'))

    elif callback.data.split("_")[-1] == 'backward':
        pg = int(callback.data.split("_")[2])
        if pg > 0:
            pg -= 1
            if pg > 3:
                pg_b = pg -1
                N = 1
                pos = PLAYERS['defender']
                img = my_commands[pg_b]['p_img']
            elif pg > 0:
                pg_b = pg -1
                N = 1
                pos = PLAYERS['forward']
                img = my_commands[pg_b]['p_img']
            else:
                pg_b = 0
                N = 0
                pos = PLAYERS['goalkeeper']
                img = my_commands[pg_b]['g_img']
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=img),
                                         reply_markup=kb_team(f"my_team_{pg}", pos,
                                                              'backward', PAGE['replace'], 'forward'))
    #Заменить
    elif callback.data.split("_")[-1] == PAGE['replace']:
        my_tg_id = callback.from_user.id #Мой ид
        category = callback.data.split("_")[-2]
        players = await get_players_team(my_tg_id, category)
        if players:
            if int(callback.data.split("_")[2]) > 0:
                N = 1
            else:
                N = 0
            pg = 0
            await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players[pg]['img']),
                                                                       reply_markup=create_pg_choice_players(
                                                                           f"ch_team_{pg}_{callback.data.split('_')[2]}_{callback.data.split('_')[-2]}",
                                                                           PAGE['choice'], 'backward', f'{pg+1} / {len(players)}',
                                                                           'forward'))
        else:
            await callback.answer(text='❌У вас нет других игроков❌', show_alert=True)
    await callback.answer()


'''Листание страниц при замене'''
@router.callback_query(F.data.startswith('ch_team_'))
async def paging_card(callback: CallbackQuery):
    #Получение команды -> ИД и категория
    players = await get_players_team(callback.from_user.id,
                                     callback.data.split("_")[-2])
    pg = int(callback.data.split('_')[2])
    print(players)
    if callback.data.split('_')[-1] == 'forward':
        if players:
            if  pg < len(players)-1:
                pg = int(callback.data.split('_')[2]) + 1
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                                 media=InputMediaPhoto(media=players[pg]['img']),
                                                                           reply_markup=create_pg_choice_players(
                                                                               f"ch_team_{pg}_{callback.data.split('_')[3]}_{callback.data.split('_')[-2]}",
                                                                               PAGE['choice'], 'backward', f'{pg+1} / {len(players)}',
                                                                               'forward'))
    elif callback.data.split('_')[-1] == 'backward':
        if players:
            if pg > 0:
                pg = int(callback.data.split('_')[2]) - 1
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players[pg]['img']),
                                             reply_markup=create_pg_choice_players(
                                                 f"ch_team_{pg}_{callback.data.split('_')[3]}_{callback.data.split('_')[-2]}",
                                                 PAGE['choice'], 'backward', f'{pg + 1} / {len(players)}',
                                                 'forward'))

    #Выбор игрока при замене
    elif callback.data.split('_')[-1] == 'choice':
        await update_team(callback.from_user.id, players[pg]['player_id'], int(callback.data.split('_')[3]))
        pg = int(callback.data.split('_')[3])
        my_commands = await get_my_commands(callback.from_user.id)
        img = 'p_img'
        if pg > 3:
            pos = PLAYERS['defender']
            pg -= 1
        elif pg > 0:
            pos = PLAYERS['forward']
            pg -= 1
        else:
            pos = PLAYERS['goalkeeper']
            img = 'g_img'
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=my_commands[pg][img]),
                                     reply_markup=kb_team(f"my_team_{pg}", pos,
                                                          'backward', PAGE['replace'], 'forward'))
    else:
        pg = int(callback.data.split('_')[3])
        my_commands = await get_my_commands(callback.from_user.id)
        img = 'p_img'
        if pg > 3:
            pos = PLAYERS['defender']
        elif pg > 0:
            pos = PLAYERS['forward']
        else:
            pos = PLAYERS['goalkeeper']
            img = 'g_img'

        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                     media=InputMediaPhoto(media=my_commands[pg][img]),
                                     reply_markup=kb_team(f"my_team_{pg}", pos,
                                                          'backward', PAGE['replace'], 'forward'))
    await callback.answer()



'''Кнопка команда в чате'''
@router.message(F.text=='🥅Команда')
async def choice_menu(message: Message):
    pass

