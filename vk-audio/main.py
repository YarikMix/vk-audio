# -*- coding: utf-8 -*-
import time
import re
import threading
from pathlib import Path
from pytils import numeral

import vk_api
from vk_api import audio
import requests

from functions import decline


class VkMusicDownloader():
	def __init__(self):
		self.BASE_DIR = Path(__file__).resolve().parent
		self.PATH = self.BASE_DIR.joinpath("music")

	def auth_handler(self, remember_device=None):
		code = input("Введите код подтверждения\n> ")
		if remember_device is None:
			remember_device = True
		return code, remember_device

	def auth(self):
		"""
		Просим у пользователя логин и пароль от вк
		Создаём новую сессию vk api.
		"""
		login = input("Введите логин\n> ")
		password = input("Введите пароль\n> ")

		vk_session = vk_api.VkApi(
			login=login,
			password=password,
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

	def check_id(self, id: str):
		"""Проверяет, существует ли пользователь с таким id"""
		try:
			id = int(id)
			if id > 0:
				user = self.vk.users.get(user_ids=id)
				if len(user) != 0:
					return True
		except:
			return None

	def check_album_number(self, album_number: str, albums_count: int):
		try:
			if isinstance(int(album_number), int):
				if 0 <= int(album_number) <= albums_count:
					return True
		except:
			return None

	def download_audio(self, audios: list, audio_path):
		"""Скачивает все аудиозаписи из переданного объекта audio."""

		# Number of parallel threads
		self.lock = threading.Semaphore(4)

		# List of threads objects I so we can handle them later
		thread_pool = []

		self.number = 1
		for audio in audios:
			thread = threading.Thread(target=self.download_single_audio, args=(audio, audio_path))
			thread_pool.append(thread)
			thread.start()

			# Add one to our lock, so we will wait if needed.
			self.lock.acquire()

		for thread in thread_pool:
			thread.join()

	def download_single_audio(self, audio, audio_path):
		artist = re.sub(r'[\\/:*?"<>]', " ", audio["artist"])
		song_title = re.sub(r'[\\/:*?"<>]', " ", audio["title"])
		title = "{} - {}".format(artist, song_title)
		file_path = audio_path.joinpath(title + ".mp3")
		if file_path.exists():
			print("{} Уже скачено: {}".format(self.number, title))
		else:
			response = requests.get(audio["url"])
			if response.status_code == 200:
				with open(file_path, "wb") as output_file:
					output_file.write(response.content)
					print("{} Скачивание завершено: {}".format(self.number, title))

		self.number += 1
		self.lock.release()

	def download_album(self, album: dict):
		"""Скачивает все аудиозаписи из переданного альбома"""
		album_title = re.sub(r'[\\/:*?"<>]', " ", album["title"])
		album_path = self.music_path.joinpath(album_title)
		# Создаём папку с аудиозаписями альбома, если её нет
		if not album_path.exists():
			print(f"Создаём папку с аудиозаписями альбома {album_title}")
			album_path.mkdir()

		audios = self.vk_audio.get(
			owner_id=album["owner_id"],
			album_id=album["id"],
			access_hash=album["access_hash"]
		)

		print("{} {} из альбома {}".format(
			numeral.choose_plural(len(audios), "Будет скачена, Будут скачены, Будут скачены"),
			numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей"),
			album_title
		))

		print("Скачивание началось...")

		time_start = time.time()
		self.download_audio(
			audios=audios,
			audio_path=album_path
		)

		time_finish = time.time()
		download_time = round(time_finish - time_start)
		print("{} {} из альбома {} за {}".format(
			numeral.choose_plural(len(audios), "Скачена, Скачены, Скачены"),
			numeral.get_plural(len(audios), "аудиозапись, аудиозаписи, аудиозаписей"),
			album_title,
			numeral.get_plural(download_time, "секунду, секунды, секунд")
		))

	def download_albums(self, albums: list):
		"""Скачивает все аудиозаписи из переданных альбомов"""
		for album in albums:
			self.download_album(album)

	def get_audio(self):
		"""Получаем аудиозаписи пользователя."""
		user_info = self.vk.users.get(
			user_id=self.user_id,
			fields="sex"
		)[0]
		self.decline_username = decline(
			first_name=user_info["first_name"],
			last_name=user_info["last_name"],
			sex=user_info["sex"]
		)

		# Страница пользователя удалена
		if "deactivated" in user_info:
			print("Эта страница удалена")
		else:
			# Профиль закрыт
			if user_info["is_closed"] and not user_info["can_access_closed"]:
				print(f"Профиль {self.decline_username} закрыт")
			else:
				username = f"{user_info['first_name']} {user_info['last_name']}"
				print('Подготовка к скачиванию...')

				self.music_path = self.PATH.joinpath(username)
				# Создаём папку с аудиозаписями пользователя, если её не существует.
				if not self.music_path.exists():
					print(f"Создаём папку с аудиозаписями {self.decline_username}")
					self.music_path.mkdir()

				# Получаем аудиозаписи пользователя
				print(f"Получаем аудиозаписи {self.decline_username}")
				audio = self.vk_audio.get(owner_id=self.user_id)

				print("{} {} {}".format(
					numeral.choose_plural(len(audio), "Будет, Будут, Будут"),
					numeral.choose_plural(len(audio), "скачена, скачены, скачены"),
					numeral.get_plural(len(audio), "аудиозапись, аудиозаписи, аудиозаписей")
				))

				print("Скачивание началось...")

				time_start = time.time()  # сохраняем время начала скачивания
				self.download_audio(
					audios=audio,
					audio_path=self.music_path
				)

				time_finish = time.time()
				download_time = round(time_finish - time_start)
				print("{} {} за {}".format(
					numeral.choose_plural(len(audio), "Скачена, Скачены, Скачены"),
					numeral.get_plural(len(audio), "аудиозапись, аудиозаписи, аудиозаписей"),
					numeral.get_plural(download_time, "секунду, секунды, секунд")
				))

	def get_albums(self):
		print(f"Список альбомов {self.decline_username}")

		# Получаем альбомы пользователя
		albums = self.vk_audio.get_albums(owner_id=self.user_id)
		albums_path = self.music_path.joinpath("альбомы")

		print("0. Скачать все альбомы")
		for i, album in enumerate(albums, start=1):
			print("{}. {}".format(i, album["title"]))

		album_number = input("Введите номер альбома, который хотите скачать. "
							 "Если хотите скачать все альбомы, то введите 0\n> ")

		if self.check_album_number(album_number, len(albums)):
			album_number = int(album_number)
			if album_number == 0:
				print("Будут скачены {}".format(
					numeral.get_plural(len(albums), "альбом, альбома, альбомов")
				))
				self.download_albums(albums)
			else:
				self.download_album(albums[album_number-1])
		else:
			print("Альбома с таким номером нет")

	def main(self):
		# Создаём папку music, если её не существует.
		if not self.PATH.exists():
			self.PATH.mkdir()

		downloader.auth()  # Авторизация

		user_id = input("Введите id пользователя\n> ")
		if self.check_id(user_id):
			self.user_id = int(user_id)
			self.get_audio()
			self.get_albums()
		else:
			print("Пользователя с таким id не существует")

if __name__ == '__main__':
	downloader = VkMusicDownloader()
	downloader.main()