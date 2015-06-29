#!/usr/bin/env python
import rospy
from zmq_object_exchanger.zmq_object_exchanger import zmqObjectExchanger
import importlib

class rosZmqBridge():

    def __init__(self, robot_name, addr, port):
    
        self.forwards = {}
        # name, ip address and port of "this" robot
        self.zmq = zmqObjectExchanger(robot_name, addr, port)
     
    def callback(self, msg, topic):
    
        (sub, zmq) = self.forwards[topic]
        zmq.send_msg(topic, msg)
        
    # topics which we want to publish through zmq
    def forward(self, rtype, topic):
    
        tmp = rtype.split("/")
        mod = importlib.import_module(tmp[0] + ".msg")
        msgtype = getattr(mod, tmp[1])
        sub = rospy.Subscriber(topic, msgtype, self.callback, callback_args = topic)
        
        self.forwards[topic] = (sub, zmq)
        
    def listen_to(self, rtype, topic, robot_name, addr, port):
    
        self.zmq.add_remote(robot_name, addr, port)
        # TODO register callback (add support to zmqObjectExchanger)

def main():
    
    rospy.init_node('zmq_bridge', anonymous=True)
    
    bridge = rosZmqBridge("robotxyz", "127.0.0.1", 1234)
    
    bridge.forward("geometry_msgs/PoseStamped", "pose")
    
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
