import asyncpg

from environs import Env

from lexicon.lexicon_ru import PLAYERS

env = Env()
env.read_env()

'''Получение информации об пользователи'''


async def get_user(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        users = await conn.fetchrow(f"SELECT * FROM users WHERE tg_id = '{id}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return users
            print('[INFO] PostgresSQL closed')


'''Добавление пользователя'''


async def add_users(tg_id, username):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO users(tg_id, user_name) 
                          VALUES($1, $2)''',
                           tg_id, username)

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Дабавление карточки'''


async def add_card_players(new_card):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO players(img, name, position, attack, endurance, power, defense, pur_price, sal_price) 
                          VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)''',
                           new_card['img'], new_card['name'], new_card['position'], new_card['attack'],
                           new_card['endurance'], new_card['power'], new_card['defense'], new_card['pur_price'],
                           new_card['sal_price'])

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Добавление карточки вратаря'''


async def add_card_goalkeeper(new_card):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO goalkeepers(img, name, reliability, endurance, defense, pur_price, sal_price) 
                          VALUES($1, $2, $3, $4, $5, $6, $7)''',
                           new_card['img'], new_card['name'], new_card['reliability'], new_card['endurance'],
                           new_card['defense'], new_card['pur_price'], new_card['sal_price'])

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Получение всех голкиперов на стартовый набор'''

async def get_goalkeepers():
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeepers = await conn.fetch(f"SELECT * FROM goalkeepers WHERE start_player = 'True'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return goalkeepers
            print('[INFO] PostgresSQL closed')


'''Список команд'''


async def get_name_commands(name):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = await conn.fetchrow(f"SELECT * FROM team WHERE name = '{name}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return command
            print('[INFO] PostgresSQL closed')


'''Проверка существует ли команда'''

async def get_name_commands_id(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = await conn.fetchrow(f"SELECT * FROM team WHERE tg_id = {id}")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return command
            print('[INFO] PostgresSQL closed')


'''Выбор нападающий и игроков'''
async def get_players(position, user_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = await conn.fetch(f"SELECT *"
                                   f"FROM players "
                                   f"WHERE players.position = '{position}' AND players.start_player = 'true' "
                                   f"AND NOT EXISTS ("
                                   f"SELECT 1 "
                                   f"FROM players_user "
                                   f"WHERE players.id = players_user.id_players "
                                   f"AND players_user.id_user = {user_id}"
                                   f")")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return command
            print('[INFO] PostgresSQL closed')


'''Добавление карточек'''

async def add_card_user(user_id, id_card, pos):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO players_user(id_user, id_players, position) 
                          VALUES($1, $2, $3)''',
                           user_id, id_card, pos)

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Добавление команды'''


async def add_command(new_command, user_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO team(tg_id, name, goalkeeper, forward_1, forward_2, forward_3, 
                                                defender_1, defender_2) 
                          VALUES($1, $2, $3, $4, $5, $6, $7, $8)''',
                           user_id, new_command['name'], new_command['goalkeepers'], new_command['forward_1'],
                           new_command['forward_2'], new_command['forward_3'], new_command['defender_1'],
                           new_command['defender_2'])

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Обновление готовности к игре'''


async def up_command_ready(id, points, my_gol, opp_gol):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.fetch(f"UPDATE team SET ready = 'False', game_date = 'now()',"
                         f"pucks_scored = pucks_scored + {my_gol}, missed_pucks = missed_pucks + {opp_gol}, "
                         f"points = points + {points}, count = count + 1 "
                         f" WHERE tg_id = '{id}';")



    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Получение данных и моей команде'''

async def get_my_commands(tg_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = []
        goalkeeper = await conn.fetchrow(f"SELECT team.name as t_name, goalkeepers.img, goalkeepers.name, goalkeepers.reliability, "
                                      f"goalkeepers.endurance, goalkeepers.defense "
                                      f"FROM team "
                                      f"JOIN goalkeepers "
                                      f"ON team.goalkeeper = goalkeepers.id AND team.tg_id = {tg_id};")
        command.append(goalkeeper)

        for i in range(3):
            forward = await conn.fetchrow(f"SELECT team.name as t_name, players.img, players.name, players.attack, "
                                          f"players.endurance, players.power, players.defense "
                                          f"FROM team "
                                          f"JOIN players "
                                          f"ON team.forward_{i+1} = players.id AND team.tg_id = {tg_id};")
            command.append(forward)

        for i in range(2):
            forward = await conn.fetchrow(f"SELECT team.name as t_name, players.img, players.name, players.attack, "
                                          f"players.endurance, players.power, players.defense "
                                          f"FROM team "
                                          f"JOIN players "
                                          f"ON team.defender_{i+1} = players.id AND team.tg_id = {tg_id};")
            command.append(forward)

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return command
            print('[INFO] PostgresSQL closed')

'''Команда противника'''
async def get_opp_commands(tg_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = []
        id_commands = await conn.fetchrow(f"SELECT tg_id FROM users WHERE tg_id != {tg_id} ORDER BY random() LIMIT 1")


        goalkeeper = await conn.fetchrow(f"SELECT team.name as t_name, goalkeepers.name, goalkeepers.reliability, "
                                      f"goalkeepers.endurance, goalkeepers.defense "
                                      f"FROM team "
                                      f"JOIN goalkeepers "
                                      f"ON team.goalkeeper = goalkeepers.id AND team.tg_id = {id_commands['tg_id']};")
        command.append(goalkeeper)

        for i in range(3):
            forward = await conn.fetchrow(f"SELECT team.name as t_name, players.name, players.attack, "
                                          f"players.endurance, players.power, players.defense "
                                          f"FROM team "
                                          f"JOIN players "
                                          f"ON team.forward_{i+1} = players.id AND team.tg_id = {id_commands['tg_id']};")
            command.append(forward)

        for i in range(2):
            forward = await conn.fetchrow(f"SELECT team.name as t_name, players.name, players.attack, "
                                          f"players.endurance, players.power, players.defense "
                                          f"FROM team "
                                          f"JOIN players "
                                          f"ON team.defender_{i+1} = players.id AND team.tg_id = {id_commands['tg_id']};")
            command.append(forward)

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return command
            print('[INFO] PostgresSQL closed')





'''Получение голкипера для отображения'''
async def get_goalkeeper_page():
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeeper = await conn.fetchrow(f"SELECT * FROM goalkeepers")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return goalkeeper
            print('[INFO] PostgresSQL closed')



'''Получение нападающих и защитников для отображения'''
async def get_players_page(category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeeper = await conn.fetchrow(f"SELECT * FROM players WHERE position = '{category}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return goalkeeper
            print('[INFO] PostgresSQL closed')


'''Получение игроков пользователя'''
async def get_user_players(user_id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        card = await conn.fetch(f"SELECT id_players FROM players_user WHERE position = '{category}' AND id_user = {user_id}")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return card
            print('[INFO] PostgresSQL closed')


'''Количество строк'''
async def len_card(id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))


        if category == PLAYERS['goalkeeper']:
            count_len = await conn.fetchrow("SELECT count(*) FROM goalkeepers")
            pg = await conn.fetchrow(f"SELECT count(*) as row_number FROM goalkeepers WHERE id <= {id}")
        else:
            count_len = await conn.fetchrow(f"SELECT count(*) FROM players WHERE position = '{category}'")
            pg = await conn.fetchrow(f"SELECT count(*) as row_number FROM players WHERE id <= {id} AND position = '{category}'")



    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return count_len, pg
            print('[INFO] PostgresSQL closed')



'''Листание страниц'''
'''Вперед голкипер'''

async def get_goalkeeper_next(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeeper = await conn.fetchrow(f"SELECT * FROM goalkeepers "
                                         f"WHERE EXISTS ("
                                         f"SELECT 1 "
                                         f"FROM goalkeepers "
                                         f"WHERE id = {id}) AND id > {id} "
                                         f"ORDER BY id LIMIT 1")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return goalkeeper
            print('[INFO] PostgresSQL closed')

'''Вперед нападающий и защитник'''
async def get_players_next_page(id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        player = await conn.fetchrow(f"SELECT * FROM players "
                                         f"WHERE EXISTS ("
                                         f"SELECT 1 "
                                         f"FROM players "
                                         f"WHERE position = '{category}' AND id = {id}) AND id > {id} "
                                         f"ORDER BY id LIMIT 1")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return player
            print('[INFO] PostgresSQL closed')

'''Назад голкипер'''
async def get_goalkeeper_previous(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeeper = await conn.fetchrow(f"SELECT * FROM goalkeepers "
                                         f"WHERE id < {id} "
                                         f"ORDER BY id DESC "
                                         f"LIMIT 1")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return goalkeeper
            print('[INFO] PostgresSQL closed')


'''Нападающий и защитник назад'''
async def get_players_previous_page(id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        player = await conn.fetchrow(f"SELECT * FROM players "
                                         f"WHERE position = '{category}' AND id < {id} "
                                         f"ORDER BY id DESC "
                                         f"LIMIT 1")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return player
            print('[INFO] PostgresSQL closed')


'''Получение баланса пользователя'''
async def get_balance(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        balance = await conn.fetchrow(f"SELECT balance FROM users "
                                         f"WHERE tg_id = {id}")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return balance
            print('[INFO] PostgresSQL closed')



'''Узнаем цену карточки'''
async def get_price_card(category, id, Q): #Категория, id карточки и что хотим сделать продать или купить
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        if category == PLAYERS['goalkeeper']:
            if Q == 1:
                price = await conn.fetchrow(f"SELECT pur_price FROM goalkeepers "
                                             f"WHERE id = {id}")
            else:
                price = await conn.fetchrow(f"SELECT sal_price FROM goalkeepers "
                                            f"WHERE id = {id}")
        else:
            if Q == 1:
                price = await conn.fetchrow(f"SELECT pur_price FROM players "
                                             f"WHERE id = {id} AND position='{category}'")
            else:
                price = await conn.fetchrow(f"SELECT sal_price FROM players "
                                            f"WHERE id = {id} AND position='{category}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return price
            print('[INFO] PostgresSQL closed')

'''Проверка есть ли такая карта в команде'''
async def get_card_user(tg_id, category, card_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))
        if category == PLAYERS['goalkeeper']:
            card = await conn.fetchrow(f"SELECT * FROM team "
                                             f"WHERE tg_id = {tg_id} AND goalkeeper = {card_id}")
        elif category == PLAYERS['forward']:
            card = await conn.fetchrow(f"SELECT * FROM team WHERE tg_id = {tg_id} AND (forward_1 = {card_id} OR forward_2 = {card_id} OR forward_3 = {card_id})")
        else:
            card = await conn.fetchrow(f"SELECT * FROM team WHERE tg_id = {tg_id} AND (defender_1 = {card_id} OR defender_2 = {card_id})")


    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return card
            print('[INFO] PostgresSQL closed')


'''Обновление баланса'''
async def up_balance_user(tg_id, price):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.fetchrow(f"UPDATE users SET balance = balance + {price} WHERE tg_id = {tg_id}")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')

'''Удаление карточки у игрока'''
async def card_del_user(tg_id, category, id_card):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.fetchrow(f"DELETE FROM players_user WHERE id_user = {tg_id} AND id_players = {id_card} AND position = '{category}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')