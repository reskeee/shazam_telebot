
# Настройка виртуального окружения
## В корне папки с проектом
```sh
python -m venv venv
```

## После создания `venv`
```sh
.\venv\Scripts\activate # Windows
```
```sh
source venv/bin/activate # Unix
```

## Установка необходимых библиотек
```sh
pip install -r requirements.txt
```

## Для корректной работы необходимо создать папки `music` и `voices`

## Также необходимо создать файл `.env` и по аналогии с файлом `.env_example` вставить после `TOKEN=` токен своего бота.

## Запуск
```sh
python main.py
```

Приятного пользования!
