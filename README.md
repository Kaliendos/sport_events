# sport_events
Бэкенд приложения для поиска людей для совместных тренировок и спортивных мероприятий. 
Используемые технологии:
FastAPi, Postgresql и его расширение PostGis.
В качестве орм используется sqlalchemy
В качестве решения jwt  авторизации была выбрана библиотека fastapi users.
Проект протестирован через pytest.
# установка 
1. клонировать репозиторий
2. Перейти в дирректорию проекта cd sport_events
3. установить зависимости pip install -r requirements.txt
4. Разввернуть постгрес локально, создать базу и в базу добавить расширение postgis CREATE EXTENSION postgis;
5. задать конфиги базы в src.core.database файле
7. выполнить миграции alembic upgrade head
8. Запустить сервер uvicorn src.main:app --reload в корне проекта

