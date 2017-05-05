import RPi.GPIO as GPIO
import time
import os
import glob
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#          [ a,  b,  c,  d, e, f, g]
segments = [26, 16, 19, 13, 6, 5, 0]

for segment in segments:
	GPIO.setup(segment, GPIO.OUT)
	GPIO.output(segment, 1)

digits = [20, 21]

for digit in digits:
	GPIO.setup(digit, GPIO.OUT)
	GPIO.output(digit, 0)

#      'n':[a, b, c, d, e, f, g]
num = {' ':[],
       '0':[0, 0, 0, 0, 0, 0, 1],
       '1':[1, 0, 0, 1, 1, 1, 1],
       '2':[0, 0, 1, 0, 0, 1, 0],
       '3':[0, 0, 0, 0, 1, 1, 0],
       '4':[1, 0, 0, 1, 1, 0, 0],
       '5':[0, 1, 0, 0, 1, 0, 0],
       '6':[0, 1, 0, 0, 0, 0, 0],
       '7':[0, 0, 0, 1, 1, 1, 1],
       '8':[0, 0, 0, 0, 0, 0, 0],
       '9':[0, 0, 0, 0, 1, 0, 0]}

freq = 35

delay = float(1/(float(freq)*2))

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
command = 'cat ' + device_file + ' | grep "t=" | cut -d "=" -f 2'

def read_temp():
	temp_string = subprocess.check_output([command], shell=True)
	temp_c = float(temp_string) / 1000.0
	temp = str(temp_c).split('.')
	global temp_left
	temp_left = temp[0].rjust(2, '0')
	global temp_right
	temp_right = temp[1].ljust(2, '0')
	return

try:
	read_temp()
	temp_time = time.time()
	unit_time = time.time()
	while True:
		if time.time() - temp_time > 60:
			read_temp()
			temp_time = time.time()
			unit_time = time.time()

		for digit in range(2):
			GPIO.output(digits[digit], 1)

			if time.time() - unit_time > 5:
				for segment in range(7):
					GPIO.output(segments[segment], num[temp_right[digit]][segment])
				if time.time() - unit_time > 6:
					unit_time = time.time()
			else:
				for segment in range(7):
					GPIO.output(segments[segment], num[temp_left[digit]][segment])

			time.sleep(delay)

			GPIO.output(digits[digit], 0)

except KeyboardInterrupt:
	GPIO.cleanup()
