import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Union, Tuple


class SQLite(object):
    __slots__ = (
        '_db',
        '_cursor',
        '_db_file',
    )

    def __init__(self,
                 db_name: str = 'HTMLInfo',
                 db_dir: Optional[Union[str, Path]] = None,
                 ) -> None:
        if db_dir is None or db_dir == '':
            raise ValueError('db_dir must be provided')
        else:
            data_base_dir = db_dir if isinstance(db_dir, Path) else Path(db_dir)
            if not data_base_dir.exists():
                data_base_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )
            self._db_file = data_base_dir.joinpath(
                db_name,
            ).with_suffix('.db')
            self._db = sqlite3.connect(self._db_file)
            self._cursor = self._db.cursor()

    @staticmethod
    def get_key(url: str) -> Optional[str]:
        try:
            key = hashlib.sha256(url.encode('utf-8')).hexdigest()
            return key
        except TypeError as e:
            print('Error: %s (In the get_key function)' % e)
            return None

    def create_table(self, table_name: str = 'HTMLInfo') -> None:
        try:
            create_table_sql = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        HASH_URL  TEXT NOT NULL,
                        HTML_FILE TEXT NOT NULL,
                        TIMESTAMP TEXT NOT NULL);
                    '''
            self._cursor.execute(
                create_table_sql,
            )
        except sqlite3.OperationalError as e:
            print('Error: %s (In the create_table function)' % e)
            return None
        return None

    def insert(self,
               url: str,
               html_path: str,
               timestamp: Union[str, int, float],
               table_name: str = 'HTMLInfo',
               ) -> None:
        try:
            self._cursor.execute(
                f"INSERT INTO {table_name}(HASH_URL, HTML_FILE, TIMESTAMP) VALUES(?, ?, ?);",
                (
                    self.get_key(url=url),
                    html_path,
                    timestamp)
            )
            self._db.commit()
        except sqlite3.OperationalError as e:
            print('Error: %s (In the insert function)' % e)
            return None
        return None

    def delete(self,
               url: str,
               table_name: str = 'HTMLInfo',
               ) -> None:
        try:
            self._cursor.execute(
                f"DELETE FROM {table_name} WHERE HASH_URL=?;",
                (self.get_key(url=url),)
            )
            self._db.commit()
        except sqlite3.OperationalError as e:
            print('Error: %s (In the delete function)' % e)
            return None
        return None

    def query(self,
              url: str,
              table_name: str = 'HTMLInfo',
              ) -> Optional[Tuple[str, str]]:
        key = ''
        if url:
            key = self.get_key(url)
        else:
            raise ValueError('url must be provided')
        self._cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,)
        )
        exists = self._cursor.fetchone() is not None
        if exists is False:
            raise ValueError('table does not exist')
        else:
            try:
                self._cursor.execute(
                    "SELECT HTML_FILE, TIMESTAMP FROM HTMLInfo WHERE HASH_URL=?;",
                    (key,),
                )
                return self._cursor.fetchone()
            except sqlite3.OperationalError as e:
                print('Error: %s (In the query function)' % e)
                return None

    def update(self,
               url: str,
               html_path: str,
               timestamp: Union[str, float, int],
               table_name: str = 'HTMLInfo',
               ) -> None:
        try:
            self._cursor.execute(
                f"UPDATE {table_name} SET HTML_FILE=?, TIMESTAMP=? WHERE HASH_URL=?;",
                (
                    html_path,
                    timestamp if isinstance(timestamp, str) else str(timestamp),
                    self.get_key(url))
            )
            self._db.commit()
        except sqlite3.OperationalError as e:
            print('Error: %s (In the update function)' % e)
            return None
        return None

    def close(self) -> None:
        try:
            self._cursor.close()
            self._db.close()
        except sqlite3.OperationalError as e:
            print('Error: %s (In the close function)' % e)
        return None

    def __enter__(self) -> 'SQLite':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

__all__ = [
    'SQLite',
]
