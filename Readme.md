# Заполнение коллекции из случайных треков

> Проект учебный, мне было просто интересно его реализовать

## Задача

Есть коллекция музыкальных файлов гигантского размера, нажитая непосильными усилиями за последние несколько лет.
Есть какой-то условный плеер с ограниченным объемом внутреннего хранилища.  
Требуется иметь возможность перезаписывать плеер максимально невстречавшимися ранее треками.

## Реализация

Скрипт понимает две команды: `init` и `burn`

- **init**: сканирование музыкальной коллекции, сохранение путей в БД
- **burn**: получение из БД списка треков до определенного размера (хранилища плеера) и копирование треков на носитель плеера.

```
$ py sdburn.py -h
usage: MusicCDBurner [-h] [-d DB_FILE] [-c COL_PATH] [-m MUSIC_DIR] [-s CDSIZE] [-f] [-v] [--version]
                     {init,burn}

Создание музыкальных сборников

positional arguments:
  {init,burn}   Инициализация данных о музыкальном каталоге

options:
  -h, --help    show this help message and exit
  -d DB_FILE    Имя файла базы данных
  -c COL_PATH   Каталог формируемой коллекции
  -m MUSIC_DIR  Каталог с музыкой
  -s CDSIZE     Требуемый размер коллекции (байт)
  -r            Добавление случайных префиксов к имени файла (burn)
  -f            Перезаписывать каталоги и файлы
  -v            Режим избыточного протоколирования
  --version     show program's version number and exit
```