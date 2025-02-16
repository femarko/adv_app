# REST API (backend) для сервиса объявлений
### Идея
Создать RESTful API, архитектура которого облегчает расширение и замену составляющих. 
Например, чтобы можно было безболезненно заменить одну БД на другую.  
Конечно, нет смысла тратить время и силы на дополнительные абстракции, когда функционал 
приложения прост. Но цель этого проекта - самообучение его автора :wink:  
Простая реализация CRUD-приложения на Flask (один из моих проектов во время учебы в Нетологии) - [здесь](https://github.com/Femarko/Flask_HW/tree/task_1).
### Функционал
  - аутентификация и авторизация пользователей
  - CRUD-операции с объявлениями
  - поиск объявлений, в т.ч. по тексту
### Структура
  - [domain](https://github.com/femarko/adv_app/tree/main/app/domain) (предметная область):
    - ```models.py``` - классы Python, *не связанные с таблицами БД*
    - ```services.py``` - функции, создающие пользователя / объявление, обновляющие и возвращающие их параметры
    - ```errors.py``` - кастомные классы исключений, использующиеся в приложении как часть бизнес-логики
  - [orm](https://github.com/femarko/adv_app/tree/main/app/orm):
    - ```__init__.py``` - инициализация object-relational mapper (```SQLAlchemy```)
    - ```table-mapper.py``` - мэппинг классов python из ```models.py``` с таблицами БД (imperative mapping)
  - [repository](https://github.com/femarko/adv_app/tree/main/app/repository) (абстракция постоянного хранилища данных):
    - ```repository.py``` - абстракция, реализующая доступ к БД
    - ```filtering.py``` - функционал фильтрации данных из постоянного хранилища
  - [pass_hashing_and_validation](https://github.com/femarko/adv_app/tree/main/app/pass_hashing_and_validation):
    - ```pass_hashing.py``` - хэширование паролей (библиотека ```bcrypt```)
    - ```validation.py``` - валидация входящих данных (библиотека ```pydantic```)
  - ```flask_entrypoints``` (web-API приложения):
    - ```views.py``` - функции, которые принимают HTTP-запросы, вызывают функции из ```service_layer/app_manager.py```, передают им входящие данные и зависимости, возвращают ответы на HTTP-запросы
    - ```authentication.py``` - аутентификация пользователей (библиотека ```flask_jwt_extended```)
    - ```error_handlers.py``` - реализация кастомного исключения для web-API
    - ```run_app.py``` - запуск приложения ```Flask```
    - ```__init__.py``` - инициализация приложения ```Flask```
### БД
  - БД (```PostreSQL```) и средство просмотра ее таблиц (```PGAdmin```) поднимаются в docker-контейнерах (```docker-compose.yml```).


