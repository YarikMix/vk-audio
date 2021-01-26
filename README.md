Скрипт python3 для скачивания вашей и не вашей музыки из вк.

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```
Запускаем программу:
```bash
python ./src/main.py
```
При первом запуске программа попросит вас авторизоваться:
```bash
Авторизоваться заново? y/n
> y
```
Далее вводим свой логин от аккаунта вконтакте:
```bash
Введите логин
> my_login 
```
Затем пароль:
```bash
Введите пароль
> my_password
```
Если введёные данные корректны, то вы увидите следующее сообщение:
```bash
Вы успешно авторизовались.
Хотите скачать свои аудиозаписи?
1: Да
2: Нет
```
Если хотим скачать свои аудизаписи вводим 1. Начнётся процесс скачивания аудиозаписей с вашей страницы
```bash
> 1
```
Если хотим скачать аудиозаписи другого человека, то вводим 2
```bash
> 2
```
Вводим id человека, аудиозаписи которого хотим скачать
```bash
Введите id профиля
> id
```
Узнать id по имени можно [здесь](http://regvk.com/id/)
