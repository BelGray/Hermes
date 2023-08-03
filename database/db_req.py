from database.sql_config import bot_db, cursor
from tools.logger import Log
from tools.tool import *

class DBRequests:

    @staticmethod
    async def init_database():
        Log.i("init_database", "Init process started")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id VARCHAR,
            winner_count INTEGER
            );
        """)
        bot_db.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_draws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_channel_id VARCHAR,
        messages_count INTEGER,
        time VARCHAR,
        completed INTEGER
        );
        """)
        bot_db.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_draws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_channel_id VARCHAR,
        user_in_channel_time VARCHAR,
        time VARCHAR,
        completed INTEGER
        );
        """)
        bot_db.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_draws_members (
        draw_id INTEGER,
        user_id INTEGER,
        messages_in_channel INTEGER
        );
        """)
        bot_db.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_draws_members (
        draw_id INTEGER,
        user_id INTEGER,
        time_in_channel INTEGER
        );
        """)
        bot_db.commit()

        Log.i("init_database", "Init process finished")

    @staticmethod
    async def insert_user(discord_id: str, winner_count: int):
        """table_name: users"""
        TAG = "insert_user"
        TABLE_NAME = "users"
        cursor.execute(f"SELECT * FROM users WHERE discord_id = ?", [discord_id])
        result = cursor.fetchone()
        if not result:
            try:
                cursor.execute(f"""
                    INSERT INTO users VALUES(
                    NULL,
                    ?,
                    ?
                    )
                    """, [discord_id, winner_count])
                bot_db.commit()
                Log.sql(TAG, f"Inserted new user with discord_id {discord_id}", TABLE_NAME)
                return True, cursor.lastrowid
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
                return False, None
        else:
            Log.sql(TAG, f"User with discord_id {discord_id} already exists in database", TABLE_NAME)
            return False, None

    @staticmethod
    async def update_user_by_id(id: int, winner_count: int):
        """table name: users"""
        TAG = "update_user_by_id"
        TABLE_NAME = "users"
        cursor.execute(f"SELECT * FROM users WHERE id = ?", (id,))
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE users SET winner_count = ? WHERE id LIKE ?", [winner_count, id])
                bot_db.commit()
                Log.sql(TAG, f"Updated user with id: {id}", TABLE_NAME)
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
        else:
            Log.sql(TAG, f"User with id {id} is not found", TABLE_NAME)

    @staticmethod
    async def get_user_by_id(id: int):
        """table name: users"""
        TAG = "get_user_by_id"
        TABLE_NAME = "users"
        cursor.execute(f"SELECT * FROM users WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        Log.sql(TAG, f"User with id {id} is not found", TABLE_NAME)
        return False, None

    @staticmethod
    async def insert_text_draw(discord_channel_id: str, messages_count: int, time: str, completed: bool):
            """table_name: text_draws"""
            TAG = "insert_text_draw"
            TABLE_NAME = "text_draws"
            try:
                cursor.execute(f"""
                        INSERT INTO text_draws VALUES(
                        NULL,
                        ?,
                        ?,
                        ?,
                        ?
                        )
                        """, [discord_channel_id, messages_count, time, convert_boolean(completed)])
                bot_db.commit()
                Log.sql(TAG, f"Inserted new text draw", TABLE_NAME)
                return True, cursor.lastrowid
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
                return False, None

    @staticmethod
    async def update_text_draw_by_id(id: int, completed: bool):
        """table_name: text_draws"""
        TAG = "update_text_draw_by_id"
        TABLE_NAME = "text_draws"
        cursor.execute(f"SELECT * FROM text_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE text_draws SET completed = ? WHERE id LIKE ?", [convert_boolean(completed), id])
                bot_db.commit()
                Log.sql(TAG, f"Updated draw with id: {id}", TABLE_NAME)
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
        else:
            Log.sql(TAG, f"Text draw with id {id} is not found", TABLE_NAME)

    @staticmethod
    async def get_text_draw_by_id(id: int):
        """table name: text_draws"""
        TAG = "get_text_draw_by_id"
        TABLE_NAME = "text_draws"
        cursor.execute(f"SELECT * FROM text_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        Log.sql(TAG, f"Text draw with id {id} is not found", TABLE_NAME)
        return False, None

    @staticmethod
    async def insert_voice_draw(discord_channel_id: str, user_in_channel_time: int, time: str, completed: bool):
        """table_name: voice_draws"""
        TAG = "insert_voice_draw"
        TABLE_NAME = "voice_draws"
        try:
            cursor.execute(f"""
                            INSERT INTO voice_draws VALUES(
                            NULL,
                            ?,
                            ?,
                            ?,
                            ?
                            )
                            """, [discord_channel_id, user_in_channel_time, time, convert_boolean(completed)])
            bot_db.commit()
            Log.sql(TAG, f"Inserted new voice draw", TABLE_NAME)
            return True, cursor.lastrowid
        except Exception as e:
            Log.e(TAG, f"EXCEPTION: {e}")
            return False, None

    @staticmethod
    async def update_voice_draw_by_id(id: int, completed: bool):
        """table_name: voice_draws"""
        TAG = "update_voice_draw_by_id"
        TABLE_NAME = "voice_draws"
        cursor.execute(f"SELECT * FROM voice_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE voice_draws SET completed = ? WHERE id LIKE ?", [convert_boolean(completed), id])
                bot_db.commit()
                Log.sql(TAG, f"Updated draw with id: {id}", TABLE_NAME)
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
        else:
            Log.sql(TAG, f"Voice draw with id {id} is not found", TABLE_NAME)

    @staticmethod
    async def get_voice_draw_by_id(id: int):
        """table name: voice_draws"""
        TAG = "get_voice_draw_by_id"
        TABLE_NAME = "voice_draws"
        cursor.execute(f"SELECT * FROM voice_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        Log.sql(TAG, f"Voice draw with id {id} is not found", TABLE_NAME)
        return False, None

    @staticmethod
    async def insert_voice_draw_member(draw_id: int, user_id: int, time_in_channel: int):
        """table_name: voice_draws_members"""
        TAG = "insert_voice_draw_member"
        TABLE_NAME = "voice_draws_members"
        try:
            cursor.execute(f"""
                                INSERT INTO voice_draws_members VALUES(
                                NULL,
                                ?,
                                ?,
                                ?
                                )
                                """, [draw_id, user_id, time_in_channel])
            bot_db.commit()
            Log.sql(TAG, f"Inserted new voice draw member with user_id: {user_id}", TABLE_NAME)
            return True, cursor.lastrowid
        except Exception as e:
            Log.e(TAG, f"EXCEPTION: {e}")
            return False, None

    @staticmethod
    async def update_voice_draw_member_by_id(user_id: int, draw_id: int, time_in_channel: int):
        """table_name: voice_draws_members"""
        TAG = "update_voice_draw_member_by_id"
        TABLE_NAME = "voice_draws_members"
        cursor.execute(f"SELECT * FROM voice_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE voice_draws_members SET time_in_channel = time_in_channel + ? WHERE user_id LIKE ? AND draw_id LIKE ?", [time_in_channel, user_id, draw_id])
                bot_db.commit()
                Log.sql(TAG, f"Updated draw member with user_id: {user_id}", TABLE_NAME)
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
        else:
            Log.sql(TAG, f"Voice draw member with user_id {user_id} is not found", TABLE_NAME)

    @staticmethod
    async def get_voice_draw_member_by_id(user_id: int, draw_id: int):
        """table name: voice_draws_members"""
        TAG = "get_voice_draw_member_by_id"
        TABLE_NAME = "voice_draws_members"
        cursor.execute(f"SELECT * FROM voice_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            return True, result
        Log.sql(TAG, f"Voice draw member with user_id {user_id} is not found", TABLE_NAME)
        return False, None


    @staticmethod
    async def insert_text_draw_member(draw_id: int, user_id: int, messages_in_channel: int):
        """table_name: text_draws_members"""
        TAG = "insert_text_draw_member"
        TABLE_NAME = "text_draws_members"
        try:
            cursor.execute(f"""
                                INSERT INTO text_draws_members VALUES(
                                NULL,
                                ?,
                                ?,
                                ?
                                )
                                """, [draw_id, user_id, messages_in_channel])
            bot_db.commit()
            Log.sql(TAG, f"Inserted new text draw member with user_id: {user_id}", TABLE_NAME)
            return True, cursor.lastrowid
        except Exception as e:
            Log.e(TAG, f"EXCEPTION: {e}")
            return False, None

    @staticmethod
    async def update_text_draw_member_by_id(user_id: int, draw_id: int, messages_in_channel: int):
        """table_name: text_draws_members"""
        TAG = "update_text_draw_member_by_id"
        TABLE_NAME = "text_draws_members"
        cursor.execute(f"SELECT * FROM text_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE text_draws_members SET messages_in_channel = messages_in_channel + ? WHERE user_id LIKE ? AND draw_id LIKE ?", [messages_in_channel, user_id, draw_id])
                bot_db.commit()
                Log.sql(TAG, f"Updated draw member with user_id: {user_id}", TABLE_NAME)
            except Exception as e:
                Log.e(TAG, f"EXCEPTION: {e}")
        else:
            Log.sql(TAG, f"Text draw member with user_id {user_id} is not found", TABLE_NAME)

    @staticmethod
    async def get_text_draw_member_by_id(user_id: int, draw_id: int):
        """table name: text_draws_members"""
        TAG = "get_text_draw_member_by_id"
        TABLE_NAME = "text_draws_members"
        cursor.execute(f"SELECT * FROM text_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            return True, result
        Log.sql(TAG, f"Text draw member with user_id {user_id} is not found", TABLE_NAME)
        return False, None