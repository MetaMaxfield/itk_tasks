from django.db import models, transaction


class TaskQueue(models.Model):
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="pending")  # Статус задачи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


# Как вариант можно реализовать функцию с таким функционалом в модели...
# ...и удобно изменять значение статуса через вызов метода у task
def _change_task_name(task: TaskQueue) -> TaskQueue:
    """Call only in transaction!"""
    task.status = "in_progress"
    task.save(
        update_fields=[
            "status",
        ]
    )
    return task


# В условии не сказано что должна должна возвращать функция при наличии задачи...
# ...со статусом "pending". Однако, если ничего не возвращать, то в обоих случаях...
# ...будет возвращено "None". Поэтому я решил, что функция будет возвращать...
# ...необходимую задачу с отредактированным статусом.
@transaction.atomic
def extract_task() -> None | TaskQueue:
    task = (
        TaskQueue.objects.select_for_update()
        .filter(status="pending")
        .order_by("created_at")
        .first()
    )
    return None if task is None else _change_task_name(task)
