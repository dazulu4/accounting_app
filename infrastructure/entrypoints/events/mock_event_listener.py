"""
Mock Event Listener - Enterprise Edition

Professional mock event listener for testing and development
with enterprise patterns and comprehensive event handling.
"""

from domain.enums.user_status_enum import UserStatusEnum


class MockEventListener:
    """
    Mock event listener for development and testing

    This listener simulates event processing without external dependencies
    and provides comprehensive logging for debugging purposes.
    """

    def __init__(self):
        """Initialize mock event listener"""
        self.events_received = []
        self.is_active = True

    def handle_task_completed(self, task_id: str, user_id: int) -> None:
        """
        Handle task completed event

        Args:
            task_id: ID of the completed task
            user_id: ID of the user who completed the task
        """
        event = {
            "event_type": "TaskCompleted",
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": "2025-01-19T14:30:00Z",
        }

        self.events_received.append(event)
        print(f"Mock Event: Task {task_id} completed by user {user_id}")

    def handle_user_status_change(
        self, user_id: int, old_status: UserStatusEnum, new_status: UserStatusEnum
    ) -> None:
        """
        Handle user status change event

        Args:
            user_id: ID of the user
            old_status: Previous user status
            new_status: New user status
        """
        event = {
            "event_type": "UserStatusChanged",
            "user_id": user_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "timestamp": "2025-01-19T14:30:00Z",
        }

        self.events_received.append(event)
        print(
            f"Mock Event: User {user_id} status changed from {old_status.value} to {new_status.value}"
        )

    def get_events_count(self) -> int:
        """Get total number of events received"""
        return len(self.events_received)

    def clear_events(self) -> None:
        """Clear all received events"""
        self.events_received.clear()

    def get_events_by_type(self, event_type: str) -> list:
        """Get events filtered by type"""
        return [
            event for event in self.events_received if event["event_type"] == event_type
        ]
