import random
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from bot_menu.menu import main_menu, menu_user_private, menu_admin, create_pg_kb_command, menu_user
from create_bot import bot
from database.orm import get_user, add_users, get_goalkeepers, get_name_commands, get_name_commands_id, get_players, \
    add_card_user, add_command, up_command_ready, get_my_commands, get_opp_commands
from lexicon.lexicon_ru import Attributes_goalkeepers, PLAYERS, Attributes_players, PAGE

router: Router = Router()

'''Команда старт в группе'''


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    users = await get_user(message.from_user.id) #Данные о пользователи
    commands = await get_name_commands_id(message.from_user.id) # Данные о команде
    if users and commands:
        if users['admin']:
            await message.answer(text=f'🤝Приветствую тебя, {message.from_user.username}!',
                                 reply_markup=menu_user)
        else:
            await message.answer(text=f'🤝Приветствую тебя, {message.from_user.username}!',
                                 reply_markup=menu_user)
    else:
        await message.answer(text=f'🤝Приветствую тебя, {message.from_user.username}!\n'
                                  'Сначала создай команду по ссылке: @rus_hockey_bot')


'''Кнопка игра'''


@router.message(F.text == '🏒🥅ИГРА')
async def menu_commands(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    command = await get_name_commands_id(message.from_user.id)
    difference = datetime.now() - command['game_date']
    seconds = difference.total_seconds()
    hours = seconds / (60 * 60)
    minutes = seconds / 60
    if hours >= 24 or command['ready']:
        my_commands = await get_my_commands(message.from_user.id)
        opp_commands = await get_opp_commands(message.from_user.id)
        my_indicator = await get_indicators(my_commands)
        opp_indicator = await get_indicators(opp_commands)
        my_gol = 0
        opp_gol = 0
        if my_indicator[1] - opp_indicator[2] > 0:
            for i in range(my_indicator[1] - opp_indicator[2]):
                n = random.randint(1, 1000)
                if n > opp_indicator[0]:
                    my_gol += 1

        if opp_indicator[1] - my_indicator[2] > 0:
            for i in range(opp_indicator[1] - my_indicator[2]):
                n = random.randint(1, 1000)
                if n > my_indicator[0]:
                    opp_gol += 1

        if my_gol > opp_gol:
            await up_command_ready(message.from_user.id, 3, my_gol, opp_gol)  # Делаем готовность False, обновляем время на текущее
            await message.answer(text=f'{my_commands[0]["t_name"]}   <b><u>{my_gol}:{opp_gol}</u></b>   '
                                      f'{opp_commands[0]["t_name"]}\n\n'
                                      f'Хорошая работа! 🏒 Ты смог одержать победу в этой хоккейной игре!\n'
                                      f'Твой навык на льду и стратегические решения помогли тебе достичь успеха.\n'
                                      f'Поздравляю с этой выдающейся победой! 🎉🥳')
        elif my_gol == opp_gol:
            await up_command_ready(message.from_user.id, 1, my_gol, opp_gol)
            await message.answer(
                text=f'{my_commands[0]["t_name"]}   <b><u>{my_gol}:{opp_gol}</u></b>   '
                                      f'{opp_commands[0]["t_name"]}\n\n'
                     f'Ничья - это также уважаемый результат!\n'
                     f'В этом матче ты сумел удержать равновесие и завершить игру с равным счетом.\n'
                     f'Твоя способность адаптироваться к сопернику и держаться в тяжелых ситуациях '
                     f'заслуживает похвалы.\n'
                     f'Ничья показывает, что ты стоишь на равных соперником и способен справиться с '
                     f'любым испытанием на льду.\n'
                     f'Отличная работа! 🏒🤝💪 Продолжай развиваться и стремиться к новым высотам в следующих матчах!\n'
                     f'#NeverSettle')
        else:
            await up_command_ready(message.from_user.id, 0, my_gol, opp_gol)
            await message.answer(
                text=f'{my_commands[0]["t_name"]}   <b><u>{my_gol}:{opp_gol}</u></b>   '
                                      f'{opp_commands[0]["t_name"]}\n\n'
                     f'К сожалению, в этом матче тебе не удалось одержать победу. Но не отчаивайся!\n'
                     f'🏒💪 Поражение - это всего лишь временный результат, и оно дает тебе возможность '
                     f'изучить свои ошибки и стать еще лучше. Уверен, что ты сможешь восстановиться, '
                     f'тренироваться усерднее и достичь громких побед в будущих играх! 🥅🏆 \n#NeverGiveUp')



    else:
        await bot.send_message(chat_id=message.chat.id, text='Вы уже провели игру сегодня.\n'
                                                             f'Следующая игра доступна через {23 - int(hours)} часа {(59 - (int(minutes) % 60))} минут.')


'''Получение атаки'''

async def get_indicators(my_commands: list):
    attack = 0
    deffend = 0
    for i in range(1, 6):
        attack += int(my_commands[i]['attack']) + (
                    int(my_commands[i]['attack']) * (int(my_commands[i]['endurance'] / 1000)))
        deffend += int(my_commands[i]['defense']) + int(
            my_commands[i]['power'] + (int(my_commands[i]['power'] * int(my_commands[i]['endurance'] / 1000))))

    def_goalkeeper = "{:.0f}".format(float(my_commands[0]['defense']) + (float(my_commands[0]['defense']) *
                                                                         (float(my_commands[0]['reliability'] * (float(
                                                                             my_commands[0]['endurance'] / 10000))))))
    return int(def_goalkeeper), attack, deffend


