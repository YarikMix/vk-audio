# -*- coding: utf-8 -*-
# Импорт библиотек
import vk_api
from vk_api import audio
import pytz
import requests
import datetime
from time import time
import os
import pickle
import json


def get_time():
    # возвращает время формата ДД.ММ.ГГ ЧЧ:ММ:СС (по МСК)
    # например, 01.01.01 13:37:00
    return datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Europe/Moscow')), "%d.%m.%Y %H:%M:%S")


def console_log(text):
    # вывод текста в консоль со временем
    print('[{}] {}'.format(get_time(), text[0].upper() + text[1:]))


def get_num_ending(num, cases):
    num = num % 100
    if 11 <= num <= 19:
        return cases[2]
    else:
        i = num % 10
        if i == 1:
            return cases[0]
        elif i in [2, 3, 4]:
            return cases[1]
        else:
            return cases[2]


class VkMusicDownloader():
    CONFIG_DIR = "config"
    USERDATA_FILE = f"{CONFIG_DIR}/UserData.datab"  # файл хранит логин, пароль и id
    REQUEST_STATUS_CODE = 200
    path = 'music/'

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if remember_device is None:
            remember_device = True
        return code, remember_device

    def save_user_data(self):
        save_data = [self.login, self.password]

        with open(self.USERDATA_FILE, 'wb') as dataFile:  # записываем данные в файл
            pickle.dump(save_data, dataFile)

    def auth(self, new=False):
        try:
            if os.path.exists(self.USERDATA_FILE) and new == False:
                with open(self.USERDATA_FILE, 'rb') as DataFile:
                    loaded_data = pickle.load(DataFile)

                self.login = loaded_data[0]
                self.password = loaded_data[1]
            else:  # если есть, но пользователь выбрал новую авторизацию, то удаляем данных и просим ввести новые
                if os.path.exists(self.USERDATA_FILE) and new == True:
                    os.remove(self.USERDATA_FILE)

                self.login = input("Введите логин\n> ")
                self.password = input("Введите пароль\n> ")
                self.save_user_data()

            save_data = [self.login, self.password]
            with open(self.USERDATA_FILE, 'wb') as dataFile:
                pickle.dump(save_data, dataFile)  # сохраняем введённые данные

            vk_session = vk_api.VkApi(
                login=self.login,
                password=self.password
            )
            try:
                vk_session.auth()
            except vk_api.exceptions.Captcha:
                print("Данные некорректны, повторите снова.")
                self.auth(new=True)
            except:
                vk_session = vk_api.VkApi(
                    login=self.login,
                    password=self.password,
                    auth_handler=self.auth_handler
                )
                vk_session.auth()
            print('Вы успешно авторизовались.')
            self.vk = vk_session.get_api()
            self.vk_audio = audio.VkAudio(vk_session)
        except KeyboardInterrupt:
            console_log('Вы завершили выполнение программы.')

    def download_audio(self, audio, count=1):
        for i in audio:
            fileM = "{} - {}.mp3".format(i["artist"], i["title"])
            # fileM = re.sub("/", "_", fileM)
            try:
                if os.path.exists(fileM):
                    console_log("{} Уже скачен: {}".format(count, fileM))
                else:
                    r = requests.get(i["url"])
                    if r.status_code == self.REQUEST_STATUS_CODE:
                        console_log("{} Скачивание завершено: {}".format(count, fileM))
                        with open(fileM, "wb") as output_file:
                            output_file.write(r.content)
            except OSError:
                if not os.path.exists(fileM):
                    console_log("{} !!! Не удалось скачать аудиозапись: {}".format(count, fileM))

            count += 1

    def download(self, user_id):
        console_log('Подготовка к скачиванию...')

        # В папке music создаем папку с именем пользователя, которого скачиваем.
        info = self.vk.users.get(user_id=user_id)[0]
        username = "{} {}".format(info['first_name'], info['last_name'])
        music_path = "{}/{}".format(self.path, username)
        if not os.path.exists(music_path):
            console_log("Создаём папку с аудиозаписями пользователя {} {}".format(
                info['first_name'],
                info['last_name']))
            os.makedirs(music_path)

        time_start = time()  # сохраняем время начала скачивания
        os.chdir(music_path)  # меняем текущую директорию

        audio = self.vk_audio.get(owner_id=user_id)
        console_log("Будет скачано: {} {}.".format(
            len(audio),
            get_num_ending(len(audio), [
                "аудиозапись",
                "аудиозаписи",
                "аудиозаписей"
            ])
        ))

        console_log("Скачивание началось...\n")

        # скачиваем музыку
        self.download_audio(audio=audio)

        time_finish = time()
        console_log("Скачано {} {} за: {} секунд.".format(
            len(audio),
            get_num_ending(len(audio), [
                "аудиозапись",
                "аудиозаписи",
                "аудиозаписей"
            ]),
            round(time_finish - time_start, 1)
        ))

    def main(self, auth_dialog="y"):
        try:
            if not os.path.exists(self.CONFIG_DIR):
                os.mkdir(self.CONFIG_DIR)
            if not os.path.exists(self.path):
                os.makedirs(self.path)

            if auth_dialog == "y":
                auth_dialog = input("Авторизоваться заново? y/n\n> ")
                if auth_dialog == "y":
                    self.auth(new=True)
                elif auth_dialog == "n":
                    self.auth(new=False)
                else:
                    print('Ошибка, неверный ответ.')
                    self.main()
            elif auth_dialog.lower() == 'n':
                self.auth(new=False)

            target = input("Хотите скачать аудиозаписи со своей страницы вк? y/n\n> ")
            if target == "y":
                with open("vk_config.v2.json") as vk_config:
                    uid = json.load(vk_config)[self.login]["cookies"][1]["value"]
                self.download(uid)
            elif target == "n":
                user_id = input("Введите id пользователя:\n> ")
                self.download(user_id)
            else:
                print("Ошибка, неверный ответ.")
                self.main()

        except KeyboardInterrupt:
            console_log('Вы завершили выполнение программы.')


if __name__ == '__main__':
    vkMD = VkMusicDownloader()
    vkMD.main(auth_dialog="y")
