import os
import sqlite3

# Timezone formats:
#   24 -> Standard Military time format
#   12 -> 12h format with pm am etc
#   1  -> ISO-8601 format1

class database:
    def __init__(self, path_to_db_file: str):
        self.path = path_to_db_file
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.create_table()

    def create_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS timezones (
            user_id INTEGER PRIMARY KEY,
            timezone text NOT NULL,
            timeformat_config INTEGER
        );"""
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
        finally:
            conn.close()
            
    def check_user_exists(self, user_id: int) -> bool:
        query = "SELECT user_id FROM timezones WHERE user_id = ?"
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                return cursor.fetchone() is not None        
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
            return False
        finally:
            conn.close()

    def write_timezone(self, user: int, zone: str):
        print(f'Writing TIMEZONE: {user} -> {zone}')
        
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()

                # override existing user data
                if self.check_user_exists(user):
                    print(f'OVERRIDING data of \"{user}\" in the database')
                    sql = "UPDATE timezones SET timezone = ? WHERE user_id = ?"
                    cursor.execute(sql, (zone, user))
                else:
                    print(f'NEW database entry of {user}')
                    sql = "INSERT INTO timezones(user_id, timezone) VALUES(?, ?)"
                    cursor.execute(sql, (user, zone))

                conn.commit()
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
        finally:
            conn.close()

    def write_timeformat_config(self, user: int, timeformat: int):
        print(f'Writing TIMEFORMAT_CONFIG: {user} -> {timeformat}')

        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()

                # override existing user data
                if self.check_user_exists(user):
                    print(f'OVERRIDING data of \"{user}\" in the database')
                    sql = "UPDATE timezones SET timeformat_config = ? WHERE user_id = ?"
                    cursor.execute(sql, (timeformat, user))
                else:
                    print(f'NEW database entry of {user}')
                    sql = "INSERT INTO timezones(user_id, timeformat_config) VALUES(?, ?)"
                    cursor.execute(sql, (user, timeformat))

                conn.commit()
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
        finally:
            conn.close()

    def get_timezone(self, user: int) -> str | None:
        query = "SELECT timezone FROM timezones WHERE user_id = ?"
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user,))
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                return None
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
        finally:
            conn.close()

    def get_timeformat_config(self, user: int) -> int | 24:
        query = "SELECT timeformat_config FROM timezones WHERE user_id = ?"
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user,))
                result = cursor.fetchone()

                if result:
                    return result[0]
                return 24
        except sqlite3.OperationalError as e:
            print("failed to open database: ", e)
        finally:
            conn.close()


    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
