import time
import threading
from lib.drone import Drone
from pynput import keyboard
import os

if __name__ == "__main__":
    drone = Drone()

    # send initialization for 1 second
    init_end = time.time() + 1
    while time.time() < init_end:
        drone.initialize_image()
        time.sleep(0.1)

    def background():
        global drone
        while True:
            drone.build_message()
            drone.send_message()
            time.sleep(0.1)
        
    drone_thread = threading.Thread(target=background)
    drone_thread.start()

    MOVEMENT_KEY_PRESSED = set()
    MOVEMENT_KEYS = ['w', 's', 'a', 'd', 'i', 'm']
    MOVEMENT_VECTOR = [0, 0, 0] # x, y, z, x = forward, y = left, z = up
    PITCH = 127
    ROLL = 127
    THROTTLE = 127
    SPEED_MULTIPLIER = 48
    # 63 -> 127 -> 191

    def on_press(key): 
        try:
            MOVEMENT_VECTOR = [0, 0, 0]
            print('Key {0} pressed'.format(key.char))

            if key.char in MOVEMENT_KEYS:
                MOVEMENT_KEY_PRESSED.add(key.char)

            if 'w' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[0] += 1

            if 's' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[0] -= 1

            if 'a' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[1] -= 1
            
            if 'd' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[1] += 1

            if 'i' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[2] += 1
            
            if 'm' in MOVEMENT_KEY_PRESSED:
                MOVEMENT_VECTOR[2] -= 1

            PITCH = 127 + MOVEMENT_VECTOR[0] * SPEED_MULTIPLIER
            ROLL = 127 + MOVEMENT_VECTOR[1] * SPEED_MULTIPLIER
            THROTTLE = 127 + MOVEMENT_VECTOR[2] * SPEED_MULTIPLIER

            print(PITCH, ROLL, THROTTLE)

            drone.set_pitch(PITCH)
            drone.set_roll(ROLL)
            drone.set_throttle(THROTTLE)

            if key.char == 'q':
                drone.set_yaw(63)
            elif key.char == 'e':
                drone.set_yaw(191)
            elif key.char == 'r':
                drone.calibrate()
            elif key.char == 'f':
                drone.takeoff()
            elif key.char == 'v':
                drone.land()
            elif key.char == 'c':
                drone.stop()
            elif key.char == 'j':
                drone.reset_command()
        except AttributeError:
            print('Key {0} pressed'.format(key))

    running = True

    def on_release(key):
        global running
        try:
            if key == keyboard.Key.esc:
                print("ESC")
                running = False
                listener.stop()
                return False
            else:
                if key.char in MOVEMENT_KEYS:
                    MOVEMENT_KEY_PRESSED.remove(key.char)

                PITCH = 127 + MOVEMENT_VECTOR[0] * SPEED_MULTIPLIER
                ROLL = 127 + MOVEMENT_VECTOR[1] * SPEED_MULTIPLIER
                THROTTLE = 127 + MOVEMENT_VECTOR[2] * SPEED_MULTIPLIER

                print(PITCH, ROLL, THROTTLE)

                drone.set_pitch(PITCH)
                drone.set_roll(ROLL)
                drone.set_throttle(THROTTLE)
        except AttributeError:
            print('Key {0} released'.format(key))
    try:
        while running:
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                print("Ready To Teleop")
                listener.join()
    except KeyboardInterrupt:
        print('interrupted!')
        drone.stop()
        drone_thread.join() 
        exit()
    finally:
        drone.stop()
        drone_thread.join()
        exit()
    