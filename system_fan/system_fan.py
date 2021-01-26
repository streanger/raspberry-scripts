'''
script for fan control (ON/OFF), depends on specified edge temperatures
'''
import time
import subprocess
import RPi.GPIO as GPIO


def cpu_temp():
	'''cpu temperature
	divide by 1000, to get human readable value
	'''
	cmd = 'cat /sys/class/thermal/thermal_zone0/temp'
	cmd_out = subprocess.getoutput(cmd)
	temp_float = (int(cmd_out.strip())/1000)
	#temp_str = "temp={:01.1f}'C".format(temp_float)
	return temp_float
	
	
def gpu_temp():
	'''
	gpu temperature
	example:
		temp=47.2'C
	'''
	cmd = 'vcgencmd measure_temp'
	temp_str = subprocess.getoutput(cmd)
	temp_float = float((temp_str.split('=')[1]).split("'")[0])
	return temp_float
	
	
if __name__ == "__main__":
	# ******** SETUP ********
	GPIO.setwarnings(False) # Ignore warning for now
	GPIO.setmode(GPIO.BCM) # Use Broadcom SOC channel
	
	# set edge temperatures ['C]
	low_temp, high_temp = 55, 70
	
	
	# ******** MOTOR ********
	print('[*] system_fan app starts')
	FAN_MOTOR = 18
	GPIO.setup(FAN_MOTOR, GPIO.OUT, initial=GPIO.LOW)
	
	
	# ******** LEDS ********
	LED_GREEN = 14
	LED_RED = 15
	
	GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.LOW)
	
	# green at start
	GPIO.output(LED_GREEN, GPIO.HIGH)
	
	try:
		# main loop
		while True:
			# measure
			cpu_float = cpu_temp()
			cpu_str = "{:01.2f}'C".format(cpu_float)
			gpu_float = gpu_temp()
			gpu_str = "{:01.2f}'C".format(gpu_float)
			max_temp = max(cpu_float, gpu_float)
			max_temp_str = "{:01.2f}'C".format(max_temp)
			print('(cpu) {}, (gpu) {}; max_temp: {}'.format(cpu_str, gpu_str, max_temp_str))
			
			if max_temp < high_temp:
				# print("no need for cool, max_temp: {}'C".format(max_temp))
				time.sleep(1)
				continue
				
			# cool
			GPIO.output(FAN_MOTOR, GPIO.HIGH)	# Turn on
			
			# switch leds
			GPIO.output(LED_GREEN, GPIO.LOW)
			GPIO.output(LED_RED, GPIO.HIGH)
			print('[*] fan state < ON >')
			
			while True:
				# cool down 2[s]
				time.sleep(1)
				
				# measure
				cpu_float = cpu_temp()
				cpu_str = "{:01.2f}'C".format(cpu_float)
				gpu_float = gpu_temp()
				gpu_str = "{:01.2f}'C".format(gpu_float)
				max_temp = max(cpu_float, gpu_float)
				max_temp_str = "{:01.2f}'C".format(max_temp)
				print('(cpu) {}, (gpu) {}; max_temp: {}'.format(cpu_str, gpu_str, max_temp_str))
				
				# check if we are under low_temp
				if max_temp < low_temp:
					# print("now its cool, max_temp: {}'C".format(max_temp))
					GPIO.output(FAN_MOTOR, GPIO.LOW)	# Turn off
					
					# switch leds
					GPIO.output(LED_GREEN, GPIO.HIGH)
					GPIO.output(LED_RED, GPIO.LOW)
					print('[*] fan state < OFF >')
					break
					
	except KeyboardInterrupt:
		print('broken by user')
		
	finally:
		GPIO.cleanup()
		print('GPIO pins cleaned')
		
		
'''
info:
	J8:
	   3V3  (1) (2)  5V    
	 GPIO2  (3) (4)  5V    
	 GPIO3  (5) (6)  GND   
	 GPIO4  (7) (8)  GPIO14
	   GND  (9) (10) GPIO15
	GPIO17 (11) (12) GPIO18
			  ...
	
	LED_GREEN 	- GPIO14
	LED_RED 	- GPIO15
	FAN_MOTOR	- GPIO18
	
todo:
	-clear all not used lines at start
	-use PWM
	-
	
'''
