import os
from pathlib import Path
import re
import random
import logging 
import sqlite3
from shutil import copy, rmtree
from datetime import datetime as dt

class BurnCD:
    """
    Заполнение каталога коллекции файлами музыкальных треков
    """
    REDICT = '0123456789ABCDEFGHIGKLMNOPQRSTUVWXYZ'     # charset for prefix word
    REPREFX = f'^\[[{REDICT}]+\]'                       # regex to match prefix in filename
    NUMRND = 6                                          # number of random chars in prefix

    def __init__(self, db:sqlite3, cdpath:Path, cdsize:int, randomize:bool, force:bool, log:logging) -> None:
        self.db = db
        self.cdpath = cdpath
        self.cdsize = cdsize
        self.force = force
        self.log = log
        self.randomize = randomize
        self.conn = None
        self.create_collection()

    def create_collection(self) -> None:
        """
        Получает из БД случайный список еще не прослушанных (или давно прослушанных)
        композиций и копирует эти файлы в каталог коллекции
        """
        self._clear_sd_if_needed()
        self.conn_db()
        with self.conn:
            path_to_collection = self._track_collection()

        SDpath = Path(self.cdpath)
        # if self.force:
        #     self.log.debug(f'Из-за флага force нужно очистить Каталог коллекции "{Path(self.cdpath).absolute()}"')
        #     if SDpath.is_dir():
        #         rmtree(SDpath)
        #         self.log.debug(f'Каталог коллекции "{self.cdpath}" очищен')

        # SDpath.mkdir(exist_ok=True)
        #✔ TODO: Изменять в записи по файлу поле 'used' на сегодняшнюю дату    
        for mm in path_to_collection:
            Pmm = Path(mm)
            nm = self.randname(Pmm.name) if self.randomize else Pmm.name    
            copy(mm, Path.joinpath(SDpath, nm))
            self.log.debug(f'Файл {self.file_name(mm)} размером {self.humanize(Pmm.stat().st_size)} скопирован в каталог {self.cdpath}')
            self.update_used_field(mm)

    # TODO Rename this here and in `create_collection`
    def _track_collection(self):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        coll = cursor.execute("""
                    SELECT * FROM mp3files
                    ORDER BY used, hash
                """)
        rows = coll.fetchall()
        result = []
        total_size = 0
        self.log.info(f'Формируется коллекция "{self.cdpath}"')
        for row in rows:
            total_size = total_size + row['size']
            if total_size>self.cdsize:
                break
            result.append(row['fpath'])
            self.log.debug(f'Файл {self.file_name(row["fpath"])} размером {row["size"]}b. добавлен в коллекцию. Всего {self.humanize(total_size)}')
                    # print(f'Файл {self.file_name(row["fpath"])} размером {row["size"]}b. добавлен в коллекцию. Всего {self.humanize(total_size)} сравниваем с {self.humanize(self.cdsize)}')

        self.log.info(f'В список для коллекции {self.cdpath} помещено {len(rows)} файлов')    

        return result
    
    def _clear_sd_if_needed(self):
        """
        очищает каталог коллекции, если передан флаг -f 
        """
        if cdpath_is_empty := Path(self.cdpath).stat().st_size == 0:
             return
         
        if self.force:
            self.log.info(f'Получен флаг  `force` - очищаем каталог {self.cdpath.absolute()}')
            rmtree(self.cdpath)
            self.cdpath.mkdir(exist_ok=True)
            self.log.info(f'Каталог {self.cdpath.absolute()} очищен')            
        else:
            self.log.warn(f"Каталог  {self.cdpath.absolute()} не пустой. Файлы будут дописаны")
            
    def randname(self, name:str) -> str:
        """
        добавляет (или изменяет) случайный префикс 
        к имени файла музыкального трека
        """
        if match:= re.search(self.REPREFX, name):
            return re.sub(self.REPREFX, self.rnd_word(), name)
        else:
            return self.rnd_word() + name

    def rnd_word(self)-> str:  
        """
        возвращает случайный префикс
        """
        ww = ''
        for l in random.sample(self.REDICT, self.NUMRND):
            ww = ww + l
        return  f'[{ww}]'

    def conn_db(self):
        "Соединение с БД"
        if self.conn is None:
            self.conn = sqlite3.connect(self.db)
    
    def update_used_field(self, mm) -> None:
        """
        обновляет поле `used` текущей датой
        
        Args:
            mm (str): полное имя файла музыкального трека
        """
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
            cifer (int): число байтов

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
