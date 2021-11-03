import psycopg2
from psycopg2.extras import RealDictCursor


class PgStore:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def init_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            print("Database connection was successful")
            cursor = conn.cursor()
            return {"cursor": cursor, "conn": conn}
        except Exception as error:
            print(f"Connecting to database failed: {error}")
            raise error
