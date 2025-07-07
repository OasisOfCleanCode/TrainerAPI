# services/celery/tasks.py

from services.celery.init_app import celery_app


@celery_app.task
def test():
    print("✅ TrainerAPI: 🐰 Celery - test task выполнена")
