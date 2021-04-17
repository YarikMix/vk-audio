## Скрипт для асинхронного скачивания музыки пользователей ВКонтакте

### Системные требования:

* Python 3 и выше
* Доступ к интернету
* Логин и пароль от ВКонтакте

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```

В файл config.yaml вписываем свой логин и пароль от ВКонтакте:
```yaml
login: ""  # Ваш логин он ВКонтакте
password: ""  # Ваш пароль он ВКонтакте
```

Запускаем скрипт:
```bash
python vk-audio/main.py
```

Вводим id пользователя, аудиозаписи которого нужно скачать:
```bash
Введите id профиля
> 
```

Узнать id человека или группы ВКонтакте можно [тут](https://regvk.com/id/)

Выбираем аудиозаписи пользователя, или альбомы
```bash
1.Скачать аудиозаписи
2.Скачать альбомы
>
```