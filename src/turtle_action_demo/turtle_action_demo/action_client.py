import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus

from turtle_action_interfaces.action import MoveToPosition


class TurtleActionClient(Node):

    def __init__(self):
        super().__init__('turtle_action_client')

        # 声明 ROS 2 参数
        self.declare_parameter(
            'target_x_list', [2.0, 8.0, 8.0]
        )

        self.declare_parameter(
            'target_y_list', [2.0, 2.0, 8.0]
        )

        # 读取参数
        target_x_list = self.get_parameter(
            'target_x_list'
        ).value

        target_y_list = self.get_parameter(
            'target_y_list'
        ).value

        # 组合成目标点
        self.targets = list(zip(
            target_x_list,
            target_y_list
        ))

        self.target_index = 0

        # 创建 Action Client
        self.action_client = ActionClient(
            self,
            MoveToPosition,
            'move_to_position'
        )

        self.get_logger().info('Turtle Action Client started!')

    def send_goal(self):

        # 判断是否还有目标点
        if self.target_index >= len(self.targets):
            self.get_logger().info('All goals completed!')
            return

        # 获取当前目标点
        target_x, target_y = self.targets[self.target_index]

        # 创建 Goal
        goal = MoveToPosition.Goal()

        goal.target_x = target_x
        goal.target_y = target_y

        self.get_logger().info(
            f'Sending goal {self.target_index + 1}: '
            f'x={target_x}, y={target_y}'
        )

        # 等待服务端
        self.action_client.wait_for_server()

        # 异步发送目标
        self.send_goal_future = self.action_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        # 注册 Goal 响应回调
        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback

        current_x = feedback.current_x
        current_y = feedback.current_y
        distance = feedback.distance_remaining

        self.get_logger().info(
            f'Current position: '
            f'x={current_x:.2f}, '
            f'y={current_y:.2f}, '
            f'Distance remaining: {distance:.2f}'
        )

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected!')
            return

        self.get_logger().info('Goal accepted!')

        # 保存 Goal Handle
        self.goal_handle = goal_handle

        # 异步获取最终结果
        self.get_result_future = goal_handle.get_result_async()

        self.get_result_future.add_done_callback(
            self.get_result_callback
        )

        # 启动终端输入线程
        threading.Thread(
            target=self.cancel_input_thread,
            daemon=True
        ).start()

    def get_result_callback(self, future):

        response = future.result()

        result = response.result
        status = response.status

        if status == GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().info('Goal succeeded!')

            self.target_index += 1
            self.send_goal()

        elif status == GoalStatus.STATUS_CANCELED:

            self.get_logger().info('Goal canceled!')

        elif status == GoalStatus.STATUS_ABORTED:

            self.get_logger().error('Goal aborted!')

        else:

            self.get_logger().info(
                f'Unknown status: {status}'
            )
    def cancel_input_thread(self):

        input('输入 c 并按回车，取消当前任务：')

        self.get_logger().info(
            'Sending cancel request...'
        )

        self.cancel_future = self.goal_handle.cancel_goal_async()

        self.cancel_future.add_done_callback(
            self.cancel_response_callback
        )

    def cancel_response_callback(self, future):

        cancel_response = future.result()

        if len(cancel_response.goals_canceling) > 0:

            self.get_logger().info(
                'Cancel request accepted!'
            )

        else:

            self.get_logger().info(
                'Cancel request rejected!'
            )


def main(args=None):

    rclpy.init(args=args)

    node = TurtleActionClient()

    # 发送目标
    node.send_goal()

    # 持续处理回调
    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
