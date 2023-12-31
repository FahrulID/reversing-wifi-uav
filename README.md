# Reverse Engineering Chinese WIFI UAV Drone
Author: Fahrul Ramadhan Putra

[![The Drone][drone-image]](https://github.com/FahrulID/reversing-wifi-uav)

So, I just got this Chinese drone, the LSRC-S1S. You can control it with a smartphone app, and it's one of those common designs you see all over. The app lets you do cool things like manual flying, checking out live camera feeds, and messing around with features like palm control and follow-me. That got me thinking, you know? Since it's can be controlled through an app, I should be able to control it automatically. So now I'm curious to dig into how the drone works.

## Reversing the app ( WIFI UAV )

After giving [Dex2Jar](https://github.com/pxb1988/dex2jar) a shot for reversing the APK, not much luck on that because i couldn't found nothing. Time to switch tactics, and that's where [WireShark](https://www.wireshark.org/) steps in. Let's dive into the network traffic and see if we can uncover what's going on.

## Sniffing with WireShark

A quick sniffing with [WireShark](https://www.wireshark.org/) reveals that the app is communicating with the drone over UDP. The drone takes a role as an AP which will be connected to with our phone.

[![UDP Packet from App to Drone][wireshark-app-to-drone]](https://github.com/FahrulID/reversing-wifi-uav)

After some tweaking with the app,turns out the UDP Packet corresponds to the control of the drone is sent to the drone on port `:8800`. As far as i could tweak, the packet contains the following:

- Some kind of sequence, highlighted in red
- The controller command consists of 20 bytes, highlighted in blue :
    - Starts with hex `0x66`
    - Followed by 4 bytes of data ( `0x80 0x80 0x80 0x80` ) from 3rd byte to 6th byte, which means the RC value of the controller ( Roll, Pitch, Throttle, Yaw ). This value ranging from `0x00` to `0xFF`, which means the RC value is ranging from `0` to `255`.
    - 7th byte is for command, which are: 
        - `0x01` for takeoff
        - `0x02` for emergency stop
        - `0x03` for landing
        - `0x04` for calibrating gyroscope
    - 8th byte is for headless mode, which are:
        - `0x02` for headless mode off
        - `0x03` for headless mode on
    - 19th byte is for checksum, which is the xor of all bytes from 3rd byte to 8th byte ( as for my observation )
    - 20th byte is the end of the packet, which is `0x99`

[![UDP Packet from App to StreamOn][wireshark-app-to-drone-streamon]](https://github.com/FahrulID/reversing-wifi-uav)

The app also sends a packet to the drone to start the video stream. The packet is always the same, and it's just 4 bytes long `0xef 0x00 0x04 0x00`. This will open a port on the drone, and the video stream will be sent to that port, that is port `:1234`.

[![UDP Packet from Drone to App Video Stream][wireshark-drone-to-app-video-stream]](https://github.com/FahrulID/reversing-wifi-uav)

Now that the stream is on. The drone will sends its video stream to the app from port `:1234`. The video stream is likely to be encoded in H264, but to this day I couldn't decode it. The packet is sent in parts of maximum 1080 bytes including with the header. The header i assume consists of batch number ( highlighted in blue ), part number ( highlighted in red ), and maybe timestamp and etc. I've searched the internet for this kind of packet, but i couldn't find anything. If you have any idea, please let me know. You can get the packet capture file [here](others/capture.pcapng).

### Controlling the drone

With the mistery of UDP Packets unraveled, now we can control the drone with our own program. I've made a simple python script to control the drone. You can get the script [here](src/teleop.py) and run it with `python teleop.py`. But first you have to be connected to the Drone's AP.

## Physical Reverse Engineering

Here is components of the drone that i've found after teardown.

![IR Sensor][ir-sensor]
![Flight Control Unit Front Side][fcu-front-side]
![Flight Control Unit Back Side][fcu-back-side]
![Arm With Brushless Motor][arm]
![Camera Wifi Module][camera-wifi-module]
![Camera Wifi Module Front Side][camera-wifi-module-front-side]
![Camera Wifi Module Back Side][camera-wifi-module-back-side]

### Reversing the Camera Wifi Module

![Camera Wifi Module USB-TTL][camera-wifi-module-usb-ttl]

The module seems to communicate with the flight control unit (FCU) through UART. The UART pins are labeled on the board. Using Multi/AVO Meter, turns out the module itself has it owns Step Down Converter to 3.3V. So, we can safely connect the module directly to our computer through USB-TTL. After some mindless checking on the buffer, the module is using `115200` baudrate, `8` data bits, `1` stop bit, and `no` parity. The module is sending the same data as the app does : 

![Serial from Camera Wifi Module][serial-from-camera-wifi-module]

- The Data, with length of 20 bytes :
    - Starts with hex `0x66`
    - Followed by 4 bytes of data ( `0x80 0x80 0x80 0x80` ) from 3rd byte to 6th byte, which means the RC value of the controller ( Roll, Pitch, Throttle, Yaw ). This value ranging from `0x00` to `0xFF`, which means the RC value is ranging from `0` to `255`.
    - 7th byte is for command, which are: 
        - `0x01` for takeoff
        - `0x02` for emergency stop
        - `0x03` for landing
        - `0x04` for calibrating gyroscope
    - 8th byte is for headless mode, which are:
        - `0x02` for headless mode off
        - `0x03` for headless mode on
    - 19th byte is for checksum, which is the xor of all bytes from 3rd byte to 8th byte ( as for my observation )
    - 20th byte is the end of the packet, which is `0x99`

## Modding Time

Now that i can send my own command to the FCU, I could make my own module to control the drone, with ESP32 as the Microcontroller. Also I can add more sensors to help the drone to fly autonomously (e.g IMU, Baro, GPS, Compass, etc). Also, remember that I can't stream my own video? Now I can, with my own Camera.

## Future Work

Find out what the other bytes in the packet are for.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[drone-image]: images/drone.jpg
[wireshark-app-to-drone]: images/wireshark-app-to-drone.png
[wireshark-app-to-drone-streamon]: images/wireshark-app-to-drone-streamon.png
[wireshark-drone-to-app-video-stream]: images/wireshark-drone-to-app-video-stream.png
[arm]: images/arm.jpg
[camera-wifi-module-back-side]: images/camera-wifi-module-back-side.jpg
[camera-wifi-module-front-side]: images/camera-wifi-module-front-side.jpg
[camera-wifi-module]: images/camera-wifi-module.jpg
[camera-wifi-module-usb-ttl]: images/camera-wifi-module-usb-ttl.jpg
[fcu-back-side]: images/fcu_back_side.jpg
[fcu-front-side]: images/fcu_front_side.jpg
[ir-sensor]: images/ir_sensor.jpg
[serial-from-camera-wifi-module]: images/serial-from-camera-wifi-module.png