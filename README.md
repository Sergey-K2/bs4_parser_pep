# Проект парсинга pep

## Технологии
Python BeautifulSoup4 Prettytable 

## Парсинг документов PEP
Парсер собирает данные обо всех PEP документах, сравнивает статусы и записывает их в файл, также реализованы сбор информации о статусе версий, скачивание архива с документацией и сбор ссылок о новостях в Python, логирует свою работу и ошибки в командную строку и файл логов.

## Как запустить проект:
1. Клонировать репозиторий и перейти в него в командной строке:
    ```
    git clone https://github.com/Sergey-K2/bs4_parser_pep.git
    cd bs4_parser_pep 
    ```
2. Cоздать и активировать виртуальное окружение:
    ```
    python -m venv venv
    source venv/Scripts/activate
    ```
3. Установить зависимости из файла requirements.txt:
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Примеры команд
1. Вывод справки по использованию:
    ```
    python main.py pep -h
    ```
2. Создаст csv файл с таблицей из двух колонок: «Статус» и «Количество»:
    ```
    python main.py pep -o file
    ```
3. Вывод таблицы prettytable с тремя колонками: "Ссылка на документацию", "Версия", "Статус":
    ```
    python main.py latest-versions -o pretty 
    ```
4. Выводит ссылки в консоль на нововведения в python:
    ```
    python main.py whats-new
    ```

## Автор: 
Сергей Козлов
GitHub: [Sergey-K2](https://github.com/Sergey-K2)