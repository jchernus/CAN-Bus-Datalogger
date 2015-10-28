#!/usr/bin/env python

import subprocess, random

def parse_data(msg_id, data):
    
    if (msg_id == "477" or msg_id == "478"):
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        soc = int(data[10] + data[11] + data[8] + data[9], 16)/2

    elif (msg_id == "479" or msg_id == "480"):
        batt_high_temp = int(data[0] + data[1], 16)
        batt_low_temp = int(data[4] + data[5], 16)
        batt_high_temp_id = int(data[8] + data[9], 16)
        batt_low_temp_id = int(data[10] + data[11], 16)

    elif (msg_id == "475"):
        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        heatsink_temp = int(data[4] + data[5], 16)
        current_fault = int(data[8] + data[9] + data[6] + data[7], 16)
        traction_state = int(data[10] + data[11], 16)
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "270"):
        motor_voltage = int(data[14] + data[15] + data[12] + data[13], 16)/16.0

    elif (msg_id == "294"):
        max_batt_charge_current = int(data[6] + data[7] + data[4] + data[5], 16)
        max_batt_discharge_current = int(data[10] + data[11] + data[8] + data[9], 16)
        mc_battery_current = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "306"):
        motor_temp = int(data[2] + data[3] + data[0] + data[1], 16)
        vehicle_speed = int(data[6] + data[7] + data[4] + data[5], 16)
        motor_velocity = int(data[14] + data[15] + data[12] + data[13] + data[10] + data[11] + data[8] + data[9], 16) #Something special needs to be done with this

while (True): #Sends logs

    m477 = ''.join([random.choice('0123456789abcdef') for n in xrange(12)])
    m478 = ''.join([random.choice('0123456789abcdef') for n in xrange(12)])
    m479 = ''.join([random.choice('0123456789abcdef') for n in xrange(12)])
    m480 = ''.join([random.choice('0123456789abcdef') for n in xrange(12)])

    m475 = ''.join([random.choice('0123456789abcdef') for n in xrange(16)])
    m270 = ''.join([random.choice('0123456789abcdef') for n in xrange(16)])
    m294 = ''.join([random.choice('0123456789abcdef') for n in xrange(16)])
    m306 = ''.join([random.choice('0123456789abcdef') for n in xrange(16)])
    
    #send x messages
    p = subprocess.Popen("./cansend can0 477#" + m477, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 478#" + m478, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 479#" + m479, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 480#" + m480, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 475#" + m475, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 270#" + m270, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 294#" + m294, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    p = subprocess.Popen("./cansend can0 306#" + m306, cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
