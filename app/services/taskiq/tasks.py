# services/taskiq/tasks.py

from services.taskiq.init_app import taskiq_redis_broker


@taskiq_redis_broker.task
async def test_task():
    print("✅ TrainerAPI: 🧠 TaskIQ - test task выполнена")
