import psyorg2
import configs

class database:

    def __init__(self, dbs = configs.dbs_name, user = configs.user_name, host = configs.host, password = configs.password, port = configs.port):
        self.dbs = dbs
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.connection = psyorg2.connect(database = self.dbs,
                                          user = self.user,
                                          host = self.host,
                                          password = self.password,
                                          port = self.port)
        self.cursor = self.connection.cursor()

    def insert_new_user(self, id = "", queue = "{}" , playlist = ""):
        query = "INSERT INTO users (guildID, queue, playlist) VALUES (%s, %s, %s);"
        self.cursor.execute(query,(id,queue,playlist))
        self.connection.commit()

    def add_to_queue(self, id, song):
        query = ("""
            UPDATE users
            SET queue = queue || %s
            WHERE guildID = %s;
        """)
        self.cursor.excetute(query,(song,id))
        self.connection.commit()

    def pop_top_queue(self, id):
        query = ("""
            SELECT queue FROM users
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(id,))
        response = cursor.fetchall()
        name = response[0][0][0]
        response = response[0][0].pop(0)
        response = ", ".join(response[0][0])
        response = "{" + response + "}"
        query = ("""
            UPDATE users
            SET queue = %s 
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(response,id))
        self.connection.commit()
        return name

    def queue_length(self,id):
        query = ("""
            SELECT queue FROM users
             WHERE guildID = %s;
        """)
        self.cursor.execute(query,(id,))
        response = cursor.fetchall()
        response = response[0][0]
        return len(response)

    def change_playlist(self,id,playlist):
        query = ("""
            UPDATE users
            SET playlist = %s
            WHERE guildID = %s;
        """)
        self.cursor.execute(query,(playlist,id))
        self.connection.commit()
