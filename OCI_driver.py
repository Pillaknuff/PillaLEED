#import required packages
from distutils.command.config import config
from tkinter import *
from tkinter.filedialog import askdirectory
import numpy as np
import serial
import cv2
import urllib.request
import time
import io
import binascii
import _thread as thread
from PIL import Image
from pathlib import Path
import time
from datetime import datetime
from tkinter import ttk
import os

# #Define standard values
# #Energy in eV
# energy_start=100.0
# energy_step = 5.0
# energy_stop = 150.0
# #Filiament current in A
# filiament_current = 2.7
# #Voltages in V
# grid_voltage_ratio=0.7
# focus_voltage_ratio = 1.2
# wehnelt_voltage=0.0
# screen_voltage=5000
# #camera adress
# camera_ip='http://192.168.88.103/axis-cgi/mjpg/video.cgi'
# #Savepath
# save_path=""
# #String added to the filename at the begining of each file
# today = datetime.today()
# today_str = today.strftime("%Y-%m-%d")
# now = datetime.now()
# current_time = now.strftime("%H-%M-%S")
# subfolder_path = today_str +"_" + current_time 
# file_name_prefix = "Sample"

# #Number of pictures to save for each energy
# number_of_pictures = 5
# #time to wait after values are send until pictures are taken in s
# time_delay = 3
# #Variable to check if device was initialized
LEED_not_set = True

#Function to send data to LEED
#command: specific command to adress value e.g. "V1" to set filiament current
#value: value to set (see list below), expects string with 5 chars with the number value as the last 4 chars
#List of commands:
"""V1 1700 Filament: 1.70A
V2 1005 Energie: 100.5eV
V3 5000 Screen: 5kV
V4 0070 Grid: 70V
V5 0121 Focus: 121V
V6 0010 Wehnelt: 1.0V """

class myLEED:
    def __init__(self,baud,com):
        self.baud = baud
        self.com = com

        self.settings_available = {                             # Goes as following: Internal name: External name to write, to read, conversion factor, Unit, limits
            'I_Fil' : ['V1', 'V7', 1000, 'A', [0,2.9]],         # Filament Current in Amps
            'E_Beam' : ['V2', 'VA', 10, 'V', [0,750]],          # Beam Energy in Volts
            'Screen' : ['V3', 'VD', 1, 'V', [0,5000]],
            'Grid' : ['V4','VB',1,'V',[0,3200]],
            'Focus' : ['V5', 'VE', 1 , 'V', [0,3200]],
            'Wehnelt' : ['V6', 'V9', 10, 'V', [0,40]],          # Wehnelt in Volt
        }

    def give_settings(self):                                    # to be called externally to get the settings dict
        return self.settings_available

    def reconfigure(self,baud,com):
        self.baud = baud
        self.com = com

    def getSingleAttribute(self,name):
        try:
            cmd = self.settings_available[name][1]
            error = False
        except:
            print("Invalid parameter asked "+ str(name) )
            error = True

        if not error:
            answer,error = self.getFromDevice(cmd)
            try:
                answer = answer.split(' ')[1]
                answer = float(answer)
                answer = answer/float(self.settings_available[name][2])
            except Exception as e:
                print('Error getting attribute' + str(e))
                error = True
                answer = 0
        return answer, error

    def getAllAttributes(self):
        answer, error = self.getFromDevice('VZ')
        answerdict = {}
        try:
            answer = answer.split(' ')
            for key in self.settings_available.keys():
                referer = self.settings_available[key][1]
                index = answer.index(referer)
                value = answer[index+1]
                value = float(value)/float(self.settings_available[key][2])
                answerdict[key] = value
        except Exception as e:
            print("error getting all attributes " + str(e))
            error = True
        
        return answerdict, error

    def setAttribute(self,key,value, chk=True):
        com = self.settings_available[key][0]
        if chk:
            if (value > self.settings_available[key][4][0]) and (value < self.settings_available[key][4][1]):
                outofbounds = False
            else:
                outofbounds = True
        else:
            outofbounds = True

        if not outofbounds:
            value = int(value*self.settings_available[key][2])
            value = '%04d'%value
            com = com + ' ' + value
            ans, err = self.getFromDevice(com)
        else:
            print('out of bounds: ' + key)
            err = True
        return err



    def getFromDevice(self,command):
        error = False
        try:
            ser = serial.Serial()
            ser.baudrate = self.baud
            ser.port = self.com
            ser.open()
            serialcmd = command + '\r'
            ser.write(serialcmd.encode())
            read_val = ser.read()
            ser.close()
            return read_val, error
        except Exception as e:
            print("error in getFromDevice " + str(e))
            return '', True



    #******************************some more advanced methods*****************************
    def setAttributesByList(self,dict):
        for key in dict.keys():
            self.setAttribute(key,dict[key])

    #set all values back to zero
    def reset_LEED(self):
        for key in self.settings_available.keys():
            self.setAttribute(key,0)

# old!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # def send_value(self, command, value):
    #     try: 
    #         ser = serial.Serial()
    #         ser.baudrate = self.baud
    #         ser.port = self.com
    #         ser.open()
    #         serialcmd = command + " " + value[1:5] + '\r'
    #         ser.write(serialcmd.encode())
    #         ser.close()
    #         print(command + " " + value[1:5] + '\r')

    #         return False
    #     except Exception as e:
    #         print("error in serial com " + str(e))
    #         return True

    # #Function to acquire data from LEED
    # #command: command to get value
    # """V7 1703 --> Filament in mA
    # V8 0000 --> Emission in µA
    # V9 0010 --> Wehnelt in 0.1 V
    # VA 1000 --> Energie in 0.1 V
    # VB 0069 --> Grid in V
    # VC 0000 --> Beamcurrent in 10 nA
    # VD 4998 --> Screen in V
    # VE 0120 --> Focus in V"""
    # def get_value(self,command):
    #     try:
    #         ser = serial.Serial()
    #         ser.baudrate = self.baud
    #         ser.port = self.com
    #         ser.open()
    #         serialcmd = command + '\r'
    #         ser.write(serialcmd.encode())
    #         read_val = ser.read(size=8)
    #         ser.close()
    #         return_value = int(read_val[3:7])
    #         return return_value
    #     except Exception as e:
    #         print("error in get value " + str(e))
    #         return -1




    #function to take pictures of each energy value and adjust energy
    # def start_measurement(self):
    #     error = False
    #     today = datetime.today()
    #     today_str = today.strftime("%Y-%m-%d")
    #     now = datetime.now()
    #     current_time = now.strftime("%H-%M-%S")
    #     subfolder_path = today_str +"_" + current_time
    #     label_subfolder_path.config(text=subfolder_path)
    #     #check for empty text boxes
    #     if(text_energy_start.get()!="" and text_energy_stop.get()!=""
    # and text_energy_step.get()!=""  and text_grid_voltage.get()!=""and text_wehnelt_voltage.get()!="" and text_focus_voltage.get()!="" and text_focus_voltage.get()!=""  and text_camera_ip.get()!="" and text_file_name_prefix.get()!="" and text_number_of_pictures.get()!="" and text_save_path.get()!=""):
    #         #retrieve text from text boxes
    #         wehnelt_voltage=float(text_wehnelt_voltage.get())
    #         energy_start=float(text_energy_start.get())
    #         energy_step = float(text_energy_step.get())
    #         energy_stop = float(text_energy_stop.get())
    #         grid_voltage_ratio=float(text_grid_voltage.get())
    #         focus_voltage_ratio = float(text_focus_voltage.get())
    #         camera_ip=text_camera_ip.get()
    #         save_path=text_save_path.get()
    #         file_name_prefix = text_file_name_prefix.get()
    #         number_of_pictures = int(text_number_of_pictures.get())
    #         time_delay = int(text_time_delay.get())
    #     else:
    #         error=True
    #         label_descreption.config(text="Empty insert.", fg="#ff0000")
    #     #initialize if not done
    #     print(text_save_path.get())
    #     if(LEED_not_set):
    #         initialize_LEED()
    #         window.update()
    #     #check if values are valid
    #     if(not error):
    #         if(energy_start>energy_stop):
    #             label_descreption.config(text="Energy not valid.", fg="#ff0000")
    #             error = True
    #         if( energy_start < 0 or energy_stop > 750.0):
    #             label_descreption.config(text="Energy out of range.", fg="#ff0000")
    #             error = True
    #         if(grid_voltage_ratio < 0.5 or grid_voltage_ratio > 1.1):
    #             label_descreption.config(text="Grid voltage not valid.", fg="#ff0000")
    #             error = True
    #         if(focus_voltage_ratio < 0.7 or focus_voltage_ratio > 1.8):
    #             label_descreption.config(text="Focus voltage not valid.", fg="#ff0000")
    #             error = True
    #         if(wehnelt_voltage<0 or wehnelt_voltage>37.0):
    #             label_descreption.config(text="Wehnelt Voltage not valid.", fg="#ff0000")
    #     #         error=True


    #function  to set filiament current, screen voltage and wehnelt voltage

        
    # #function to choose file path
    # def choose_file():
    #     filename = askdirectory()
    #     if(filename!=""):
    #         save_path=filename
    #         text_save_path.delete(0,END)
    #         text_save_path.insert(0,save_path)
    #         label_descreption.config(text="File path set", fg = "#000000")
    #     else:
    #         print("Empty file name.")
    #         label_descreption.config(text="Empty file path", fg="#ff0000")
        
    # #update values retrieved from device
    # def update_values():
    #     label_get_filiament_current.config(text="%.3f"%(float(get_value("V7"))/1000.0))
    #     label_get_screen_voltage.config(text="%d"%(get_value("VD")))
    #     label_get_wehnelt_voltage.config(text="%.1f"%(float(get_value("V9"))/10.0))
    #     label_get_focus_voltage.config(text="%d"%(get_value("VE")))
    #     label_get_grid_voltage.config(text="%d"%(get_value("VB")))
    #     label_get_energy.config(text="%.1f"%(float(get_value("VA"))/10.0))
    #     label_get_emission_current.config(text="%d"%(get_value("V8")))
    #     label_get_beam_current.config(text="%.2f"%(float(get_value("VC"))/100.0))

    




    #function to set energy, focus and grid voltage without taking pictures
    # def set_values(self):
    #     error = False
    #     #initialize if not done
    #     if(LEED_not_set):
    #         initialize_LEED()
    #         window.update()
    #     #check for empty text boxes
    #     if(text_energy_start.get()!="" and text_grid_voltage.get()!="" and text_wehnelt_voltage.get()!="" and text_focus_voltage.get()!="" and text_time_delay.get()!=""):
    #         #retrieve text from text boxes
    #         energy=float(text_energy_start.get())
    #         grid_voltage_ratio=float(text_grid_voltage.get())
    #         focus_voltage_ratio = float(text_focus_voltage.get())
    #         time_delay = int(text_time_delay.get())
    #         wehnelt_voltage=float(text_wehnelt_voltage.get())
    #     else:
    #         error=True
    #         label_descreption.config(text="Empty insert.", fg="#ff0000")

    #     #check if values are valid
    #     if(not error):
    #         if( energy < 0 or energy > 500.0):
    #             label_descreption.config(text="Energy out of range.", fg="#ff0000")
    #             error = True
    #         #TODO: Update Boundarys
    #         if(grid_voltage_ratio < 0.5 or grid_voltage_ratio > 1.1):
    #             label_descreption.config(text="Grid voltage not valid.", fg="#ff0000")
    #             error = True
    #         if(focus_voltage_ratio < 0.7 or focus_voltage_ratio > 1.8):
    #             label_descreption.config(text="Focus voltage not valid.", fg="#ff0000")
    #             error = True
    #         if(wehnelt_voltage<0 or wehnelt_voltage>37.0):
    #             label_descreption.config(text="Wehnelt Voltage not valid.", fg="#ff0000")
    #             error=True
    #     #send values if values are valid
    #     if(not error):
    #         label_descreption.config(text="Values send", fg = "#000000")  
    #         window.update()
    #         send_value("V2","%d"%(10000 + energy*10))
    #         grid_voltage = int(energy*grid_voltage_ratio)
    #         focus_voltage = int(energy*focus_voltage_ratio)
    #         send_value("V4","%d"%(10000 + grid_voltage))
    #         send_value("V5","%d"%(10000 + focus_voltage))
    #         send_value("V6", "%d"%(10000 + wehnelt_voltage*10))
    #         if(correct_energy.get()):
    #                 time.sleep(2)
    #                 energy_measured = float(get_value("VA"))/10.0
    #                 label_descreption.config(text="Correcting energy.", fg = "#000000")
    #                 window.update()
    #                 counter=0
    #                 temp_energy=energy
    #         #try finding correct energy in 10 iterations
    #                 while(energy_measured!=energy and counter < 10):
    #                     if(energy_measured<energy):
    #                         temp_energy=temp_energy+0.1
    #                     if(energy_measured>energy):
    #                         temp_energy=temp_energy-0.1
    #                     send_value("V2","%d"%(10000 + temp_energy*10))
    #                     time.sleep(0.5)
    #                     energy_measured = float(get_value("VA"))/10.0
    #                     counter=counter+1
    #                 if(counter==10):
    #                     label_descreption.config(text="Energy not set after 10 iterations.", fg="#ff0000")
    #                 else:   
    #                     label_descreption.config(text="Energy set", fg = "#000000")
    #                 update_values()
    #         else:
    #                 time.sleep(time_delay)
    #                 update_values()



