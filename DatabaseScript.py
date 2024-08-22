import asyncpg
import configs

class Database:

    def __init__(self, dbs=configs.dbs_name, user=configs.user_name, host=configs.host, password=configs.password, port=configs.port):
        self.dbs = dbs
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.pool = None

    async def connect(self):
        # Tworzenie puli połączeń
        self.pool = await asyncpg.create_pool(
            database=self.dbs,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    async def insert_new_user(self, id="", queue=[], playlist="https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"):
        query = "INSERT INTO users (guildID, queue, playlist, currentsong, repeat) VALUES ($1, $2, $3,$4,$5);"
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id), queue, playlist, '', 'false')

    async def add_to_queue(self, id, song):
        query = """
            UPDATE users
            SET queue = queue || $1
            WHERE guildID = $2;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, [song], str(id))

    async def change_current_song(self, id, song):
        query = """
            UPDATE users
            SET currentSong = $1
            WHERE guildID = $2;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, song, str(id))

    async def get_current_song(self, id):
        query = """
            SELECT currentSong FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            return response['currentsong']

    async def reset_current_song(self, id):
        query = """
            UPDATE users
            SET currentSong = ''
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

    async def pop_top_queue(self, id):
        select_query = """
            SELECT queue FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(select_query, str(id))
            if response and response['queue']:
                queue = response['queue']
                name = queue.pop(0)
                update_query = """
                    UPDATE users
                    SET queue = $1 
                    WHERE guildID = $2;
                """
                await connection.execute(update_query, queue, str(id))
                return name
            return None

    async def queue_length(self, id):
        query = """
            SELECT queue FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            if response and response['queue']:
                return len(response['queue'])
            return 0

    async def change_playlist(self, id, playlist):
        query = """
            UPDATE users
            SET playlist = $1
            WHERE guildID = $2;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, playlist, str(id))

    async def remove_user(self, id):
        query = """
            DELETE FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

    async def restart_queue(self, id):
        query = """
            UPDATE users
            SET queue = '{}'
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

    async def loop_song(self, id):
        query = """
            UPDATE users 
            SET repeat = 'true'
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

        '''query = """
            SELECT currentSong FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
        query = """
            INSERT INTO loops (guildID, songName) values ($1, $2);
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id), response['currentsong'])'''


    async def unloop_song(self, id):
        query = """
            UPDATE users
            SET repeat = 'false'
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

    async def check_loop(self, arg):
        if type(arg) == int :
            query = """
                SELECT repeat FROM users
                WHERE guildID = $1;
            """
            async with self.pool.acquire() as connection:
                response = await connection.fetchrow(query, str(arg))
                status = response['repeat']
                if status == 'true':
                    return True
                return False
        else :
            query = """
                         SELECT repeat FROM users
                         WHERE currentSong = $1;
                     """
            async with self.pool.acquire() as connection:
                response = await connection.fetchrow(query, str(arg))
                if response == None:
                    return False
                if response['repeat'] == 'true':
                    return True
                return False


    async def get_playlist(self, id):
        query = """
            SELECT playlist FROM users
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            if response:
                return response['playlist']
            return None

    async def save_game_info(self, id, songs, players, channelID ):
        if songs == [] or players == [] :
            return False
        query = """
            INSERT INTO games (guildID, players, songs, currentSong, channelID) values ($1, $2, $3, $4, $5);
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id), players, songs, '', str(channelID))

    async def next_game_round(self, id):
        query = """
            SELECT songs FROM games
            WHERE guildID = $1;
        """
        with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            songs = response['songs']
            if songs == []:
                return False
            song = songs.pop(0)
            query = """
                UPDATE games
                SET songs = $1
                WHERE guildID = $2;
            """
            await connection.execute(query, songs, str(id))
            query = """
                UPDATE games
                SET currentSong = $1
                WHERE guildID = $2;
            """
            await connection.execute(query, song, str(id))
            return True

    async def get_players(self, id):
        query = """
            SELECT players FROM games
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            return response['players']

    async def get_game_song(self, id):
        query = """
            SELECT currentSong FROM games
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            return response['currentsong']

    async def end_game(self, id):
        query = """
            DELETE FROM games
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(query, str(id))

    async def get_game_channel(self, id):
        query = """
            SELECT channelID FROM games
            WHERE guildID = $1;
        """
        async with self.pool.acquire() as connection:
            response = await connection.fetchrow(query, str(id))
            return response['channelID']








'''import psycopg2
import configs

class database:

    def __init__(self, dbs = configs.dbs_name, user = configs.user_name, host = configs.host, password = configs.password, port = configs.port):
        self.dbs = dbs
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.connection = psycopg2.connect(database = self.dbs,
                                          user = self.user,
                                          host = self.host,
                                          password = self.password,
                                          port = self.port)
        self.cursor = self.connection.cursor()

    def insert_new_user(self, id = "", queue = "{}" , playlist = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"):
        query = "INSERT INTO users (guildID, queue, playlist) VALUES (%s, %s, %s);"
        self.cursor.execute(query,(str(id),queue,playlist))
        self.connection.commit()

    def add_to_queue(self, id, song):
        query = ("""
            UPDATE users
            SET queue = queue || %s
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,('{' + song + '}',str(id)))
        self.connection.commit()

    def pop_top_queue(self, id):
        query = ("""
            SELECT queue FROM users
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(str(id),))
        response = self.cursor.fetchall()

        name = response[0][0][0]
        print(name)
        response[0][0].pop(0)
        print(response)
        response = ", ".join(response[0][0])
        response = "{" + response + "}"
        query = ("""
            UPDATE users
            SET queue = %s 
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(response,str(id)))
        self.connection.commit()
        return name

    def queue_length(self,id):
        query = ("""
            SELECT queue FROM users
             WHERE guildID = %s;
        """)
        self.cursor.execute(query,(str(id),))
        response = self.cursor.fetchall()
        response = response[0][0]
        return len(response)

    def change_playlist(self,id,playlist):
        query = ("""
            UPDATE users
            SET playlist = %s
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(playlist,str(id)))
        self.connection.commit()

    def remove_user(self,id):
        query = ("""
            DELETE FROM users
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(str(id),))
        self.connection.commit()

    def restart_queue(self,id):
        query = ("""
            UPDATE users
            SET queue = "{}"
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(str(id),))
        self.connection.commit()

    def get_playlist(self,id):
        query = ("""
            SELECT playlist FROM users
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(str(id),))
        response = self.cursor.fetchall()
        return response[0][0]'''