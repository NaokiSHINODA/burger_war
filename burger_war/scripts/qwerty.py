#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This is rumdom run node.
subscribe No topcs.
Publish 'cmd_vel' topic. 
mainly use for simple sample program

by Takuya Yamaguhi.
'''
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from sensor_msgs.msg import Imu
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
import sendIdToJudge
from tf.transformations import euler_from_quaternion
import subprocess


class Qwerty():
    def __init__(self, bot_name="NoName",
                 use_lidar=False, use_camera=False, use_imu=False,
                 use_odom=False, use_joint_states=False, use_rviz=False):
        self.name = bot_name

        # velocity publisher
        self.vel_pub = rospy.Publisher('cmd_vel', Twist,queue_size=1)

        # lidar scan subscriber
        if use_lidar:
            self.scan = LaserScan()
            self.lidar_sub = rospy.Subscriber('scan', LaserScan, self.lidarCallback)

        # camera subscribver
        # please uncoment out if you use camera
        if use_camera:
            # for convert image topic to opencv obj
            self.img = None
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber('image_raw', Image, self.imageCallback)

        # imu subscriber
        if use_imu:
            self.imu_sub = rospy.Subscriber('imu', Imu, self.imuCallback)

        # odom subscriber
        if use_odom:
            self.odom_sub = rospy.Subscriber('odom', Odometry, self.odomCallback)

        # joint_states subscriber
        if use_joint_states:
            self.odom_sub = rospy.Subscriber('joint_states', JointState, self.jointstateCallback)

        if use_rviz:
            # for convert image topic to opencv obj
            self.rviz_img = None
            self.rviz_bridge = CvBridge()
            self.rviz_image_sub = rospy.Subscriber('image_raw', Image, self.rvizimageCallback)
    # lidar scan topic call back sample
    # update lidar scan state
    def lidarCallback(self, data):
        self.scan = data
        rospy.loginfo(self.scan)

    # camera image call back sample
    # comvert image topic to opencv object and show
    def imageCallback(self, data):
        try:
            self.img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)
        '''
        self.S = self.area(self.img)
        if self.S != None:
            print(self.S)
        '''
        cv2.imshow("Image window", self.img)
        cv2.waitKey(1)

    # imu call back sample
    # update imu state
    def imuCallback(self, data):
        self.imu = data
        rospy.loginfo(self.imu)

    # odom call back sample
    # update odometry state
    def odomCallback(self, data):
        self.pose_x = data.pose.pose.position.x
        self.pose_y = data.pose.pose.position.y
        rospy.loginfo("odom pose_x: {}".format(self.pose_x))
        rospy.loginfo("odom pose_y: {}".format(self.pose_y))

    # jointstate call back sample
    # update joint state
    def jointstateCallback(self, data):
        self.wheel_rot_r = data.position[0]
        self.wheel_rot_l = data.position[1]
        rospy.loginfo("joint_state R: {}".format(self.wheel_rot_r))
        rospy.loginfo("joint_state L: {}".format(self.wheel_rot_l))

    def rvizimageCallback(self, data):
        try:
            self.rviz_img = self.rviz_bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)

        cv2.imshow("rviz Image window", self.rviz_img)
        cv2.waitKey(1)

    def area(self,img):
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        hsvLower = np.array([0, 128, 0])
        hsvUpper = np.array([30, 255, 255])
        mask1 = cv2.inRange(hsv, hsvLower, hsvUpper)

        hsvLower = np.array([150, 128, 0])
        hsvUpper = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv, hsvLower, hsvUpper)
        
        mask = mask1 + mask2

        masked_hsv = cv2.bitwise_and(img, img, mask=mask)
        gray = cv2.cvtColor(masked_hsv,cv2.COLOR_BGR2GRAY)

        ret,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)
        image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        return cv2.contourArea(contours[0])

    def calcTwist(self):
        x = 0
        th = 0
        twist = Twist()
        twist.linear.x = x; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th
        return twist

    def strategy(self):
        r = rospy.Rate(1) # change speed 1fps

        target_speed = 0
        target_turn = 0
        control_speed = 0
        control_turn = 0

        while not rospy.is_shutdown():
            twist = self.calcTwist()
            print(twist)
            self.vel_pub.publish(twist)
            r.sleep()


if __name__ == '__main__':
    rospy.init_node('all_sensor_sample')
    bot = Qwerty(bot_name='qwerty', use_lidar=False, use_camera=True,
                 use_imu=False, use_odom=False, use_joint_states=False, use_rviz=False)
    bot.strategy()

