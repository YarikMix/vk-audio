# -*- coding: utf-8 -*-
import time
from pathlib import Path

import vk_api
from vk_api import audio
import requests

from functions import *


class VkMusicDownloader():
	def __init__(self):
		self.BASE_DIR = Path(__file__).resolve().parent
		self.PATH = BASE_DIR.joinpath("music")
		self.REQUEST_STATUS_CODE = 200
		self.HEADERS = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
		}

	def auth_handler(self, remember_device=None):
		code = input("Введите код подтверждения\n> ")
		if remember_device is None:
			remember_device = True
		return code, remember_device

	def auth(self):
		"""Просим у пользователя логин и пароль от вк,
		Создаём новую сессию vk api."""
		self.login = input("Введите логин\n> ")
		self.password = input("Введите пароль\n> ")

		vk_session = vk_api.VkApi(
			login=self.login,
			password=self.password,
			auth_handler=self.auth_handler
		)
		try:
			vk_session.auth()
		except Exception as e:
			print("Не получилось авторизоваться, попробуйте снова.")
			self.auth()
		print('Вы успешно авторизовались.')
		self.vk = vk_session.get_api()
		self.vk_audio = audio.VkAudio(vk_session)

	def download_audio(self, audio, count=1):
		"""Скачивает все аудиозаписи из переданного объекта audio."""
		for i in audio:
			title = "{} - {}".format(i["artist"], i["title"])
			file_path = self.music_path.joinpath(title + ".mp3")
			try:
				if file_path.exists():
					print("{} Уже скачен: {}".format(count, title))
				else:
					r = requests.get(i["url"], headers=self.HEADERS)
					if r.status_code == self.REQUEST_STATUS_CODE:
						with open(file_path, mode="wb") as output_file:
							output_file.write(r.content)
							print("{} Скачивание завершено: {}".format(count, title))
					else:
						raise OSError()
			except OSError:
				if file_path.exists():
					print("{} !!! Не удалось скачать аудиозапись: {}".format(count, title))

			count += 1

	def download(self, user_id):
		"""Получаем аудиозаписи пользователя."""

		info = self.vk.users.get(user_id=user_id)[0]
		username = info['first_name'] + " " + info['last_name']

		# Профиль закрыт
		if info["is_closed"] and not info["can_access_closed"]:
			print(f"Профиль {decline(username)} закрыт")
		else:
			print('Подготовка к скачиванию...')
			
			self.music_path = self.PATH.joinpath(username)
			# Создаём папку с аудиозаписями пользователя, если её не существует.
			if not self.music_path.exists():
				print(f"Создаём папку с аудиозаписями {decline(username)}")
				self.music_path.mkdir(parents=True, exist_ok=True)

			audio = self.vk_audio.get(owner_id=user_id)
			print("Будет скачано: {} {}".format(
				len(audio),
				get_num_ending(len(audio), [
					"аудиозапись",
					"аудиозаписи",
					"аудиозаписей"
				])
			))

			time_start = time.time()  # сохраняем время начала скачивания

			print("Скачивание началось...\n")

			self.download_audio(audio=audio) # скачиваем музыку

			time_finish = time.time()  # сохраняем время конца скачивания
			print("Скачано {} {} за: {}".format(
				len(audio),
				get_num_ending(len(audio), [
					"аудиозапись",
					"аудиозаписи",
					"аудиозаписей"
				]),
				download_time(round(time_finish - time_start))
			))

			# # Получаем альбомы пользователя
			# albums = self.vk_audio.get_albums(owner_id=user_id)
			# albums_dialog = input(
			#     "Хотите скачать {} {}? y/n\n> ".format(
			#         len(albums),
			#         get_num_ending(len(albums), [
			#             "альбом",
			#             "альбома",
			#             "альбомов"
			#         ])
			#     )
			# )
			# if albums_dialog == "y":
			#     try:
			#         for i in albums:
			#             audio = self.vk_audio.get(owner_id=user_id, album_id=i['id'])
			#             time_start = time()

			#             print("Будет скачено: {} {} из альбома {}".format(
			#                 len(audio),
			#                 get_num_ending(len(audio), [
			#                     "аудиозапись",
			#                     "аудиозаписи",
			#                     "аудиозаписей"
			#                 ]),
			#                 i["title"]
			#             ))

			#             album_path = "{}/{}".format(music_path, i["title"])
			#             print(album_path)
			#             if not os.path.exists(album_path):
			#                 os.makedirs(album_path)

			#             os.chdir(album_path)  # меняем текущюю директорию

			#             # скачиваем музыку
			#             self.download_audio(audio=audio)

			#             time_finish = time()
			#             print("Скачано {} {} из альбома {} за: {} сек.".format(
			#                 len(audio),
			#                 get_num_ending(len(audio), [
			#                     "аудиозапись",
			#                     "аудиозаписи",
			#                     "аудиозаписей"
			#                 ]),
			#                 i["title"],
			#                 round(time_finish - time_start, 1)
			#             ))

			#         os.chdir("../../../")
				# except vk_api.AccessDenied:
				#     print("Не получилось скачать альбомы пользователя {}".format(username))
			# elif albums_dialog == "n":
			#     console_log("Выход из программы.")
			# else:
			#     print('Ошибка, неверный ответ.')
			#     self.main()

	def main(self):
		# Создаём папку music, если её не существует.
		if not self.PATH.exists():
			self.PATH.mkdir()

		self.auth() # Авторизация

		target = input("Хотите скачать аудиозаписи со своей страницы вк? y/n\n> ")
		if target == "y":
			user_id = self.vk.users.get()[0]["id"]
			self.download(user_id)
		elif target == "n":
			user_id = int(input("Введите id пользователя:\n> "))
			if user_id in range(1, get_last_vk_id() + 1):
				self.download(user_id)
			else:
				print("Пользователя с таким id не существует")
				self.main()
		else:
			print("Ошибка, неверный ответ")
			self.main()


if __name__ == '__main__':
	vkMD = VkMusicDownloader()
	vkMD.main()