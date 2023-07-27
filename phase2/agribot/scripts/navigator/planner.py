import rospy

from perceptor import AgribotPerceptor
from utils.action import SteppedAction, Action

from utils.helpers import (
    ForgetfulMemory,
    BasicQueue
)


class AgribotPlanner:
    def __init__(self, perception: AgribotPerceptor) -> None:
        self._perception = perception
        self._last_actions_memory = ForgetfulMemory()
        self._next_actions_queue = BasicQueue()

    @property
    def _has_enqueued_actions(self):
        return not self._next_actions_queue.empty()

    def _resolve_enqueued_actions(self) -> Action | None:
        """Returns the next action in the queue, removing it from the structure."""
        if self._has_enqueued_actions:
            return self._next_actions_queue.dequeue()
        return None

    def enqueue_action(self, action: Action) -> None:
        """Add a new action to the action queue."""
        self._next_actions_queue.enqueue(action)

    def plan_action(self) -> Action | None:
        """Analyse the information from the perception mechanisms and determine the
        best course of action to be taken by the robot."""
        if self._has_enqueued_actions:
            return self._resolve_enqueued_actions()
        # TODO
        return None

