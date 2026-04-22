#import module
from machine import Pin, PWM, time_pulse_us
import bluetooth
import time
import neopixel


#initialise all the pins

'''check'''
#front driver
front_left_1  = Pin(13, Pin.OUT)   # IN1  Front-Left  forward
front_left_2  = Pin(12, Pin.OUT)   # IN2  Front-Left  backward
front_right_1  = Pin(14, Pin.OUT)   # IN3  Front-Right forward
front_right_2  = Pin(27, Pin.OUT)   # IN4  Front-Right backward
front_ena = PWM(Pin(23),freq=1000)   # speed of front left motor
front_enb = PWM(Pin(22),freq=1000)   # speed of front right motor

'''check'''
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


#define functions for going front back left right (one step at a time)

'''check'''
#turning on all the en
def set_speed(sleft,sright):
    front_ena.duty(sleft)
    back_ena.duty(sleft)
    front_enb.duty(sright)
    back_enb.duty(sright)

'''check'''
#turning off all the en
def stop():
    front_left_1.off()
    front_left_2.off()
    front_right_1.off()
    front_right_2.off()
    back_left_1.off()
    back_left_2.off()
    back_right_1.off()
    back_right_2.off()
    set_speed(0,0)

'''check'''
#making the left wheels move clockwise and the right wheels move anticlockwise
def forward():
    front_left_1.on()
    front_left_2.off()
    front_right_1.on()
    front_right_2.off()
    back_left_1.on()
    back_left_2.off()
    back_right_1.on()
    back_right_2.off()
    set_speed(1023,1023)

'''check'''
#making the left wheels move anticlockwise and the right wheels move clockwise
def backward():
    front_left_1.off()
    front_left_2.on()
    front_right_1.off()
    front_right_2.on()
    back_left_1.off()
    back_left_2.on()
    back_right_1.off()
    back_right_2.on()
    set_speed(1000,1000)

'''check'''
#making the left wheels slower with a lower RPM and the right faster with a higher RPM
def left():
    front_left_1.on()
    front_left_2.off()
    front_right_1.on()
    front_right_2.off()
    back_left_1.on()
    back_left_2.off()
    back_right_1.on()
    back_right_2.off()
    set_speed(400,1000)
    time.sleep(0.4)
    stop() #should i make it stop after turn or keep goinf with forward() function

'''check'''
#making the left wheels faster with a higher RPM and the right slower with a lower RPM
def right():
    front_left_1.on()
    front_left_2.off()
    front_right_1.on()
    front_right_2.off()
    back_left_1.on()
    back_left_2.off()
    back_right_1.on()
    back_right_2.off()
    set_speed(1000,400)
    time.sleep(0.4)
    stop() #should i make it stop after turn or keep goinf with forward() function
    

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
 
#when car is moving forward
def neo_forward():
    for i in range(8):
        neo[i] = (0, 60, 0)
    neo.write()
 
#the ultrasound sensor is rotating to scan for obstacles
def neo_scanning():
    for i in range(8):
        neo[i] = (80, 40, 0)
    neo.write()
    
    
#define function for the obstacle avoidance tech with the stepper and ultrasonic sensor

'''check'''
#defining a function to move the servo motor
def set_servo(angle):
    #this is supposed to convert degrees into duty cicle needed (still have to check its accuraccy)
    duty = int(25 + (angle / 180) * (110 - 35))
    servo.duty(duty)

'''check'''
#defining the distance at which the onstacle is detected
def read_distance():
    #sending a 10 microsecond pulse
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    duration = time_pulse_us(echo, 1, 30000)   # 30 millisecond timeout
    if duration < 0:
        print("No object detected (Timeout)")   #for checking the distance and is its detecting properly
    else:
        distance = duration/58
        print("Distance:", distance, "cm")    #for checking the distance

'''check'''
#checking right side if obstacle is detected
def look_right():
    neo_scanning()
    set_servo(10)  #scanning 10° degree (on right side)
    time.sleep(0.4)
    d = read_distance()  #reading the distance storing the distance scanned 
    set_servo(90)  #returning to the center
    time.sleep(0.2)
    return d   

'''check'''
#checking left side if obstacle is detected
def look_left():
    neo_scanning()
    set_servo(170)  #scanning 170 degree to the left
    time.sleep(0.4)
    d = read_distance()  #reading the distance storing the distance scanned 
    set_servo(90)  #returning to the center
    time.sleep(0.2)

'''check'''
#moving the car where there is no obstacle
def avoid_obstacle():
    """
    this is the steps thats happening:
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
    time.sleep(0.4)
    stop()
    time.sleep(0.3)
 
    distance_right = look_right()
    time.sleep(0.3)
    distance_left  = look_left()
    time.sleep(0.3)
 
    print("Right:", distance_right, "cm\nLeft:", distance_left, "cm")
 
    #this is supposed to compare the obstacle distance on both sides and move accordingly 
    if distance_right >= distance_left:
        right()
    else:
        left()
 
    move_stop()
    neo_clear()
    
#for auto obstacle detection mode this valriable is there (when true it will ditect obstacle on its own and move forward, if false then it will have to be controlled through manual controls)
auto_mode = True

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
            
            '''buttons in the app which control the cars movements'''
            if msg == "auto": #automatic obstacle detection mode
                auto_mode = True
            elif msg in ("F", "B", "L", "R", "S"): #manual control mode (forward, backward, left, right, stop)
                auto_mode = False
                

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


'''check'''
#main code inside while loop
while True:
    #for manual control mode
    while auto_mode == False:
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
        
        #checks again if modes are switch during the loop
        if value in ("F", "B", "L", "R", "S"):
            auto_mode = False       
        elif value == "auto":
            auto_mode = True
            value = ""  #resetting value 
            continue   #skipping the rest of the loop anf moving to the next loop
        
        time.sleep(0.2)
    
    #for automatic onbstacle detection mode
    while auto_mode == True:
        
        #checks for obstacle before moving forward
        dist = read_distance()
        if dist <= 200:
            avoid_obstacle()
        else:
            neo_forward()
            forward()
     
        #checks again if modes are switch during the loop
        if value in ("F", "B", "L", "R", "S"):
            auto_mode = False
            continue   #skipping the rest of the loop anf moving to the next loop
        elif value == "auto":
            auto_mode  = True
            value = ""   #resetting value 
 
    time.sleep_ms(30)

