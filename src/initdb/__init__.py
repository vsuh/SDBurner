import os
import sys
import sqlite3
from pathlib import Path
import hashlib
import logging
from datetime import datetime as dt

class InitDB:

    def __init__(self, mp3path: Path, db: str, force: bool, log) -> None:
        self.mp3path = mp3path
        self.db = db
        self.force = force
        self.log = log
        self.cursor = None
        self.conn = None
        self.create_db()

    def conn_db(self):
        self.conn = sqlite3.connect(self.db)
        with self.conn:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS mp3files')
            self.conn.commit()
            self.log.info(f"создаю БД '{self.db}'")
            cursor.execute('''
            CREATE TABLE mp3files (
                id INTEGER PRIMARY KEY,
                fpath TEXT NOT NULL,
                hash TEXT NOT NULL,
                used DATETIME DEFAULT '2033-12-12',
                size INTEGER
            );''')
            
            self.conn.commit()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_used ON mp3files (used)')
            self.conn.commit()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON mp3files (hash)')
            self.conn.commit()
         
    def get_file_hash(self, file:str) -> str:
        BUF_SIZE = 65536
        md5 = hashlib.md5()
        # with open(file, 'rb') as f:
        #     while True:
        #         data = f.read(BUF_SIZE)
        #         if not data:
        #             break
        #         md5.update(data)
        md5.update(str(file).encode())
        return md5.hexdigest()

    def add_file_record(self, file: Path):
        with self.conn:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()    
            sql = f'INSERT INTO mp3files (fpath, hash, size) VALUES ( "{file.absolute()._str}", "{self.get_file_hash(file)}",  "{file.stat().st_size}")'
            # print(sql)
            cursor.execute(sql)
            self.conn.commit()
            
    def create_db(self) -> None:
        
        self.conn_db()
        if not self.mp3path.exists():
            raise FileNotFoundError("mp3 каталог не найден")
        filelist = self.mp3path.rglob('*')
        r=0
        with self.conn:
            for f in filelist:
                if f.is_dir():
                    continue
                self.add_file_record(f)
                self.log.debug(f'добавлен файл {self.file_name(f)} в БД')
                r=r+1
            # self.conn.close()
        self.log.info(f'{r} записей добавлено в БД')
    
    def file_name(self, fn:str) -> str:
        return Path(fn).name
