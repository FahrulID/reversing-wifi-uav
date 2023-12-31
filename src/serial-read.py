import serial
ser = serial.Serial('COM7', 
    baudrate=115200, 
    parity=serial.PARITY_NONE, 
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS, 
    timeout=1
)

data = []
try:
    while True:
        try:
            while len(data) < 20:
                binary = ser.read()
                hex = binary.hex()
                data.append(hex)
        except KeyboardInterrupt:
            ser.close()
            break

        print(len(data))
        print(data)
        data = []

except KeyboardInterrupt:
    ser.close()

print("bye")