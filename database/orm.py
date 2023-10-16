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
        return users
    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

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

async def get_name_commands_id(tg_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = await conn.fetchrow(f"SELECT * "
                                      f"FROM team "
                                      f"JOIN users USING (user_id)"
                                      f"WHERE users.tg_id = {tg_id}")
        return command

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Выбор нападающий и игроков'''
async def get_players(position, user_id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        command = await conn.fetch(f'''
                                        SELECT *
                                        FROM players
                                        WHERE position = '{position}' -- замените 'нападающий' на желаемую позицию
                                            AND start_player = 'true'
                                            AND NOT EXISTS (
                                                SELECT 1
                                                FROM players_user
                                                WHERE players_user.player_id = players.player_id
                                                    AND players_user.user_id = (
                                                        SELECT user_id
                                                        FROM users
                                                        WHERE tg_id = {user_id} -- замените 'ваш_tg_id' на желаемый tg_id пользователя
                                                    )
                                                    AND players_user.position = '{position}'
                                            )
        ''')

        print(command)
        return command

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

            print('[INFO] PostgresSQL closed')


'''Добавление карточек'''

async def add_card_user(user_id, id_card, pos):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.execute(f'''INSERT INTO players_user(user_id, player_id, position) 
                                VALUES (
                                    (SELECT user_id FROM users WHERE tg_id = $1),
                                    $2,
                                    $3
                                )''',
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
        #user = await conn.fetchrow(f'''SELECT user_id FROM users WHERE tg_id = {user_id}''')
        await conn.execute(f'''INSERT INTO team(user_id, name, goalkeeper_id, forward_1, forward_2, forward_3, 
                                                defender_1, defender_2) 
                          VALUES((SELECT user_id FROM users WHERE tg_id = {user_id}), $1, $2, $3, $4, $5, $6, $7)''',
                           new_command['name'], new_command['goalkeepers'], new_command['forward_1'],
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


        teams = await conn.fetch(f'''SELECT team.id, team.user_id, team.name, team.ready, team.count, team.pucks_scored, 
                                            team.missed_pucks, team.points, g.img AS g_img, g.name AS g_name, g.reliability AS g_reliability, 
                                            g.endurance AS g_endurance, g.defense AS g_defense, g.pur_price AS g_pur_price, 
                                            g.sal_price AS g_sal_price, p.img AS p_img, p.name AS p_name, p.position AS p_position, 
                                            p.attack AS p_attack, p.endurance AS p_endurance, p.power AS p_power, p.defense AS p_defense, 
                                            p.pur_price AS p_pur_price, p.sal_price AS p_sal_price 
                                    FROM team 
                                    JOIN goalkeepers g USING (goalkeeper_id) 
                                    JOIN players p ON team.forward_1 = player_id 
                                                    OR team.forward_2 = player_id 
                                                    OR team.forward_3 = player_id 
                                                    OR team.defender_1 = player_id 
                                                    OR team.defender_2 = player_id 
                                    JOIN users USING (user_id) 
                                    WHERE users.tg_id = {tg_id} 
                                    ORDER BY CASE WHEN team.forward_1 = player_id 
                                    THEN 0 WHEN team.forward_2 = player_id THEN 1 
                                    WHEN team.forward_3 = player_id THEN 2 
                                    WHEN team.defender_1 = player_id THEN 3 
                                    WHEN team.defender_2 = player_id THEN 4 END
        ''')
        return teams

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
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
        return goalkeeper

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

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
async def get_user_players(tg_id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        card = await conn.fetch(f'''SELECT player_id 
                                    FROM players_user 
                                    JOIN users USING (user_id) 
                                    WHERE players_user.position = '{category}' AND users.tg_id = {tg_id}''')
        return card


    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Количество строк'''
async def len_card(id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))


        if category == PLAYERS['goalkeeper']:
            count_len = await conn.fetchrow("SELECT count(*) FROM goalkeepers")
            pg = await conn.fetchrow(f"SELECT count(*) as row_number FROM goalkeepers WHERE goalkeeper_id <= {id}")
        else:
            count_len = await conn.fetchrow(f"SELECT count(*) FROM players WHERE position = '{category}'")
            pg = await conn.fetchrow(f"SELECT count(*) as row_number FROM players WHERE player_id <= {id} AND position = '{category}'")
        return count_len, pg


    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

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
                                         f"WHERE goalkeeper_id = {id}) AND goalkeeper_id > {id} "
                                         f"ORDER BY goalkeeper_id LIMIT 1")
        return goalkeeper
    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

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
                                         f"WHERE position = '{category}' AND player_id = {id}) AND player_id > {id} "
                                         f"ORDER BY player_id LIMIT 1")
        return player


    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')

'''Назад голкипер'''
async def get_goalkeeper_previous(id):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        goalkeeper = await conn.fetchrow(f"SELECT * FROM goalkeepers "
                                         f"WHERE goalkeeper_id < {id} "
                                         f"ORDER BY goalkeeper_id DESC "
                                         f"LIMIT 1")
        return goalkeeper


    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')


'''Нападающий и защитник назад'''
async def get_players_previous_page(id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        player = await conn.fetchrow(f"SELECT * FROM players "
                                         f"WHERE position = '{category}' AND player_id < {id} "
                                         f"ORDER BY player_id DESC "
                                         f"LIMIT 1")
        return player

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()

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
                                             f"WHERE goalkeeper_id = {id}")
            else:
                price = await conn.fetchrow(f"SELECT sal_price FROM goalkeepers "
                                            f"WHERE goalkeeper_id = {id}")
        else:
            if Q == 1:
                price = await conn.fetchrow(f"SELECT pur_price FROM players "
                                             f"WHERE player_id = {id} AND position='{category}'")
            else:
                price = await conn.fetchrow(f"SELECT sal_price FROM players "
                                            f"WHERE player_id = {id} AND position='{category}'")

        return price

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
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

'''Удаление карточки у игрока при продаже'''
async def card_del_user(tg_id, category, id_card):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))

        await conn.fetchrow(f"DELETE FROM players_user WHERE user_id = {tg_id} AND player_id = {id_card} AND position = '{category}'")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')

'''Получение игроков для команды'''
async def get_players_team(tg_id, category):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))
        pl_def = await conn.fetchrow(f"SELECT * FROM team  WHERE tg_id = {tg_id}")

        if category == PLAYERS['defender']:
            players = await conn.fetch(f"SELECT players.id, players.img, players.name, players.attack, "
                                        f"players.endurance, players.power, players.defense "
                                       f"FROM players_user "
                                       f"JOIN players "
                                       f"ON players_user.player_id = players.id "
                                       f"AND players_user.user_id = {tg_id} "
                                       f"AND players_user.position = '{PLAYERS['defender']}' "
                                       f"AND players_user.player_id != {pl_def['defender_1']} "
                                       f"AND players_user.player_id != {pl_def['defender_2']};")
        elif category == PLAYERS['forward']:
            players = await conn.fetch(f"SELECT players.id, players.img, players.name, players.attack, "
                                       f"players.endurance, players.power, players.defense "
                                        f"FROM players_user "
                                        f"JOIN players "
                                        f"ON players_user.player_id = players.id "
                                       f"AND players_user.user_id = {tg_id} "
                                       f"AND players_user.position = '{PLAYERS['forward']}' "
                                       f"AND players_user.player_id != {pl_def['forward_1']} "
                                       f"AND players_user.player_id != {pl_def['forward_2']} "
                                       f"AND players_user.player_id != {pl_def['forward_3']};")
        else:
            players = await conn.fetch(f"SELECT goalkeepers.id, goalkeepers.img, goalkeepers.name, goalkeepers.reliability, "
                                        f"goalkeepers.endurance, goalkeepers.defense "
                                        f"FROM players_user "
                                        f"JOIN goalkeepers "
                                        f"ON players_user.player_id = goalkeepers.id "
                                       f"AND players_user.user_id = {tg_id} "
                                        f"AND players_user.position = '{PLAYERS['goalkeeper']}' "
                                       f"AND players_user.player_id != {pl_def['goalkeeper']};")

    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            return players
            print('[INFO] PostgresSQL closed')



'''Обновление игроков в команде'''
async def update_team(tg_id, card_user, old_card):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))
        if old_card == 0:
            await conn.fetchrow(f"UPDATE team SET goalkeeper = {card_user} WHERE tg_id = {tg_id}")
        elif old_card == 1:
            await conn.fetchrow(f"UPDATE team SET forward_1 = {card_user} WHERE tg_id = {tg_id}")
        elif old_card == 2:
            await conn.fetchrow(f"UPDATE team SET forward_2 = {card_user} WHERE tg_id = {tg_id}")
        elif old_card == 3:
            await conn.fetchrow(f"UPDATE team SET forward_3 = {card_user} WHERE tg_id = {tg_id}")
        elif old_card == 4:
            await conn.fetchrow(f"UPDATE team SET defender_1 = {card_user} WHERE tg_id = {tg_id}")
        elif old_card == 5:
            await conn.fetchrow(f"UPDATE team SET defender_2 = {card_user} WHERE tg_id = {tg_id}")






    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')



async def card_ava(tg_id: int, category: str, id: int, Q:int):
    try:
        conn = await asyncpg.connect(user=env('user'), password=env('password'), database=env('db_name'),
                                     host=env('host'))
        #Проверяем является ли это враталь или нападающий с защитником
        if category == PLAYERS['goalkeeper']:
            #проверяем наличие
            availability = await conn.fetchrow(f'''
                                                SELECT id
                                                FROM players_user
                                                WHERE position = '{category}' 
                                                        AND player_id = {id} 
                                                        AND user_id = (SELECT user_id FROM users WHERE tg_id = {tg_id})                                            
                                                 ''')
            #Если такой игрок есть
            if availability:
                #покупка
                if Q:
                    return 0
                #Продажа
                else:
                    sel_card = await conn.fetchrow(f'''
                                                        SELECT id
                                                        FROM team
                                                        WHERE goalkeeper_id = {availability['id']} 
                                                                AND user_id = (SELECT user_ID FROM users WHERE tg_id = {tg_id})
                    ''')
                    if not sel_card:
                        await conn.fetchrow(f'''UPDATE users 
                                                SET balance = balance + (SELECT sal_price 
                                                                        FROM goalkeepers 
                                                                        WHERE goalkeeper_id = {id}) 
                                                WHERE tg_id = {tg_id};
    
                                                DELETE FROM players_user
                                                WHERE user_id = (SELECT user_id FROM users WHERE tg_id = {tg_id} 
                                                    AND player_id = {id} AND position = '{category}'
                        ''')
                        return 1
                    else:
                        return 2

            #Такого игрока у вас нет
            else:
                #Покупка
                if Q:
                    #Проверка хватает ли денег на покупку
                    bay_card = await conn.fetchrow('''
                                            SELECT EXISTS (
                                                SELECT 1
                                                FROM users
                                                JOIN goalkeepers ON (users.balance > goalkeepers.pur_price)
                                                WHERE users.tg_id = $1
                                                AND goalkeepers.goalkeeper_id = $2
                                            )
                                        ''', tg_id, id)

                    #Если хватает денег на покупку
                    if bay_card[0]:
                        await conn.fetchrow(f'''UPDATE users 
                                                    SET balance = balance - (SELECT pur_price 
                                                                                FROM goalkeepers 
                                                                                WHERE goalkeeper_id = {id}) 
                                                    WHERE tg_id = {tg_id};
                                                    
                                                ''')
                        await conn.execute(f'''INSERT INTO players_user(user_id, player_id, position) 
                                                        VALUES (
                                                            (SELECT user_id FROM users WHERE tg_id = $1),
                                                            $2,
                                                            $3
                                                        )''',
                                           tg_id, id, category)
                        return 1
                    #Если не хватает денег на покупку
                    else:
                        return 2
                else:
                    return 0
        # Если это защитники или нападающий
        else:
            #проверяем наличие
            availability = await conn.fetchrow(f'''
                                            SELECT id
                                            FROM players_user
                                            WHERE position = '{category}' 
                                                    AND player_id = {id} 
                                                    AND user_id = (SELECT user_id FROM users WHERE tg_id = {tg_id})                                            
                                             ''')
            #Если такой игрок есть
            print(availability)
            if availability:
                #Покупка
                if Q:
                    return 0
                #Продажа
                else:
                    #Проверяем является ли игрок частью команды
                    sel_card = await conn.fetchrow(f'''
                                                        SELECT id
                                                        FROM team
                                                        WHERE (forward_1 = {availability['id']} 
                                                                OR forward_2 = {availability['id']} 
                                                                OR forward_3 = {availability['id']} 
                                                                OR defender_1 = {availability['id']} 
                                                                OR defender_2 = {availability['id']}) 
                                                                AND user_id = (SELECT user_ID FROM users WHERE tg_id = {tg_id})
                    ''')
                    if not sel_card:

                        await conn.fetchrow(f'''UPDATE users 
                                               SET balance = balance + (SELECT pur_price 
                                                                       FROM players 
                                                                       WHERE player_id = {id}) 
                                               WHERE tg_id = {tg_id};
    
                                               DELETE FROM players_user
                                               WHERE user_id = (SELECT user_id FROM users WHERE tg_id = {tg_id} 
                                                   AND player_id = {id} AND position = '{category}'
                                                   ''')
                        return 1
                    else:
                        return 2


            #Если такого игрока нет
            else:
                #Покупка
                if Q:
                    bay_card = await conn.fetchrow('''
                                                        SELECT EXISTS (
                                                            SELECT 1
                                                            FROM users
                                                            JOIN players ON (users.balance > players.pur_price)
                                                            WHERE users.tg_id = $1
                                                            AND players.player_id = $2
                                                        )
                                                    ''', tg_id, id)

                    if bay_card[0]:
                        await conn.fetchrow(f'''UPDATE users 
                                                SET balance = balance - (SELECT pur_price 
                                                                            FROM players 
                                                                            WHERE player_id = {id}) 
                                                WHERE tg_id = {tg_id};
                                            ''')
                        await conn.execute(f'''INSERT INTO players_user(user_id, player_id, position) 
                                                                    VALUES (
                                                                        (SELECT user_id FROM users WHERE tg_id = $1),
                                                                        $2,
                                                                        $3
                                                                    )''',
                                           tg_id, id, category)
                        return 1
                    else:
                        return 2
                else:
                    return 0







    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
        if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')