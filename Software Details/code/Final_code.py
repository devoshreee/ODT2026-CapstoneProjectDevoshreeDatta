'''vruddhi'''
#import module
from machine import Pin, PWM, time_pulse_us
import bluetooth
import time
import neopixel


'''vruddhi (debugged and rewritten by Devoshree)'''
#initialise all the pins

#front driver
front_left_1  = Pin(13, Pin.OUT)   # IN1  Front-Left  forward
front_left_2  = Pin(12, Pin.OUT)   # IN2  Front-Left  backward
front_right_1  = Pin(14, Pin.OUT)   # IN3  Front-Right forward
front_right_2  = Pin(27, Pin.OUT)   # IN4  Front-Right backward
front_ena = PWM(Pin(23),freq=1000)   # speed of front left motor
front_enb = PWM(Pin(22),freq=1000)   # speed of front right motor

#back driver
back_left_1  = Pin(26, Pin.OUT)   # IN1  Rear-Left  forward
back_left_2  = Pin(25, Pin.OUT)   # IN2  Rear-Left  backward
back_right_1  = Pin(33, Pin.OUT)   # IN3  Rear-Right forward
back_right_2  = Pin(32,  Pin.OUT)   # IN4  Rear-Right backward
back_ena = PWM(Pin(21),freq=1000)   # speed of back left motor
back_enb = PWM(Pin(19),freq=1000)   # speed of back right motor

#servo motor
servo = PWM(Pin(5), freq=50)

#neopixel strip
neo = neopixel.NeoPixel(Pin(18),8)

#ultrasonic sensor
trig = Pin(15, Pin.OUT)
echo = Pin(4,  Pin.IN)


'''Devoshree'''
#define functions for going front back left right (one step at a time)

#turning on all the en and defining the speed of left and right wheel speed
def set_speed(sright,sleft):
    front_ena.duty(sright)
    back_ena.duty(sright)
    front_enb.duty(sleft)
    back_enb.duty(sleft)

#turning off all the en
def stop():
    front_left_1.value(0)
    front_left_2.value(0)
    front_right_1.value(0)
    front_right_2.value(0)
    back_left_1.value(0)
    back_left_2.value(0)
    back_right_1.value(0)
    back_right_2.value(0)
    set_speed(0,0)

#making the left wheels move clockwise and the right wheels move anticlockwise
def forward():
    front_left_1.value(1)
    front_left_2.value(0)
    front_right_1.value(1)
    front_right_2.value(0)
    back_left_1.value(1)
    back_left_2.value(0)
    back_right_1.value(1)
    back_right_2.value(0)
    set_speed(1023,1023)

#making the left wheels move anticlockwise and the right wheels move clockwise
def backward():
    front_left_1.value(0)
    front_left_2.value(1)
    front_right_1.value(0)
    front_right_2.value(1)
    back_left_1.value(0)
    back_left_2.value(1)
    back_right_1.value(0)
    back_right_2.value(1)
    set_speed(1023,1023)

#making the left wheels move slower (lower RPM) and backwards and the right move faster (higher RPM) and forwards
def left():
    front_left_1.value(1)
    front_left_2.value(0)
    front_right_1.value(0)
    front_right_2.value(1)
    back_left_1.value(1)
    back_left_2.value(0)
    back_right_1.value(0)
    back_right_2.value(1)
    set_speed(1023,400)
    time.sleep(0.2)

#making the left wheels move faster (higher RPM) and forward and the right move slower (lower RPM) and backwards
def right():
    front_left_1.value(0)
    front_left_2.value(1)
    front_right_1.value(1)
    front_right_2.value(0)
    back_left_1.value(0)
    back_left_2.value(1)
    back_right_1.value(1)
    back_right_2.value(0)
    set_speed(400,1023)
    time.sleep(0.2)
    

'''Devoshree'''
#neopixels colours in deferent modes
 
#for turning on all the leds in neopixel when obsticle is detected
def neo_obstacle():
    for i in range(8):
        neo[i] = (225, 0, 0)
    neo.write()
 
#for turning off all the leds in neopixel when obsticle is gone
def neo_clear():
    for i in range(8):
        neo[i] = (0, 0, 0)
    neo.write()
 
#when car is moving
def neo_running():
    for i in range(8):
        neo[i] = (0, 60, 0)
    neo.write()
 
#the ultrasound sensor is rotating to scan for obstacles
def neo_scanning():
    for i in range(8):
        neo[i] = (80, 40, 0)
    neo.write()
    

'''Devoshree'''
#define function for the obstacle avoidance tech with the stepper and ultrasonic sensor

#defining a function to move the servo motor
def set_servo(angle):
    #this is supposed to convert degrees into duty cicle needed 
    duty = int(25 + (angle / 180) * (110 - 35))
    servo.duty(duty)

#defining the distance at which the onstacle is detected
def read_distance():
    #sending a 10 microsecond pulse
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    
    #for handaling the errors (echo never going up) in obstacle detection by the sensor without stopping the whole code
    try:
        duration = time_pulse_us(echo, 1, 30000)   # 30 millisecond timeout
    except OSError:
        print("No object detected (Timeout)")   #for checking the distance and is its detecting properly
        return 250   #assigning and returning a numarical value (if the sensor cant detect an obstacle) when function is called
    
    #normal condition without error detection
    if duration < 0:
        print("No object detected (Timeout)")   #for checking the distance and is its detecting properly
        return 250   # assigning and returning a numarical value if the sensor cant detect an obstacle
    distance = duration/58
    print("Distance:", distance, "cm")    #for checking the distance
    return distance    # assigning and returning the distnace (at which the obstacle is at) when function is called

#checking right side if obstacle is detected
def look_right():
    neo_scanning()
    set_servo(10)  #scanning 10° degree (on right side)
    time.sleep(0.4)
    d = read_distance()  #reading the distance and storing the distance scanned 
    set_servo(90)  #returning to the center
    time.sleep(0.2)
    return d   #assigning and returning the value of d when function is called

#checking left side if obstacle is detected
def look_left():
    neo_scanning()
    set_servo(170)  #scanning 170 degree to the left
    time.sleep(0.4)
    d = read_distance()  #reading the distance and storing the distance scanned 
    set_servo(90)  #returning to the center
    time.sleep(0.2)
    return d   #assigning and returning the value of d when function is called

#moving the car where there is no obstacle
def avoid_obstacle():
    """
    steps being executed:
      1. Stopping and the neopixel glows red
      2. goes backwards slightly
      3. Scanning left and right
      4. moves towards the side where there is no obstacle
      5. neopixel stops glowing red
    """
    neo_obstacle()
    stop()
    time.sleep(0.2)
 
    backward()
    time.sleep(0.3)
    stop()
    time.sleep(0.2)
 
    distance_right = look_right()   #assigning the value of d(the distance at which the onstacle is) to the variable
    time.sleep(0.3)
    distance_left  = look_left()    #assigning the value of d(the distance at which the onstacle is) to the variable
    time.sleep(0.3)
 
    print("Right:", distance_right, "cm\nLeft:", distance_left, "cm")   #to check the distance 
 
    #this is supposed to compare the obstacle distance on both sides and move accordingly 
    if distance_right >= distance_left:
        right()
        time.sleep(2)
    else:
        left()
        time.sleep(2)
 
    stop()
    neo_clear()
    

'''Devoshree'''
#for auto obstacle detection mode this valriable is there (when true it will ditect obstacle on its own and move forward, if false then it will have to be controlled through manual controls)
auto_mode = False


'''Nirzara (debugged by Devoshree)'''
#pre defined path

# wheel circumference = π × 6.5cm ≈ 20.42cm
# assuming ~3 rotations/second at full speed (1023)
# 1 meter = 100cm → 100/20.42 = 4.9 rotations → 4.9/3 ≈ 1.63 seconds
time_1m = 1.63

# 2 meters = 200cm → 200/20.42 = 9.79 rotations → 9.79/3 ≈ 3.27 seconds
time_2m = 3.27

# m = mumbai, p = panjim, d = delhi, t = tejpur
# path md  (straight, 2 meters)
def path_md():
    forward()
    time.sleep(time_2m)
    stop()

# path mp  (straight, 2 meters)
def path_mp():
    forward()
    time.sleep(time_1m)
    stop()

# path mt  (diagonal: m=right-front, t=left-back)
# layout: 1m forward → turn left → 1m forward → turn right → 1m forward
def path_mt():
    forward()
    time.sleep(time_1m)
    stop()
    left()
    forward()
    time.sleep(time_1m)
    stop()
    right()
    forward()
    time.sleep(time_1m)
    stop()

# path pd  (diagonal: b=left-front, c=right-back)
# layout: 1m forward → turn right → 1m forward → turn left → 1m forward
def path_pd():
    forward()
    time.sleep(time_1m)
    stop()
    right()
    forward()
    time.sleep(time_1m)
    stop()
    left()
    forward()
    time.sleep(time_1m)
    stop()
    

'''Vruddhi (technically copy pasted from nayan's file)'''
#bluetooth code
value = ""
name = "ESP32-NDtV" 
ble = bluetooth.BLE()

ble.active(False)
time.sleep(0.5)
ble.active(True)
ble.config(gap_name=name)

service_UUID = bluetooth.UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
char_UUID = bluetooth.UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")

char = (char_UUID, bluetooth.FLAG_WRITE)
service = (service_UUID, (char,),)
((char_handle,),) = ble.gatts_register_services((service,))


#define the bluetooth functions

def event_occured(event, data):

    if event == 1:
        print("Connected")
        
    elif event == 2:
        print("Disconnected")
        advertise(name)
        
    elif event == 3:
        conn_handle, value_handle = data
        if value_handle == char_handle:
        #reading the Value written on characteristics by Phone/client
            raw_msg = ble.gatts_read(char_handle).rstrip(b'\x00')
            msg = raw_msg.decode().strip()
            print("Received:", msg)
                
            global value
            value = msg
                

def advertise(device_name):
    
    name_bytes = device_name.encode()

    flags = bytearray([0x02, 0x01, 0x06])
    short_name = bytearray([len(name_bytes) + 1, 0x08]) + name_bytes
    full_name = bytearray([len(name_bytes) + 1, 0x09]) + name_bytes
    adv_data = flags + short_name + full_name

    ble.gap_advertise(50, adv_data=adv_data)
    print("Awating Connection...Advertising as:", device_name)

advertise(name)

ble.irq(event_occured)


'''Devoshree'''
#main code inside while loop
while True:
    #for manual control mode
    if auto_mode == False:
        if value == "F":
            forward()
        elif value == "B":
            backward()
        elif value == "L":
            left()
        elif value == "R":
            right()
        elif value == "S":
            stop()
            neo_clear()
            
        #for predefined paths   
        elif value == "M":
            path_md()
            neo_clear()
        elif value == "P":
            path_mp()
            neo_clear()
        elif value == "T":
            path_mt()
            neo_clear()
        elif value == "D":
            path_pd()
            neo_clear()
        
        #checks again if modes are switch during the loop
        if value in ("F", "B", "L", "R", "S", "M", "P", "T", "D"):
            value = ""  #resetting value
        elif value == "auto":
            auto_mode = True   #skipping the rest of the loop and moving to the next loop
        
        time.sleep(0.2)
    
    #for automatic onbstacle detection mode
    elif auto_mode == True:
        
        #checks for obstacle before moving forward
        dist = read_distance()
        if dist <= 5:  #if obstacle is 5cm away
            avoid_obstacle()
            #checks again if modes are switch during the loop
            if value in ("F", "B", "L", "R", "S", "M", "P", "T", "D"):
                stop()
                neo_clear()
                auto_mode = False   #skipping the rest of the loop anf moving to the next loop
            elif value == "auto":
                value = ""  #place holder
                pass
        else:
            neo_running()
            forward()
            #checks again if modes are switch during the loop
            if value in ("F", "B", "L", "R", "S", "M", "P", "T", "D"):
                stop()
                neo_clear()
                auto_mode = False   #skipping the rest of the loop anf moving to the next loop
            elif value == "auto":
                value = ""  #place holder
                pass
 
    time.sleep_ms(30)
