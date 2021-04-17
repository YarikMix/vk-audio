import math
import time
import logging
import re
from pathlib import Path

import yaml
import aiohttp
import aiofiles
import asyncio
import vk_api
from vk_api import audio
from tqdm.asyncio import tqdm
from pytils import numeral

from functions import decline


BASE_DIR = Path(__file__).resolve().parent
MUSIC_DIR = BASE_DIR.joinpath("Музыка")
CONFIG_PATH = BASE_DIR.joinpath("config.yaml")
VK_CONFIG_PATH = BASE_DIR.joinpath("vk_config.v2.json")

with open(CONFIG_PATH, encoding="utf-8") as ymlFile:
    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger('vk_api')
logger.disabled = True


def auth_handler(remember_device=None):
    code = input("Введите код подтверждения\n> ")
    if remember_device is None:
        remember_device = True
    return code, remember_device

def auth():
    vk_session = vk_api.VkApi(
        login=config["login"],
        password=config["password"],
        auth_handler=auth_handler
    )
    try:
        vk_session.auth()
    except Exception as e:
        logging.info("Неправильный логин или пароль")
        exit()
    finally:
        logging.info('Вы успешно авторизовались.')
        return vk_session

def check_id(id: str) -> bool:
    """Проверяет, существует ли пользователь с таким id"""
    try:
        id = int(id)
        if id > 0:
            user = vk.users.get(user_ids=id)
            if len(user) != 0:
                return True
    except:
        return False


class VkUserAlbumsDownloader:
    async def download_album(self, album: dict):
        """Скачивает все аудиозаписи из переданного альбома"""
        album_title = re.sub(r'[\\/:*?"<>|]', " ", album["title"])
        album_path = self.user_albums_path.joinpath(album_title)

        # Создаём папку с аудиозаписями альбома, если её нет
        if not album_path.exists():
            logging.info(f"Создаём папку с аудиозаписями альбома '{album_title}'")
            album_path.mkdir()

        # Получаем аудиозаписи из альбома
        logging.info(f"Получаем аудиозаписи из альбома '{album_title}'")

        audios = vk_audio.get(
            owner_id=album["owner_id"],
            album_id=album["id"],
            access_hash=album["access_hash"]
        )

        logging.info("{} {} из альбома {}".format(
            numeral.choose_plural(len(audios), "Будет скачена, Будут скачены, Будут скачены"),
            numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей"),
            album_title
        ))

        logging.info("Скачивание началось...")

        time_start = time.time()
        await audio_downloader.download_audios(audios=audios, audio_dir=album_path)

        time_finish = time.time()
        download_time = round(time_finish - time_start)
        logging.info("{} {} из альбома {} за {}".format(
            numeral.choose_plural(len(audios), "Скачена, Скачены, Скачены"),
            numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей"),
            album_title,
            numeral.get_plural(download_time, "секунду, секунды, секунд")
        ))

    async def main(self):
        try:
            self.user_albums_path = user_audio_path.joinpath("Альбомы")

            # Создаём папку c альбомами пользователя, если её не существует
            if not self.user_albums_path .exists():
                logging.info(f"Создаём папку с альбомами {decline_username}")
                self.user_albums_path.mkdir()

            print(f"Список альбомов {decline_username}")

            # Получаем альбомы пользователя
            albums = vk_audio.get_albums(owner_id=user_id)

            print("0. Скачать все альбомы")
            for i, album in enumerate(albums, start=1):
                print("{}. {}".format(i, album["title"]))

            album_number = input("Введите номер альбома, который хотите скачать. Если хотите скачать все альбомы, то введите 0\n> ")

            try:
                if album_number == "0":
                    logging.info("Будут скачены {}".format(
                        numeral.get_plural(len(albums), "альбом, альбома, альбомов")
                    ))

                    time_start = time.time()

                    for album in albums:
                        await self.download_album(album)

                    time_finish = time.time()
                    download_time = math.ceil(time_finish - time_start)
                    logging.info("{} {} за {}".format(
                        numeral.choose_plural(len(albums), "Скачена, Скачены, Скачены"),
                        numeral.get_plural(len(albums), "альбом, альбома, альбомов"),
                        numeral.get_plural(download_time, "секунду, секунды, секунд")
                    ))

                else:
                    await self.download_album(albums[int(album_number) - 1])
            except Exception as e:
                logging.info("Альбома с таким номером нет")
        except vk_api.exceptions.AccessDenied:
            logging.info(f"Альбомы {decline_username} скрыты :(")

            # Удаляем папку с альбомами пользователя
            self.user_albums_path.rmdir()


class VkUserAudioDownloader:
    async def download_audio(self, session: aiohttp.ClientSession, audio_url: str, audio_path: Path):
        if audio_path.exists():
            pass
        else:
            try:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(audio_path, "wb") as f:
                            await f.write(await response.read())
                            await f.close()
            except Exception as e:
                pass

    async def download_audios(self, audios: list, audio_dir):
        """Скачивает все фото из переданного списка"""
        async with aiohttp.ClientSession() as session:
            futures = []
            for audio in audios:
                artist = re.sub(r'[\\/:*?"<>|]', " ", audio["artist"])
                title = re.sub(r'[\\/:*?"<>|]', " ", audio["title"])
                audio_title = "{} - {}.mp3".format(artist, title)
                audio_path = audio_dir.joinpath(audio_title)
                futures.append(self.download_audio(session, audio["url"], audio_path))

            for future in tqdm(asyncio.as_completed(futures), total=len(futures)):
                await future

    async def main(self):
        try:
            logging.info("Получаем аудиозаписи...")

            # Получаем аудиозаписи пользователя
            audios = vk_audio.get(owner_id=user_id)

            logging.info("{} {} {}".format(
                numeral.choose_plural(len(audios), "Будет, Будут, Будут"),
                numeral.choose_plural(len(audios), "скачена, скачены, скачены"),
                numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей")
            ))

            logging.info("Скачивание началось...")

            time_start = time.time()

            await self.download_audios(audios=audios, audio_dir=user_audio_path)

            time_finish = time.time()
            download_time = math.ceil(time_finish - time_start)
            logging.info("{} {} за {}".format(
                numeral.choose_plural(len(audios), "Скачена, Скачены, Скачены"),
                numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей"),
                numeral.get_plural(download_time, "секунду, секунды, секунд")
            ))
        except vk_api.exceptions.AccessDenied:
            logging.info(f"Аудиозаписи {decline_username} скрыты :(")

            # Удаляем папку с аудиозаписями пользователя
            user_audio_path.rmdir()


if __name__ == '__main__':
    # Создаём папку c загрузками, если её не существует
    if not MUSIC_DIR.exists():
        MUSIC_DIR.mkdir()

    vk_session = auth()
    vk = vk_session.get_api()
    vk_audio = audio.VkAudio(vk_session)

    user_id = input("Введите id пользователя\n> ")
    if check_id(user_id):
        audio_downloader = VkUserAudioDownloader()
        albums_downloader = VkUserAlbumsDownloader()
        loop = asyncio.get_event_loop()

        # Получаем информацию о пользователе
        user_info = vk.users.get(
            user_id=user_id,
            fields="sex"
        )[0]

        decline_username = decline(
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            sex=user_info["sex"]
        )

        # Страница пользователя удалена
        if "deactivated" in user_info:
            logging.info("Эта страница удалена")
        else:
            # Профиль закрыт
            if user_info["is_closed"] and not user_info["can_access_closed"]:
                logging.info(f"Профиль {decline_username} закрыт :(")
            else:
                username = f"{user_info['first_name']} {user_info['last_name']}"
                user_audio_path = MUSIC_DIR.joinpath(username)

                # Создаём папку с аудиозаписями пользователя, если её не существует.
                if not user_audio_path.exists():
                    logging.info(f"Создаём папку с аудиозаписями {decline_username}")
                    user_audio_path.mkdir()

                time.sleep(0.1)

                prompt = input("1.Скачать аудиозаписи \n2.Скачать альбомы\n> ")
                if prompt == "1":
                    loop.run_until_complete(audio_downloader.main())
                elif prompt == "2":
                    loop.run_until_complete(albums_downloader.main())
                else:
                    logging.info("Выход из программы")
    else:
        logging.info("Пользователя с таким id не существует")

    VK_CONFIG_PATH.unlink()  # Удаляем конфиг вк