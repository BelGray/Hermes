from database.sql_config import bot_db, cursor
from tools.tool import *

class DBRequests:

    @staticmethod
    async def init_database():
        print("[init_database | bot.db] Init process started")
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

        print("[init_database | bot.db] Init process finished")

    @staticmethod
    async def insert_user(discord_id: str, winner_count: int):
        """table_name: users"""
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
                print(f"[insert_user | users] Inserted user with discord_id: {discord_id}")
            except Exception as e:
                print(f"[insert_user | users] EXCEPTION: {e}")
        else:
            print(f"[insert_user | users] User with discord_id {discord_id} already exists in database")

    @staticmethod
    async def update_user_by_id(id: int, winner_count: int):
        """table name: users"""
        cursor.execute(f"SELECT * FROM users WHERE id = ?", (id,))
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE users SET winner_count = ? WHERE id LIKE ?", [winner_count, id])
                bot_db.commit()
                print(f"[update_user_by_id | users] Updated user with id: {id}")
            except Exception as e:
                print(f"[update_user_by_id | users] EXCEPTION: {e}")
        else:
            print(f"[update_user_by_id | users] User with id {id} is not found")

    @staticmethod
    async def get_user_by_id(id: int):
        """table name: users"""
        cursor.execute(f"SELECT * FROM users WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        print(f"[get_user_by_id | users] User with id {id} is not found")
        return False, None

    @staticmethod
    async def insert_text_draw(discord_channel_id: str, messages_count: int, time: str, completed: bool):
            """table_name: text_draws"""
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
                print(f"[insert_text_draw | text_draws] Inserted new text draw")
            except Exception as e:
                print(f"[insert_text_draw | text_draws] EXCEPTION: {e}")

    @staticmethod
    async def update_text_draw_by_id(id: int, completed: bool):
        """table_name: text_draws"""
        cursor.execute(f"SELECT * FROM text_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE text_draws SET completed = ? WHERE id LIKE ?", [convert_boolean(completed), id])
                bot_db.commit()
                print(f"[update_text_draw_by_id | text_draws] Updated draw with id: {id}")
            except Exception as e:
                print(f"[update_text_draw_by_id | text_draws] EXCEPTION: {e}")
        else:
            print(f"[update_text_draw_by_id | text_draws] Text draw with id {id} is not found")

    @staticmethod
    async def get_text_draw_by_id(id: int):
        """table name: text_draws"""
        cursor.execute(f"SELECT * FROM text_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        print(f"[get_text_draw_by_id | text_draws] Text draw with id {id} is not found")
        return False, None

    @staticmethod
    async def insert_voice_draw(discord_channel_id: str, user_in_channel_time: int, time: str, completed: bool):
        """table_name: voice_draws"""
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
            print(f"[insert_voice_draw | voice_draws] Inserted new voice draw")
        except Exception as e:
            print(f"[insert_voice_draw | voice_draws] EXCEPTION: {e}")

    @staticmethod
    async def update_voice_draw_by_id(id: int, completed: bool):
        """table_name: voice_draws"""
        cursor.execute(f"SELECT * FROM voice_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE voice_draws SET completed = ? WHERE id LIKE ?", [convert_boolean(completed), id])
                bot_db.commit()
                print(f"[update_voice_draw_by_id | voice_draws] Updated draw with id: {id}")
            except Exception as e:
                print(f"[update_voice_draw_by_id | voice_draws] EXCEPTION: {e}")
        else:
            print(f"[update_voice_draw_by_id | voice_draws] Voice draw with id {id} is not found")

    @staticmethod
    async def get_voice_draw_by_id(id: int):
        """table name: voice_draws"""
        cursor.execute(f"SELECT * FROM voice_draws WHERE id = ?", [id])
        result = cursor.fetchone()
        if result:
            return True, result
        print(f"[get_voice_draw_by_id | voice_draws] Voice draw with id {id} is not found")
        return False, None

    @staticmethod
    async def insert_voice_draw_member(draw_id: int, user_id: int, time_in_channel: int):
        """table_name: voice_draws_members"""
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
            print(f"[insert_voice_draw_member | voice_draws_members] Inserted new voice draw member with user_id: {user_id}")
        except Exception as e:
            print(f"[insert_voice_draw_member | voice_draws_members] EXCEPTION: {e}")

    @staticmethod
    async def update_voice_draw_member_by_id(user_id: int, draw_id: int, time_in_channel: int):
        """table_name: voice_draws_members"""
        cursor.execute(f"SELECT * FROM voice_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE voice_draws_members SET time_in_channel = ? WHERE user_id LIKE ? AND draw_id LIKE ?", [time_in_channel, user_id, draw_id])
                bot_db.commit()
                print(f"[update_voice_draw_member_by_id | voice_draws_members] Updated draw member with user_id: {user_id}")
            except Exception as e:
                print(f"[update_voice_draw_member_by_id | voice_draws_members] EXCEPTION: {e}")
        else:
            print(f"[update_voice_draw_member_by_id | voice_draws_members] Voice draw member with user_id {user_id} is not found")

    @staticmethod
    async def get_voice_draw_member_by_id(user_id: int, draw_id: int):
        """table name: voice_draws_members"""
        cursor.execute(f"SELECT * FROM voice_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            return True, result
        print(f"[get_voice_draw_member_by_id | voice_draws_members] Voice draw member with user_id {user_id} is not found")
        return False, None


    @staticmethod
    async def insert_text_draw_member(draw_id: int, user_id: int, messages_in_channel: int):
        """table_name: text_draws_members"""
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
            print(f"[insert_text_draw_member | text_draws_members] Inserted new text draw member with user_id: {user_id}")
        except Exception as e:
            print(f"[insert_text_draw_member | text_draws_members] EXCEPTION: {e}")

    @staticmethod
    async def update_text_draw_member_by_id(user_id: int, draw_id: int, messages_in_channel: int):
        """table_name: text_draws_members"""
        cursor.execute(f"SELECT * FROM text_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            try:
                cursor.execute("UPDATE text_draws_members SET messages_in_channel = ? WHERE user_id LIKE ? AND draw_id LIKE ?", [messages_in_channel, user_id, draw_id])
                bot_db.commit()
                print(f"[update_text_draw_member_by_id | text_draws_members] Updated draw member with user_id: {user_id}")
            except Exception as e:
                print(f"[update_text_draw_member_by_id | text_draws_members] EXCEPTION: {e}")
        else:
            print(f"[update_text_draw_member_by_id | text_draws_members] Text draw member with user_id {user_id} is not found")

    @staticmethod
    async def get_text_draw_member_by_id(user_id: int, draw_id: int):
        """table name: text_draws_members"""
        cursor.execute(f"SELECT * FROM text_draws_members WHERE user_id LIKE ? AND draw_id LIKE ?", [user_id, draw_id])
        result = cursor.fetchone()
        if result:
            return True, result
        print(f"[get_text_draw_member_by_id | text_draws_members] Text draw member with user_id {user_id} is not found")
        return False, None