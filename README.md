# phonedb
Сервис получения информации о номере телефона

### Требования:
	- python3
	- справочник телефонных номеров data.db (~200 Гб)
	
### Подготовка:
```
cd phonedb/
pip3 install -r requirements.txt
python3 -m venv venv
virtualenv venv
source venv/bin/activate
export FLASK_APP=phonedb.py
```

### Запуск:
```
flask run --host 127.0.0.1
```

### Запуск в docker-контейнере:

Для примера - /mnt/data/DB/phonedb - каталог, где находится файл data.db
```
cd phonedb/
docker build -t phonedb:latest .
docker run --name phonedb -d -p 5000:5000 -v /mnt/data/DB/phonedb:/mnt/data/DB/phonedb --rm phonedb:latest
```
