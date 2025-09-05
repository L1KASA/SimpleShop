# [![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=450&size=30&duration=5100&pause=800&width=437&lines=django-shop)](https://git.io/typing-svg)

## Установка и запуск
### 1. Создание виртуального окружения
#### Windows:
````
1. python -m venv venv
2. venv\Scripts\activate
````
#### Linux/macOS:
````
python -m venv venv
source venv/bin/activate
````
#### 2. Установить зависимости
````
pip install -r requirements.txt
````
#### 3. Применить миграции
````
python manage.py migrate
````
#### 4. Запустить сервер 
```
# Стандартный запуск
python manage.py runserver

# Запуск с HTTPS (требует настройки)
python manage.py runserver_plus --cert-file cert.crt
```
#### 5. Открыть в браузере
* HTTP: http://127.0.0.1:8000/
* HTTPS: https://siterandomshop.ru:8000/

## Структура проекта

## Основные возможности

## Настройка HTTPS с доменом siterandomshop.ru:

### 1. Открыть файл hosts, расположенный по маршруту:
#### Windows:
```
C:\Windows\System32\drivers\etc\hosts
```
#### Linux/macOS:
```
/etc/hosts
```
### 2. Добавить строку
```
127.0.0.1       siterandomshop.ru
```
### 3. Запустить с HTTPS
```
python manage.py runserver_plus --cert-file cert.crt
```
