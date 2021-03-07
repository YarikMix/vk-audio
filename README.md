## Скрипт для скачивания музыки пользователей ВКонтакте
С помощью этого скрипта можно скачивать аудиозаписи пользователей ВКонтакте, в том числе и альбомы.

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```
Запускаем скрипт:
```bash
python vk-audio/main.py
```
Вводим свой логин и пароль от аккаунта ВКонтакте:
```bash
Введите логин
> my_login 
Введите пароль
> my_password
```
Вводим id человека, аудиозаписи которого нужно скачать:
```bash
Введите id профиля
> id
```
Аудиозаписи пользователя начнут скачиваться в папку music:<br><br>
![](https://github.com/YarikMix/vk-audio/raw/main/images/1.png)<br><br>
После того, как все аудиозаписи скачаются, выведется список альбомов пользователя.<br><br>
![](https://github.com/YarikMix/vk-audio/raw/main/images/2.png)<br><br>
Выберите номер альбома, который хотите скачать. **Если хотите скачать все альбомы, то введите 0**<br><br>
![](https://github.com/YarikMix/vk-audio/raw/main/images/3.png)<br><br>
Готово, вы великолепны!<br><br>
![](https://github.com/YarikMix/vk-audio/raw/main/images/3.png)