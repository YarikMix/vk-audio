Скрипт на Python для скачивания вашей и не вашей музыки из вк.

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```
Запускаем скрипт:
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
Хотите скачать аудиозаписи со своей страницы вк? y/n
```
Если хотим скачать свои аудизаписи - вводим 'y'. Начнётся процесс скачивания аудиозаписей с вашей страницы:
```bash
> y
```
Если хотим скачать аудиозаписи другого человека, то вводим 'n':
```bash
> n
```
Вводим id человека, аудиозаписи которого хотим скачать:
```bash
Введите id профиля
> id
```
Узнать id по имени можно [здесь](http://regvk.com/id/)
