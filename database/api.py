import mysql.connector

from datetime import datetime
from pathlib import Path

_USER = "root"
_PASSWORD = "pwd123"
_DATABASE = "user_statistics"
_HOST = "127.0.0.1"
_PORT = 3306


_connection = mysql.connector.connect(
    user=_USER, password=_PASSWORD, database=_DATABASE, host=_HOST, port=_PORT
)


def create_database(db_name: str) -> None:
    with _connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(db_name))
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS song_played(
                    _id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    author VARCHAR(255),
                    album VARCHAR(255),
                    title VARCHAR(255),
                    date DATETIME
                );
            """
        )
        _connection.commit()


def add_table_from_csv(csv_path: Path, sep: str = ","):
    username = csv_path.stem
    with open(csv_path, "rt") as csv_file:
        with _connection.cursor() as cursor:
            for line in csv_file:
                author, _, title, date = line.split(sep)

                formated_date = datetime.strptime(date.strip(), '%d %b %Y %H:%M').strftime(
                    '%Y-%m-%d %H:%M:%S'
                )

                query = """
                        INSERT INTO song_played(username, author, title, date)
                        VALUES ("{username}", "{author}", "{title}", "{date}");
                    """.format(
                        username=username,
                        author=author,
                        title=title,
                        date=formated_date
                    )

                cursor.execute(query)

            _connection.commit()
