from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto

from bot_menu.menu import create_inline_kb, create_pg_kb_players, main_menu
from create_bot import bot
from database.orm import get_goalkeeper_page, get_user_players, len_card, get_players_page, get_goalkeeper_next, \
    get_goalkeeper_previous, get_players_next_page, get_players_previous_page, get_name_commands_id, get_balance, \
    get_price_card, get_card_user, add_card_user, up_balance_user, card_del_user
from lexicon.lexicon_ru import PLAYERS, PAGE, Attributes_players, Attributes_goalkeepers, Price

router: Router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")



'''Кнопака игроки'''
@router.callback_query(F.data.endswith('players'))
async def choice_player(callback: CallbackQuery):
    await callback.message.answer(text='Позиции игроков', reply_markup=create_inline_kb(1, 'ch_pl_', PLAYERS['forward'],
                                                                                        PLAYERS['defender'],
                                                                                        PLAYERS['goalkeeper'], PAGE['back']))
    await callback.answer()


'''Выбор позиции для отображения'''
@router.callback_query(F.data.startswith('ch_pl_'))
async def choice_player(callback: CallbackQuery):
    if callback.data.split('_')[-1] == PLAYERS['goalkeeper']:
        goalkeeper = await get_goalkeeper_page()
        user_goalkeeper = await get_user_players(callback.from_user.id, callback.data.split('_')[-1])
        price = f"{Price['buy']}: {goalkeeper['pur_price']}"
        len_pl = await len_card(goalkeeper['goalkeeper_id'], PLAYERS['goalkeeper'])
        for i in range(len(user_goalkeeper)):
            if user_goalkeeper[i]['player_id'] == goalkeeper['goalkeeper_id']:
                price = f"{Price['sell']}: {goalkeeper['sal_price']}"
        await bot.send_photo(chat_id=callback.from_user.id,
                             photo=goalkeeper['img'],
                             reply_markup=create_pg_kb_players(f"pg_card_{callback.data.split('_')[-1]}_{goalkeeper['goalkeeper_id']}", price,
                                                               'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}', 'forward'))

    elif callback.data.split('_')[-1] == PAGE['back']:
        command = await get_name_commands_id(callback.from_user.id)
        text = f"🌟<b><u>{command['name']}</u></b>🌟\n" \
               f"🎮Игр: {command['count']}\n" \
               f"🏒Шайбы: {command['pucks_scored']}-{command['missed_pucks']}\n" \
               f"📊Очки: {command['points']}"
        await callback.message.edit_text(text=text, reply_markup=await main_menu())

    else:
        players = await get_players_page(callback.data.split('_')[-1])
        user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[-1])
        price = f"{Price['buy']}: {players['pur_price']}"
        len_pl = await len_card(players['player_id'], callback.data.split('_')[-1])
        for i in range(len(user_players)):
            if user_players[i]['player_id'] == players['player_id']:
                price = f"{Price['sell']}: {players['sal_price']}"
        await bot.send_photo(chat_id=callback.from_user.id,
                             photo=players['img'],
                             reply_markup=create_pg_kb_players(
                                 f"pg_card_{callback.data.split('_')[-1]}_{players['player_id']}", price,
                                 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}', 'forward'))
    await callback.answer()


'''Листание страниц'''
@router.callback_query(F.data.startswith('pg_card_'))
async def paging_card(callback: CallbackQuery):
    if callback.data.split('_')[-1] == 'forward':
        if callback.data.split('_')[2] == PLAYERS['goalkeeper']:
            goalkeeper = await get_goalkeeper_next(int(callback.data.split('_')[-2]))
            if goalkeeper:
                user_goalkeeper = await get_user_players(callback.from_user.id, callback.data.split('_')[2])
                price = f"{Price['buy']}: {goalkeeper['pur_price']}"
                len_pl = await len_card(goalkeeper['goalkeeper_id'], PLAYERS['goalkeeper'])
                for i in range(len(user_goalkeeper)):
                    if user_goalkeeper[i]['player_id'] == goalkeeper['goalkeeper_id']:
                        price = f"{Price['sell']}: {goalkeeper['sal_price']}"

                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=goalkeeper['img']),
                                                                       reply_markup=create_pg_kb_players(
                                                                           f"pg_card_{callback.data.split('_')[2]}_{goalkeeper['goalkeeper_id']}",
                                                                           price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                                           'forward'))
        else:
            players = await get_players_next_page(int(callback.data.split('_')[-2]), callback.data.split('_')[2])
            if players:
                user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[2])
                price = f"{Price['buy']}: {players['pur_price']}"
                len_pl = await len_card(players['player_id'], callback.data.split('_')[2])
                for i in range(len(user_players)):
                    if user_players[i]['player_id'] == players['player_id']:
                        price = f"{Price['sell']}: {players['sal_price']}"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players['img']),
                                             reply_markup=create_pg_kb_players(
                                                 f"pg_card_{callback.data.split('_')[2]}_{players['player_id']}",
                                                 price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                 'forward'))
    else:
        if callback.data.split('_')[2] == PLAYERS['goalkeeper']:
            goalkeeper = await get_goalkeeper_previous(int(callback.data.split('_')[-2]))
            if goalkeeper:
                user_goalkeeper = await get_user_players(callback.from_user.id, callback.data.split('_')[2])
                price = f"{Price['buy']}: {goalkeeper['pur_price']}"
                len_pl = await len_card(goalkeeper['goalkeeper_id'], PLAYERS['goalkeeper'])
                for i in range(len(user_goalkeeper)):
                    if user_goalkeeper[i]['player_id'] == goalkeeper['goalkeeper_id']:
                        price = f"{Price['sell']}: {goalkeeper['sal_price']}"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=goalkeeper['img']),
                                                                       reply_markup=create_pg_kb_players(
                                                                           f"pg_card_{callback.data.split('_')[2]}_{goalkeeper['goalkeeper_id']}",
                                                                           price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                                           'forward'))
        else:
            players = await get_players_previous_page(int(callback.data.split('_')[-2]), callback.data.split('_')[2])
            if players:
                user_players = await get_user_players(callback.from_user.id, callback.data.split('_')[2])
                price = f"{Price['buy']}: {players['pur_price']}"
                len_pl = await len_card(players['player_id'], callback.data.split('_')[2])
                for i in range(len(user_players)):
                    if user_players[i]['player_id'] == players['player_id']:
                        price = f"{Price['sell']}: {players['sal_price']}"
                await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                             media=InputMediaPhoto(media=players['img']),
                                             reply_markup=create_pg_kb_players(
                                                 f"pg_card_{callback.data.split('_')[2]}_{players['player_id']}",
                                                 price, 'backward', f'{len_pl[1]["row_number"]} / {len_pl[0]["count"]}',
                                                 'forward'))

    await callback.answer()

'''Продать или купить'''
@router.callback_query(F.data.startswith('price_'))
async def price_card(callback: CallbackQuery):
    if callback.data.split('_')[1] == Price['buy']:
        balance_user = await get_balance(callback.from_user.id)
        price_players = await get_price_card(callback.data.split('_')[2], callback.data.split('_')[-1], 1)
        if balance_user['balance'] > price_players['pur_price']:
            await callback.answer("Поздравляю с приобретением", show_alert=True)
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await add_card_user(callback.from_user.id, int(callback.data.split('_')[-1]), callback.data.split('_')[2])
            await up_balance_user(callback.from_user.id, -(price_players['pur_price']))
        else:
            await callback.answer("К сожалению Вам не хватает средств для покупки", show_alert=True)
    else:
        players = await get_card_user(callback.from_user.id, callback.data.split('_')[2], int(callback.data.split('_')[-1]))
        price_players = await get_price_card(callback.data.split('_')[2], int(callback.data.split('_')[-1]), 0)
        if players:
            await callback.answer("Этот игрок является частью вашей хоккейной команды.\n"
                                  "Если вы рассматриваете продажу игрока, рекомендуется сначала найти замену для него",
                                  show_alert=True)
        else:
            await callback.answer("Игрок успешно продан", show_alert=True)
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await card_del_user(callback.from_user.id, callback.data.split('_')[2], int(callback.data.split('_')[-1]))
            await up_balance_user(callback.from_user.id, price_players['sal_price'])

    await callback.answer()





