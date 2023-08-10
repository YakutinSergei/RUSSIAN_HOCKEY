from datetime import datetime
import asyncpg

from environs import Env

env = Env()
env.read_env()


async def db_connect():
    try:
        conn = await asyncpg.connect(user=env('user'),  password=env('password'), database=env('db_name'), host=env('host'))

        await conn.execute('''CREATE TABLE IF NOT EXISTS users(id BIGSERIAL NOT NULL PRIMARY KEY,
                                                            tg_id BIGSERIAL,
                                                            user_name VARCHAR(50),
                                                            attempts INTEGER DEFAULT '1',
                                                            admin BOOLEAN DEFAULT 'false',
                                                            points INTEGER DEFAULT '0',
                                                            balance INTEGER DEFAULT '0');''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS team(id BIGSERIAL NOT NULL PRIMARY KEY,
                                                                tg_id BIGSERIAL,
                                                               name VARCHAR(50) DEFAULT 'None',
                                                               goalkeeper INTEGER,
                                                               forward_1 INTEGER,
                                                               forward_2 INTEGER,
                                                               forward_3 INTEGER,
                                                               defender_1 INTEGER,
                                                               defender_2 INTEGER,
                                                               ready BOOLEAN DEFAULT 'True',
                                                               game_date TIMESTAMP DEFAULT 'now()',
                                                               count INTEGER DEFAULT '0',
                                                               pucks_scored INTEGER DEFAULT '0',
                                                               missed_pucks INTEGER DEFAULT '0',
                                                               points INTEGER DEFAULT '0');''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS players(id BIGSERIAL NOT NULL PRIMARY KEY,
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

        await conn.execute('''CREATE TABLE IF NOT EXISTS goalkeepers(id BIGSERIAL NOT NULL PRIMARY KEY,
                                                                        img VARCHAR(100),
                                                                        name VARCHAR(50),
                                                                        reliability REAL,
                                                                        endurance INTEGER,
                                                                        defense INTEGER,
                                                                        pur_price INTEGER,
                                                                        sal_price INTEGER,
                                                                        start_player BOOLEAN DEFAULT 'false');''')

        await conn.execute('''CREATE TABLE IF NOT EXISTS players_user(id BIGSERIAL NOT NULL PRIMARY KEY,
                                                                            id_user INTEGER,
                                                                            id_players INTEGER,
                                                                            position VARCHAR(50));''')

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