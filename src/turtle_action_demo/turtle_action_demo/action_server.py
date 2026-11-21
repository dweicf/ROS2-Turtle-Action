
import math
import time


import rclpy
from rclpy.node import Node

from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtle_action_interfaces.action import MoveToPosition



class TurtleActionServer(Node):

    def __init__(self):
        super().__init__('turtle_action_server')

        # 创建回调组
        self.callback_group = ReentrantCallbackGroup()

        # 声明参数
        self.declare_parameter('linear_speed', 1.5)
        self.declare_parameter('angular_speed', 2.0)
        self.declare_parameter('goal_tolerance', 0.15)

        # 获取参数
        self.linear_speed = self.get_parameter(
            'linear_speed').value

        self.angular_speed = self.get_parameter(
            'angular_speed').value

        self.goal_tolerance = self.get_parameter(
            'goal_tolerance').value

        # 创建速度发布者
        self.velocity_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 创建位置订阅者
        self.pose = None

        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group
        )

        # 创建 Action Server
        self.action_server = ActionServer(
            self,
            MoveToPosition,
            'move_to_position',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Turtle Action Server started!')


    def pose_callback(self, msg):
        self.pose = msg


    def goal_callback(self, goal_request):

        # 判断目标坐标是否在小海龟地图范围内
        if not (0.5 <= goal_request.target_x <= 10.5):
            return GoalResponse.REJECT

        if not (0.5 <= goal_request.target_y <= 10.5):
            return GoalResponse.REJECT

        self.get_logger().info(
            f'Received goal: '
            f'x={goal_request.target_x}, '
            f'y={goal_request.target_y}'
        )

        return GoalResponse.ACCEPT


    def cancel_callback(self, goal_handle):

        self.get_logger().info('Cancel request received!')

        return CancelResponse.ACCEPT



    def execute_callback(self, goal_handle):

        self.get_logger().info('Executing goal...')

        result = MoveToPosition.Result()
        feedback = MoveToPosition.Feedback()

        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y

        while rclpy.ok():

            # 检查是否收到取消请求
            if goal_handle.is_cancel_requested:

                self.stop_turtle()

                goal_handle.canceled()

                result.success = False
                result.message = 'Goal canceled'

                self.get_logger().info('Goal canceled')

                return result

            # 等待第一次位置数据
            if self.pose is None:
                time.sleep(0.1)
                continue

            # 获取当前位置
            current_x = self.pose.x
            current_y = self.pose.y
            current_theta = self.pose.theta

            # 计算距离
            dx = target_x - current_x
            dy = target_y - current_y

            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 判断是否到达目标
            if distance <= self.goal_tolerance:

                self.stop_turtle()

                goal_handle.succeed()

                result.success = True
                result.message = 'Goal reached successfully'

                self.get_logger().info('Goal succeeded!')

                return result

            # 计算目标方向
            target_theta = math.atan2(dy, dx)

            # 计算角度误差
            angle_error = target_theta - current_theta

            # 将角度误差限制在 [-pi, pi]
            angle_error = math.atan2(
                math.sin(angle_error),
                math.cos(angle_error)
            )

            # 创建速度消息
            cmd = Twist()

            # 控制角速度
            cmd.angular.z = max(
                -self.angular_speed,
                min(self.angular_speed, 4.0 * angle_error)
            )

            # 角度误差较大时先旋转，不前进
            if abs(angle_error) < 0.5:
                cmd.linear.x = min(
                    self.linear_speed,
                    1.5 * distance
                )
            else:
                cmd.linear.x = 0.0

            # 发布速度
            self.velocity_publisher.publish(cmd)

            # 发布 Feedback
            feedback.current_x = current_x
            feedback.current_y = current_y
            feedback.distance_remaining = distance

            goal_handle.publish_feedback(feedback)

            # 控制循环周期
            time.sleep(0.1)

        # ROS 2 关闭时停止机器人
        self.stop_turtle()

        goal_handle.abort()

        result.success = False
        result.message = 'ROS 2 shutdown'

        return result

    
    def stop_turtle(self):

        cmd = Twist()

        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        self.velocity_publisher.publish(cmd)

def main(args=None):

    rclpy.init(args=args)

    node = TurtleActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_turtle()
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
