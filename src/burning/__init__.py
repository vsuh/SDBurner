"""
import sqlite3 as sqlite

conn = sqlite.connect('companies_db.sqlite')

with conn:
    conn.row_factory = sqlite.Row
    curs = conn.cursor()
    curs.execute("SELECT * FROM companies_table")
    rows = curs.fetchall()
    for row in rows:
        print(f"{row['companyid']}, {row['name']}, {row['address']}.")
"""

import os
from pathlib import Path
import logging 
import sqlite3
from shutil import copy
class BurnCD:
    """
    Заполнение коллекции треками
    """
    def __init__(self, db, cdpath, cdsize, force, log) -> None:
        self.db = db
        self.cdpath = cdpath
        self.cdsize = cdsize
        self.force = force
        self.log = log
        self.conn = None
        self.create_collection()

    def create_collection(self) -> None:
        """
        Получает из БД случайный список еще не прослушанных (или давно прослушанных)
        композиций и копирует эти файлы в каталог коллекции
        """
        self.conn_db()
        with self.conn:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            coll = cursor.execute("""
                    SELECT * FROM mp3files
                    ORDER BY used, hash
                """)
            rows = coll.fetchall()
            path_to_collection = []
            total_size = 0
            self.log.info(f'Формируется коллекция "{self.cdpath}"')
            for row in rows:
                total_size = total_size + row['size']
                if total_size>self.cdsize:
                    break
                path_to_collection.append(row['fpath'])
                self.log.debug(f'Файл {self.file_name(row["fpath"])} размером {row["size"]}b. добавлен в коллекцию. Всего {self.humanize(total_size)}')
                # print(f'Файл {self.file_name(row["fpath"])} размером {row["size"]}b. добавлен в коллекцию. Всего {self.humanize(total_size)} сравниваем с {self.humanize(self.cdsize)}')
            
            self.log.info(f'В список для коллекции {self.cdpath} помещено {len(rows)} файлов')    
            # self.conn.close()
            
        if self.force:
            self.log.debug(f'Из-за флага force нужно очистить Каталог коллекции "{Path(self.cdpath).absolute()}"')
            SDpath = Path(self.cdpath)
            if SDpath.exists() and SDpath.is_dir() and self.force:
                for sd in SDpath.rglob('*'):
                    sd.unlink()
                SDpath.rmdir()
                self.log.debug(f'Каталог коллекции {self.cdpath} очищен')
            try:
                SDpath.mkdir()
            except FileExistsError:
                print(f'Каталог {SDpath} существует')
                return
            # TODO: Изменять в записи по файлу поле 'used' на сегодняшнюю дату    
            for mm in path_to_collection:
                Pmm = Path(mm)
                copy(mm, Path.joinpath(SDpath, Pmm.name))
                self.log.debug(f'Файл {self.file_name(mm)} размером {self.humanize(Pmm.stat().st_size)} скопирован в каталог {self.cdpath}')
                self.update_used_field(mm)
            
    def conn_db(self):
        "Соединение с БД"
        if self.conn is None:
            self.conn = sqlite3.connect(self.db)
    
    def update_used_field(self, mm) -> None:
        self.conn_db()
        today_str = dt.now().strftime('%Y-%m-%d')
        with self.conn:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute('UPDATE mp3files SET used = ? WHERE fpath = ?' ,(today_str, mm))
            self.log.debug(f'Обновлена информация о дате использования файла {self.file_name(mm)}')
    
    def humanize(self, cifer) -> str:
        """
        Преобразует число в байтах к человекочитаемому виду 

        Args:
            cifer (_type_): число байтов

        Returns:
            str: преобразованное значение в Mb, Kb, Gb и т.д.
        """
        if    cifer > 2**50:
            return f'{round(cifer / 2**50, 2)} Pb'
        elif  cifer > 2**40:
            return f'{round(cifer / 2**40, 2)} Tb'
        elif  cifer > 2**30:
            return f'{round(cifer / 2**30, 2)} Gb'
        elif  cifer > 2**20:
            return f'{round(cifer / 2**20, 2)} Mb'
        elif  cifer > 2**10:
             return f'{round(cifer / 2**10 ,2)} Kb'
        else:
            return f'{cifer} b'
        
    def file_name(self, fn:str) -> str:
        return Path(fn).name
