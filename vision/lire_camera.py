import sys

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

from lecteur import lire


class LecteurTest(Node):
    def __init__(self, topic):
        super().__init__("lecteur_test")
        self.pont = CvBridge()
        self.create_subscription(Image, topic, self.image, 1)

    def image(self, msg):
        img = self.pont.imgmsg_to_cv2(msg, "bgr8")
        codes = sorted(f"{e['type'][0].upper()}|{e['code']}" for e in lire(img))
        self.get_logger().info(f"{len(codes)} etiquettes : {codes}")


rclpy.init()
rclpy.spin(LecteurTest(sys.argv[1] if len(sys.argv) > 1 else "/cam_g_1/image_raw"))