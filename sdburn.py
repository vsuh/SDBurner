"""
Приложение MusicCDBurner.

Этот скрипт  формирует базу данных из имен файлов музыкальных треков 
или записывает экземпляр музыкальной коллекции в зависимости 
от переданной команды пользователя. 
Скрипт использует файл настройки .env или переменные окружения и/или 
аргументы командной строки для управления поведением.

В зависимости от перреданной команды, скрипт заполняет базу данных или 
формирует коллекцию треков заданного размера. 

Примеры:
    python sdburn.py init
    python sdburn.py burn -d my_database.sqlite -m /path/to/music -s 700000000

"""

from os import getenv
import time
from dotenv import load_dotenv, find_dotenv
import argparse
import pathlib
from src.initdb import InitDB
from src.burning import  BurnCD
import logging

VER='1.0.0.2'

load_dotenv()

DBFILE=getenv("DBFILE")
CDSIZE=getenv("CDSIZE")
MUSIC_DIR=getenv("MUSIC_DIR")
COL_PATH="sd"

parser = argparse.ArgumentParser(prog='MusicCDBurner',
                    description="Создание музыкальных сборников",)

parser.add_argument("cmd", choices=["init", "burn"], help="Инициализация данных о музыкальном каталоге")
parser.add_argument("-d", dest="db_file", help="Имя файла базы данных", default=DBFILE)
parser.add_argument("-c", dest="col_path", help="Каталог формируемой коллекции", default=COL_PATH, type=pathlib.Path)
parser.add_argument("-m", dest="music_dir", help="Каталог с музыкой", default=MUSIC_DIR, type=pathlib.Path)
parser.add_argument("-s", dest="cdsize", help="Требуемый размер коллекции (байт)", default=CDSIZE, type=int)
parser.add_argument("-f", dest="force", help="Перезаписывать каталоги и файлы", action='store_true')
parser.add_argument("-v", dest="debug", help="Режим избыточного протоколирования", action='store_true')
parser.add_argument("--version", action="version", help="Показать версию скрипта", version=f'{parser.prog} {VER}')

if __name__ == '__main__':
    args = parser.parse_args()    
    log = logging.getLogger(__name__)
    log_fmt = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"
    begin_tm = time.time()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_fmt)
    else:
        print(f'Запуск {parser.prog} в режиме "{args.cmd}". Протокол сохраняется в "sdburn.log"')
        logging.basicConfig(level=logging.INFO, filename='sdburn.log', format=log_fmt)

    # print(args)
    if args.cmd=='init':
        InitDB(args.music_dir, args.db_file, args.force, log)
    elif args.cmd=='burn':
        BurnCD(args.db_file, args.col_path, args.cdsize, args.force, log)
    
    tm = time.time() - begin_tm
    if args.debug:
        log.info(f'Время исполнения {round(tm,1)} сек.')
    else:
        print(f'Время исполнения {round(tm,1)} сек.')
        