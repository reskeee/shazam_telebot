import requests
from bs4 import BeautifulSoup

URL = "https://rus.hitmotop.com/search" # Ссылка на сайт, на котором будет проводиться поиск
tracks_amount = 5 # Количество треков, которые будут выдаваться при поиске


# Функция для поиска трека
def find_track(track_name: str) -> dict:
    response = requests.get(f"{URL}?q={track_name}") # Делает запрос к странце и получает HTML документ
    # print(response.url)
    soup = BeautifulSoup(response.content, features="html.parser") # Создание объекта "супа" для парсинга страницы
    # print(soup, type(soup))

    track_list = soup.findAll("div", "track__info")[0:tracks_amount:]
    # print(track_list)
    track_dict = {} # Создание словаря для треков

    # По тегам в html коде страницы парсит название, исполнителя, время трека и ссылку не его скачивание.
    for track in track_list:
        name = track.findAll("div", "track__title")[
            0].string.replace("\n", '').replace(' ', '')
        artist = track.find("div", "track__desc").string
        time = track.find("div", "track__fulltime").string
        href = track.findAll("a")[1].get("href")

        # print(name, artist, time, href)
        track_dict[f'{artist} - {name}'] = (href, time) # Наполнение словаря элементами

    return track_dict # Возвращает наполненный словарь


def download_track(href, name) -> str:
    req = requests.get(href, stream=True) # Получение потока байтов по ссылке на скачивание трека

    path = f"music/{name}.mp3" # Определение пути к файлу

    # Открытие файла (если такого файла нет, он создается), запись в него трека и сохранение на диске
    with open(path, "wb") as file:
        file.write(req.content)

    print("Успешно скачано")
    return path # Возвращение пути, по котрому скачан трек


if __name__ == "__main__":
    print(find_track("metallica"))
