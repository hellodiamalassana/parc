import rospy

from .planner import AgribotPlanner
from .controller import AgribotController
from .perceiver import AgribotPerceiver


class AgribotAgent:
    def __init__(self, name_id, **kwargs) -> None:
        self._node_id = name_id

        debug = kwargs['debug'] if 'debug' in kwargs else False
        log_level = rospy.DEBUG if debug else rospy.INFO

        rospy.init_node(self._node_id, anonymous=False, log_level=log_level)
        rospy.loginfo(f'-- Node {self._node_id!r} initialized')

        self._percept = AgribotPerceiver()
        self._plan = AgribotPlanner(perception=self._percept)
        self._control = AgribotController(perception=self._percept)

        rospy.on_shutdown(self._on_shutdown)

    def _on_shutdown(self) -> None:
        self._control.stop()

    def run(self) -> None:
        """Continuously execute the agent to achieve the goal."""
        rospy.loginfo(f'-- Initializing {self._node_id!r} node...')

        try:
            while not rospy.is_shutdown():
                self.execute()
        except rospy.exceptions.ROSInterruptException:
            rospy.loginfo('-- Received interrupt signal')

        rospy.loginfo(f'-- Terminating {self._node_id!r} node.')

    def execute(self):
        """Execute the planned action using control mechanisms to achieve the goal."""
        if (action := self._plan.plan_action()) is not None:
            self._control.execute_action(action)
