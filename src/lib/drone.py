import socket
import time

class Drone:
    IP = ""
    PORT = 0

    COMMAND_TAKEOFF = 0x01
    COMMAND_STOP = 0x02
    COMMAND_LAND = 0x03
    COMMAND_CALIBRATE = 0x04

    COMMAND_NON_HEADLESS = 0x02
    COMMAND_HEADLESS = 0x03

    TRANSMITTER = None
    RECEIVER = None
    RECEIVER_CLOSED = False

    MESSAGE_HEADER = None
    MESSAGE = None
    IMAGE_BUFFER = None

    COUNTER_1_1 = 0
    COUNTER_1_2 = 0

    COUNTER_2_1 = 1
    COUNTER_2_2 = 0

    COUNTER_3_1 = 2
    COUNTER_3_2 = 0

    YAW = 128
    THROTTLE = 128
    PITCH = 128
    ROLL = 128
    COMMAND = 0
    HEADLESS = 2

    def __init__(self, ip="192.168.169.1", port=8800) -> None:
        self.IP = ip
        self.PORT = port
        self.TRANSMITTER = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.RECEIVER = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.MESSAGE_HEADER = bytearray([0xef, 0x02, 0x7c, 0x00, 0x02, 0x02, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00])
        self.COUNTER_1_SUFFIX = bytearray([0x00, 0x00, 0x14, 0x00, 0x66, 0x14])
        self.CONTROL_SUFFIX = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.CHECKSUM_SUFFIX = bytearray([0x99, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x4b, 0x14, 0x2d, 0x00, 0x00 ])
        self.COUNTER_2_SUFFIX = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff])
        self.COUNTER_3_SUFFIX = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00])
        pass

    def counter(self) -> None:
        if self.COUNTER_1_1 + 1 >= 256:
            self.COUNTER_1_1 = 0
            self.COUNTER_1_2 += 1
        else :
            self.COUNTER_1_1 += 1
        
        if self.COUNTER_2_1 + 1 >= 256:
            self.COUNTER_2_1 = 0
            self.COUNTER_2_2 += 1
        else :
            self.COUNTER_2_1 += 1

        if self.COUNTER_3_1 + 1 >= 256:
            self.COUNTER_3_1 = 0
            self.COUNTER_3_2 += 1
        pass

    def build_message(self) -> None:
        counter_1 = bytearray([(self.COUNTER_1_1), (self.COUNTER_1_2)])
        counter_2 = bytearray([(self.COUNTER_2_1), (self.COUNTER_2_2)])
        counter_3 = bytearray([(self.COUNTER_3_1), (self.COUNTER_3_2)])
        control = bytearray([(self.ROLL), (self.PITCH), (self.THROTTLE), (self.YAW), (self.COMMAND), (self.HEADLESS)])
        checksum = bytearray([(self.ROLL ^ self.PITCH ^ self.THROTTLE ^ self.YAW ^ self.COMMAND ^ self.HEADLESS)])

        self.MESSAGE = self.MESSAGE_HEADER + counter_1 + self.COUNTER_1_SUFFIX + control + self.CONTROL_SUFFIX + checksum + self.CHECKSUM_SUFFIX + counter_2 + self.COUNTER_2_SUFFIX + counter_3 + self.COUNTER_3_SUFFIX

        self.counter()

    def send_message(self) -> None:
        self.TRANSMITTER.sendto(self.MESSAGE, (self.IP, self.PORT))
        pass

    def initialize_image(self) -> None:
        self.RECEIVER.sendto(bytearray([0xef, 0x00, 0x04, 0x00]), ("192.168.169.1", 8800))
        pass

    def image_listener(self) -> None:
        self.RECEIVER.sendto(bytearray([0xef, 0x00, 0x04, 0x00]), ("192.168.169.1", 1234))
        self.RECEIVER.connect(("192.168.169.1", 1234))
        while self.RECEIVER_CLOSED is not True:
            data = self.RECEIVER.recv(1080)
            self.IMAGE_BUFFER = data
            time.sleep(0.1)

    def stop_listen(self) -> None:
        self.RECEIVER.close()
        self.RECEIVER_CLOSED = True
        self.IMAGE_BUFFER = [0, 0]

    def reset_command(self) -> None:
        self.COMMAND = 0
        self.set_pitch(127)
        self.set_roll(127)
        self.set_throttle(127)
        self.set_yaw(127)
        pass

    def takeoff(self) -> None:
        self.COMMAND = self.COMMAND_TAKEOFF
        pass

    def stop(self) -> None:
        self.COMMAND = self.COMMAND_STOP
        pass

    def land(self) -> None:
        self.COMMAND = self.COMMAND_LAND
        pass

    def calibrate(self) -> None:
        self.COMMAND = self.COMMAND_CALIBRATE
        pass

    def set_roll(self, value) -> None:
        self.ROLL = value
        pass

    def set_pitch(self, value) -> None:
        self.PITCH = value
        pass

    def set_throttle(self, value) -> None:
        self.THROTTLE = value
        pass

    def set_yaw(self, value) -> None:
        self.YAW = value
        pass