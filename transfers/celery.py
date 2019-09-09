from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coldwallet.settings')

app = Celery('coldwallet', backend='rpc://')
app.config_from_object('django.conf.settings')

app.autodiscover_tasks()

app.conf.beat_schedule ={
    'check_transfers_every_minute' : {
        'task' : 'transfers.tasks.worker_scan_transfers',
        'schedule' : crontab()
    }
}
