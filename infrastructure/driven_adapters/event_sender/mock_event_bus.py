from uuid import UUID


class MockEventBus:
    def send_task_completed(self, task_id: UUID, user_id: UUID):
        print(f"[EVENT] TaskCompleted: task_id={task_id}, user_id={user_id}")
