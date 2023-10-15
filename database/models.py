from datetime import datetime
import asyncpg

from environs import Env

env = Env()
env.read_env()


async def db_connect():
    try:
        conn = await asyncpg.connect(user=env('user'),  password=env('password'), database=env('db_name'), host=env('host'))

        await conn.execute('''CREATE TABLE IF NOT EXISTS users(user_id SERIAL NOT NULL PRIMARY KEY, 
                                                            tg_id BIGSERIAL,
                                                            user_name VARCHAR(50),
                                                            attempts INTEGER DEFAULT '1',
                                                            admin BOOLEAN DEFAULT 'false',
                                                            points INTEGER DEFAULT '0',
                                                            balance INTEGER DEFAULT '0')''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS goalkeepers(goalkeeper_id SERIAL NOT NULL PRIMARY KEY,
                                                                                img VARCHAR(100),
                                                                                name VARCHAR(50),
                                                                                reliability REAL,
                                                                                endurance INTEGER,
                                                                                defense INTEGER,
                                                                                pur_price INTEGER,
                                                                                sal_price INTEGER,
                                                                                start_player BOOLEAN DEFAULT 'false');''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS players(player_id SERIAL NOT NULL PRIMARY KEY,
                                                                                img VARCHAR(100),
                                                                                name VARCHAR(50),
                                                                                position VARCHAR(50),
                                                                                attack INTEGER,
                                                                                endurance INTEGER,
                                                                                power INTEGER,
                                                                                defense INTEGER,
                                                                                pur_price INTEGER,
                                                                                sal_price INTEGER,
                                                                                start_player BOOLEAN DEFAULT 'false');''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS team(id SERIAL NOT NULL PRIMARY KEY,
                                                                user_id INTEGER REFERENCES users(user_id),
                                                               name VARCHAR(50) DEFAULT 'None',
                                                               goalkeeper_id INTEGER REFERENCES goalkeepers(goalkeeper_id) NOT NULL,
                                                               forward_1 INTEGER REFERENCES players(player_id) NOT NULL,
                                                               forward_2 INTEGER REFERENCES players(player_id) NOT NULL,
                                                               forward_3 INTEGER REFERENCES players(player_id) NOT NULL,
                                                               defender_1 INTEGER REFERENCES players(player_id) NOT NULL,
                                                               defender_2 INTEGER REFERENCES players(player_id) NOT NULL,
                                                               ready BOOLEAN DEFAULT 'True',
                                                               game_date TIMESTAMP DEFAULT 'now()',
                                                               count INTEGER DEFAULT '0',
                                                               pucks_scored INTEGER DEFAULT '0',
                                                               missed_pucks INTEGER DEFAULT '0',
                                                               points INTEGER DEFAULT '0');''')





        await conn.execute('''CREATE TABLE IF NOT EXISTS players_user(id SERIAL NOT NULL PRIMARY KEY,
                                                                            user_id INTEGER,
                                                                            player_id INTEGER,
                                                                            position VARCHAR(50));''')

        #Таблица ставок
        #num_outcomes - число исходов
        #start_data - Начало матча
        #outcomes - результат
        #team_1 team_2 - команды
        await conn.execute('''CREATE TABLE IF NOT EXISTS bets(bets_id BIGSERIAL NOT NULL PRIMARY KEY,
                                                                num_outcomes INTEGER,
                                                                start_data TIMESTAMP,
                                                                outcomes INTEGER DEFAULT '0',
                                                                team_1 VARCHAR(50),
                                                                team_2 VARCHAR(50));''')

        #Таблица со ставками игроков
        # bets_id - номер ставки
        # user_id - ссылка кто поставил
        # outcomes - На какой результат поставил
        await conn.execute('''CREATE TABLE IF NOT EXISTS bets_players(id SERIAL NOT NULL PRIMARY KEY,
                                                                            bets_id INTEGER REFERENCES bets(bets_id),
                                                                            user_id INTEGER REFERENCES users(user_id),
                                                                            outcomes VARCHAR(50));''')


        '''позиция 
        скорость
        мастерство катания
        мастерство завершения
        решительность
        коммуникабельность'''



    except Exception as _ex:
        print('[INFO] Error ', _ex)

    finally:
          if conn:
            await conn.close()
            print('[INFO] PostgresSQL closed')