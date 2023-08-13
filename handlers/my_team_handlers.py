from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message

from bot_menu.menu import create_inline_kb, create_pg_kb_players, main_menu, kb_team
from create_bot import bot
from database.orm import get_goalkeeper_page, get_user_players, len_card, get_players_page, get_goalkeeper_next, \
    get_goalkeeper_previous, get_players_next_page, get_players_previous_page, get_name_commands_id, get_balance, \
    get_price_card, get_card_user, add_card_user, up_balance_user, card_del_user, get_my_commands, get_players_team
from handlers.players_handlers import caption_players
from lexicon.lexicon_ru import PLAYERS, PAGE, Attributes_players, Attributes_goalkeepers, Price

router: Router = Router()


'''Кнопка команда в боте'''
@router.callback_query(F.data == 'commands')
async def choice_menu(callback: CallbackQuery):
    pg = 0
    my_commands = await get_my_commands(callback.from_user.id)
    await bot.send_photo(chat_id=callback.from_user.id,
                         photo=my_commands[pg]['img'],
                         caption=f'🌟<b><u>{my_commands[pg]["t_name"]}</u></b>🌟\n'
                                 +caption_players(0, my_commands[pg]),
                         reply_markup=kb_team(
                             f"my_team_{pg}", PLAYERS['goalkeeper'],
                             'backward', PAGE['replace'], 'forward'))
    await callback.answer()


'''Кнопка вперед'''

@router.callback_query(F.data.startswith('my_team_'))
async def my_team_page(callback: CallbackQuery):
    print(callback.data)
    my_commands = await get_my_commands(callback.from_user.id)
    if callback.data.split("_")[-1] == 'forward':
        pg = int(callback.data.split("_")[2])
        if pg+1 < len(my_commands):
            pg += 1
            if pg > 3:
                N = 1
                pos = PLAYERS['defender']
            elif pg > 0:
                N = 1
                pos = PLAYERS['forward']
            else:
                N = 0
                pos = PLAYERS['goalkeeper']

            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=my_commands[pg]['img'],
                                                               caption=f'🌟<b><u>{my_commands[pg]["t_name"]}</u></b>🌟\n'
                                                                        + caption_players(N, my_commands[pg])),
                                         reply_markup=kb_team(f"my_team_{pg}", pos,
                                                             'backward', PAGE['replace'], 'forward'))

    elif callback.data.split("_")[-1] == 'backward':
        pg = int(callback.data.split("_")[2])
        if pg > 0:
            pg -= 1
            if pg > 3:
                N = 1
                pos = PLAYERS['defender']
            elif pg > 0:
                N = 1
                pos = PLAYERS['forward']
            else:
                N = 0
                pos = PLAYERS['goalkeeper']
            await bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                         media=InputMediaPhoto(media=my_commands[pg]['img'],
                                                               caption=f'🌟<b><u>{my_commands[pg]["t_name"]}</u></b>🌟\n'
                                                                       + caption_players(N, my_commands[pg])),
                                         reply_markup=kb_team(f"my_team_{pg}", pos,
                                                              'backward', PAGE['replace'], 'forward'))
    elif callback.data.split("_")[-1] == PAGE['replace']:
        if callback.data.split('_')[-2] == PLAYERS['goalkeeper']:
            players = await get_players_team(callback.from_user.id,
                                             int(callback.data.split("_")[2]))
            if players:
                pg = 0
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                                 media=InputMediaPhoto(media=players[pg]['img'],
                                                                           caption=caption_players(0, players[pg])),
                                                                           reply_markup=create_pg_kb_players(
                                                                               f"ch_team_{pg}_{callback.data.split('_')[-2]}",
                                                                               PAGE['choice'], 'backward', f'{pg+1} / {len(players)}',
                                                                               'forward'))
        else:
            players = await get_players_team(callback.from_user.id,
                                             int(callback.data.split("_")[2]))
            if players:
                pg = 0
            print(players)
            # players = await get_players_page(callback.data.split('_')[-2])
            # user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[-2])
            # price = f"✅Выбрать"
            # len_pl = await len_card(players['id'], callback.data.split('_')[-2])
            # for i in range(len(user_players)):
            #     if user_players[i]['id_players'] == players['id']:
            #         price = f"🌟Уже в команде"
            # await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
            #                              media=InputMediaPhoto(media=players['img'],
            #                                                    caption=caption_players(1, players)),
            #                              reply_markup=create_pg_kb_players(
            #                                  f"ch_team_0_{players['id']}_{callback.data.split('_')[-2]}",
            #                                  PAGE['choice'], 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
            #                                  'forward'))
    await callback.answer()


'''Листание страниц'''
@router.callback_query(F.data.startswith('ch_team_'))
async def paging_card(callback: CallbackQuery):
    print(callback.data)
    if callback.data.split('_')[-1] == 'forward':
        if callback.data.split('_')[-2] == PLAYERS['goalkeeper']:
            goalkeeper = await get_goalkeeper_next(int(callback.data.split('_')[3]))
            if goalkeeper:
                user_goalkeeper = await get_user_players(callback.from_user.id, callback.data.split('_')[-2])
                price = f"✅Выбрать"
                len_pl = await len_card(goalkeeper['id'], PLAYERS['goalkeeper'])
                for i in range(len(user_goalkeeper)):
                    if user_goalkeeper[i]['id_players'] == goalkeeper['id']:
                        price = f"🌟Уже в команде"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=goalkeeper['img'],
                                                                       caption=caption_players(0, goalkeeper)),
                                                                       reply_markup=create_pg_kb_players(
                                                                           f"ch_team_0_{goalkeeper['id']}_{callback.data.split('_')[-2]}",
                                                                           price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                                           'forward'))
        else:
            players = await get_players_next_page(int(callback.data.split('_')[3]), callback.data.split('_')[-2])
            if players:
                user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[-2])
                price = f"✅Выбрать"
                len_pl = await len_card(players['id'], callback.data.split('_')[-2])
                for i in range(len(user_players)):
                    if user_players[i]['id_players'] == players['id']:
                        price = f"🌟Уже в команде"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players['img'],
                                                                   caption=caption_players(1, players)),
                                             reply_markup=create_pg_kb_players(
                                                 f"ch_team_0_{players['id']}_{callback.data.split('_')[-2]}",
                                                 price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                 'forward'))
    else:
        if callback.data.split('_')[-2] == PLAYERS['goalkeeper']:
            goalkeeper = await get_goalkeeper_previous(int(callback.data.split('_')[3]))
            if goalkeeper:
                user_goalkeeper = await get_user_players(callback.from_user.id, callback.data.split('_')[-2])
                price = f"✅Выбрать"
                len_pl = await len_card(goalkeeper['id'], PLAYERS['goalkeeper'])
                for i in range(len(user_goalkeeper)):
                    if user_goalkeeper[i]['id_players'] == goalkeeper['id']:
                        price = f"🌟Уже в команде"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=goalkeeper['img'],
                                                                       caption=caption_players(0, goalkeeper)),
                                                                       reply_markup=create_pg_kb_players(
                                                                           f"ch_team_0_{goalkeeper['id']}_{callback.data.split('_')[-2]}",
                                                                           price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                                           'forward'))
        else:
            players = await get_players_previous_page(int(callback.data.split('_')[3]), callback.data.split('_')[-2])
            if players:
                user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[-2])
                price = f"✅Выбрать"
                len_pl = await len_card(players['id'], callback.data.split('_')[-2])
                for i in range(len(user_players)):
                    if user_players[i]['id_players'] == players['id']:
                        price = f"🌟Уже в команде"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players['img'],
                                                                   caption=caption_players(1, players)),
                                             reply_markup=create_pg_kb_players(
                                                 f"ch_team_0_{players['id']}_{callback.data.split('_')[-2]}",
                                                 price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                 'forward'))

    await callback.answer()

'''Кнопка команда в чате'''
@router.message(F.text=='🥅Команда')
async def choice_menu(message: Message):
    pass

