#!/usr/bin/env python3.7
from subprocess import call
call("sudo pigpiod", shell=True)
import RPi.GPIO as GPIO
import pigpio
import time
import socket
import IMU
#import serial
import threading
import os

#port =serial.Serial(
      #"/dev/ttyUSB0",
      #baudrate=9600,
      #parity=serial.PARITY_NONE,
      #stopbits=serial.STOPBITS_ONE,
      #bytesize=serial.EIGHTBITS)


HOST = '192.168.2.104'
PORT = 8005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

IMU.detectIMU()
IMU.initIMU()

pi = pigpio.pi()
GPIO.setmode(GPIO.BOARD)
SERVO_GPIO = 8
ESC_GPIO = 7
LEFT_RIGHT_GPIO = 10
UP_DOWN_GPIO = 9

ESC_PWM_MIN = 1100 #1100
ESC_PWM_MID = 1367.0000          # 1357.0
ESC_PWM_MAX = 1850 #1850

print("ESC Calibration... Start")
#pi.set_servo_pulsewidth(ESC_GPIO, ESC_PWM_MIN)
#time.sleep(0.3)
#pi.set_servo_pulsewidth(ESC_GPIO, ESC_PWM_MAX)
#time.sleep(0.3)
#pi.set_servo_pulsewidth(ESC_GPIO, ESC_PWM_MID)
#time.sleep(0.5)
print("ESC Calibration Complete!")

pi.set_servo_pulsewidth(SERVO_GPIO, 1405)             #1800
pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO, 1530)        #1400
pi.set_servo_pulsewidth(UP_DOWN_GPIO, 1000)

if not pi.connected:
    exit()

print("PI online")

response=""
cnt = 1
ht_cnt = 1
float_result_left_right = 0.0
float_result_up_down = 0.0

# serial _ module
#def readThread(port):
    
    #while True:
        #response=port.read(12)
        #rfid= "Challenge:"+response[1:9]+":\n"
        #print(rfid)
        #s.send(rfid)
        
#thread = threading.Thread(target=readThread, args=(port,))
#thread.start()

while True:
    try:
        #except KeyboardInterrupt:
        #sys.exit()
        try:
            recv_msg = str(s.recv(1024)).encode('utf-8')
            #print(recv_msg)
            #response = port.read(12)
            

        except socket.error as e:
            #os.system('sudo reboot -f')
            #ESC_PWM_MID = 1375.00
            #time.sleep(0.1) 
            print(e)
            
            #print("socket error??")
        else:
            #recv_msg = str(recv_msg, 'utf-8')
            #print("length ::: "+str(len(recv_msg.split(';')[3])))
            #if len(recv_msg.split(';')[3]) < 3:
            if recv_msg.startswith(b"D"):   #D-Pad
                try:
                    float_pad_left_right = float(recv_msg.split(";")[1][:6])
                    #print(float_pad_left_right)
                except IndexError:
                    float_pad_left_right = 0.0
                try:
                    float_pad_up_down = float(recv_msg.split(";")[2][:6])
                except IndexError:
                    float_pad_up_down = 0.0
                
                #if float_pad_left_right >= 0 and float_pad_left_right < 1: #right
                    #float_result_pad_left_right = ((260 * float_pad_left_right)*(-1)) + 1530   #1255  1405
                    
                #if float_pad_left_right < 0 and float_pad_left_right > -1: #left
                    #float_result_pad_left_right =  ((260 * float_pad_left_right)*(-1)) + 1530  #1255  1405

                if float_pad_up_down >= 0 and float_pad_up_down < 1:    #up
                    float_result_pad_up_down = ((150 * float_pad_up_down)*(1)) + 1050
        
                if float_pad_up_down < 0 and float_pad_up_down > -1:    #down
                    float_result_pad_up_down = ((200 * float_pad_up_down)*(1)) + 1050

                #if float_result_pad_left_right != 0 and float_result_pad_left_right >= 500 and float_result_pad_left_right <= 2500:
                    #pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO, (float_result_pad_left_right))

                if float_result_pad_up_down != 0 and float_result_pad_up_down >= 500 and float_result_pad_up_down <= 2500:
                    pi.set_servo_pulsewidth(UP_DOWN_GPIO, (float_result_pad_up_down))
            
            if recv_msg.startswith(b"H"):   #HeadTracker
                #print(str(recv_msg)+":::::aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                if cnt == 1:
                    try:
                        float_init_left_right = float(recv_msg.split(';')[2][:7])
                    except IndexError:
                        float_init_left_right = 0.0

                    try:
                        float_init_up_down = float(recv_msg.split(';')[1][:7])
                    except IndexError:
                        float_init_up_down = 0.0
                
                    
                    cnt = 2 

#               if ht_cnt == 1 or ht_cnt == 5:
                try:
                    float_left_right = (float(recv_msg.split(';')[2][:7]) - float_init_left_right) 
                #   print("LLLLLLLLLLL ::: "+str(float_left_right))
                except IndexError:
                    float_left_right = 0.0
                try:
                    float_up_down = (float(recv_msg.split(';')[1][:7]) - float_init_up_down)
                #   print("UUUUUUUUUUU ::: "+str(float_up_down))
                except IndexError:
                    float_up_down = 0.0

                if float_left_right >= 0 and float_left_right < 0.25:   #left
                    float_result_left_right = (((260/0.25) * float_left_right)*(-1)) + 1240      # 1255
                if float_left_right >= 0.35 and float_left_right <= 1:
                    float_result_left_right = 995

                if float_left_right < 0 and float_left_right > -0.25:   #right
                    float_result_left_right = (((260/0.25) * float_left_right)*(-1)) + 1240      # 1255  
                if float_left_right >= -1 and float_left_right <=-0.35:
                    float_result_left_right = 1515

                if float_up_down < 0 and float_up_down > -0.15:     #down
                    float_result_up_down = (((200/0.15) * float_up_down)*(1)) + 1050
                if float_up_down >= -1 and float_up_down <= -0.15:
                    float_result_up_down = 850

                if float_up_down >= 0 and float_up_down < 0.25:     #up
                    float_result_up_down = (((170/0.25) * float_up_down)*(1)) + 1050
                if float_up_down >= 0.25 and float_up_down <= 1:
                    float_result_up_down = 1220

                #if float_left_right <= 0 and float_up_down >=0 and float_up_down < 0.25:
                #   float_result_up_down = (((170/0.25) * float_up_down)*(1)) + 1050
                #if float_left_right <= 0 and float_up_down >= 0.25 and float_up_down <= 1:
                #   float_result_up_down = 1220
                #if float_left_right <= 0 and float_up_down < 0 and float_up_down > -0.15:
                #   float_result_up_down =  (((200/0.15) * float_up_down)*(1)) + 1050
                #if float_left_right <= 0 and float_up_down <= -0.15 and float_up_down >= -1:
                #   float_result_up_down = 850
            
    #           print("xxxxxxxxxxxxxxxxxxxxxxxxx ::::::"+str(float_left_right))
    #           print("yyyyyyyyyyyyyyyyyyyyyyyyy ::::::"+str(float_up_down))
#               if int_left_right >= -90 and int_left_right < 0:        #right
#                   int_result_left_right =( ((205 / 90) * int_left_right)*(-2)) +1255
                
                    #int_result_left_right = ((205 / 45) * int_left_right) + 1255
#               if int_left_right > -180 and int_left_right <-90:
#                   int_result_left_right = 1460
                

#               if int_left_right <= 90 and int_left_right > 0: #left
#                   int_result_left_right = (((205 / 90) * int_left_right)*(-2)) + 1255
#               if int_left_right < 180 and int_left_right > 90:
#                   int_result_left_right = 1080
                
#               if int_up_down >=-90 and int_up_down < 0:   #up
#                   int_result_up_down = (((130 /90) * int_up_down)*(-2)) + 1050
#               if int_up_down > -180 and int_up_down < -90:
#                   int_result_up_down = 1180
                
#               if int_up_down <= 90 and int_up_down > 0:   #up 
#                   int_result_up_down = (((110 / 90) * int_up_down)*(-2)) + 1050
#               if int_up_down < 180 and int_up_down > 90:
#                   int_result_up_down = 940
                

                if float_result_left_right != 0 and float_result_left_right >= 995 and float_result_left_right <= 1515:
                
                #   print("RRRRRRRRR"+str(float_result_left_right))
                    pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO, (float_result_left_right))
                if float_result_up_down != 0 and float_result_up_down >= 500 and float_result_up_down <= 2500:
                #   print("BBBBBBBBBBBBBBBBbbb"+str(float_result_up_down))
                    pi.set_servo_pulsewidth(UP_DOWN_GPIO, (float_result_up_down))
                    
#               ht_cnt = ht_cnt + 1
#               if ht_cnt == 6:
#                   ht_cnt = 2

            elif recv_msg.startswith(b"W"):     #Wheel
                try:
                    float_recv_wheel = float(recv_msg.split(';')[3][:6])
                    float_recv_wheel_1 = float_recv_wheel * (-1.0)
                    #print(float_recv_wheel)
                except IndexError:
                    float_recv_wheel = 0.0
                #elif len(recv_msg.split(';')[3]) > 3:
                #   float_recv_wheel = float(recv_msg.split(';')[3][:6])
    #           print("aaaaaaaaaaaa ::: "+str(float_recv_wheel))
                if recv_msg.split(';')[1] != 0:
                    try:    
                        float_recv_axel = float(recv_msg.split(';')[1][:6])
                    except IndexError:
                        float_recv_axel = 0.0
                    try:
                        float_recv_brake = float(recv_msg.split(';')[2][:6])
                    except IndexError:
                        float_recv_brake = 0.0
                
                if float_recv_wheel < 0:
                    float_result_wheel = ((550 * float_recv_wheel_1)*(-1)) + 1405       #1800     550 1405
                    #pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO,(float_result_wheel))
                if float_recv_wheel > 0:
                    float_result_wheel = ((550 * float_recv_wheel_1)*(-1)) + 1405       #1800
                    #pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO,(float_result_wheel))
                
                ########################################  wheel tilt ######################################
                #if float_recv_wheel >= 0 and float_recv_wheel < 1:
                    #float_wheel_left_right = ((260*float_recv_wheel)*(-1))+1530
                #if float_recv_wheel < 0 and float_recv_wheel > -1:
                    #float_wheel_left_right = ((260*float_recv_wheel)*(-1))+1530
                #if float_wheel_left_right != 0 and float_wheel_left_right >= 500 and float_wheel_left_right <= 2500:
                    #pi.set_servo_pulsewidth(LEFT_RIGHT_GPIO,(float_wheel_left_right))
                ###########################################################################################
                
                float_result_axel = (485 * float_recv_axel) + ESC_PWM_MID                   #1500
                float_result_brake = ((285 * float_recv_brake) * (-1)) + ESC_PWM_MID
                #print("wheel : "+str(float_result_wheel))
                #print("axel : "+str(float_recv_axel))
                #print("brake : "+str(float_recv_brake))
                int_recv_axel = int(float_recv_axel)
                #print("int axel ::::::"+ str(int(float_result_axel)))
                int_recv_brake = int(float_recv_brake)
                #position = int(input("enter servo value : "))
                pi.set_servo_pulsewidth(ESC_GPIO, (int(float_result_axel)))
                #pi.set_servo_pulsewidth(ESC_GPIO, (int(1000)))
                pi.set_servo_pulsewidth(SERVO_GPIO, (float_result_wheel))  #
                
                if int(float_result_brake) == 1367:
                    #pi.set_servo_pulsewidth(SERVO_GPIO, (float_result_wheel))
                    #print(str(float_result_axel))
                    pi.set_servo_pulsewidth(ESC_GPIO, (int(float_result_axel)))
                if int(float_result_axel) == 1367:
                    #pi.set_servo_pulsewidth(SERVO_GPIO, (float_result_wheel))
                    pi.set_servo_pulsewidth(ESC_GPIO, (int(float_result_brake)))
                if int(float_result_brake) != 1367.0  and int(float_result_axel) != 1367.0:
                    float_result_brake = 1367.0
                    pi.set_servo_pulsewidth(ESC_GPIO,(int(float_result_brake)))
                
                #time.sleep(0.1)

            int_send_wheel = int(pi.get_servo_pulsewidth(SERVO_GPIO))
            float_send_wheel = (int_send_wheel - 1405)/550.0000      # 1800

            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()

            float_ACCx = float((ACCx * 0.244)/1000)
            float_ACCy = float((ACCy * 0.244)/1000)


            s.send("Car:"+str(float_ACCx)+","+str(float_ACCy)+","+str(float_send_wheel)+"\n")
            float_send_wheel = 0.0

            if response:        
                rfid = "Challenge:"+response[1:9]+":\n"
                print(rfid)
                s.send(rfid)

                rfid=""
    except KeyboardInterrupt:
        print("Key terminate")
GPIO.cleanup()
