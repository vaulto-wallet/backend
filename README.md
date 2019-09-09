# Vaulto project

## DJANGO Backend

### Setup
```
sudo apt-get install python3-dev libssl-dev
pip install -r requirements.txt
```

### Starting
```
python manage.py runserver
celery -A coldwallet worker --loglevel=info
```


