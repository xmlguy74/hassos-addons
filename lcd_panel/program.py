import serial
import requests
import sys
import time
import os
import RPi.GPIO as GPIO
import threading

BEARER_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
LCD_DEVICE = sys.argv[1]

HEADERS = {'Authorization': f'Bearer {BEARER_TOKEN}','Content-Type': 'application/json'}

writeLock = threading.Lock()

def WriteStat(ser, label, entityCallback):
  writeLock.acquire()
  try:
    WriteMessage(ser, label, entityCallback())
  except BaseException as err:
    print(f'Error writing stat for {label}. {err=}', flush=True)
    try:
      WriteMessage(ser, label, GetPlaceholder())
    except BaseException as err2:
      print(f'Error in exception handler for {label}. {err2=}', flush=True)
  finally:
    time.sleep(0.5)
    writeLock.release()

def WriteMessage(ser, line1, line2):  
  ser.open()
  try:
    ser.write(f'{{"line1":"{line1.center(16)}","line2":"{line2.center(16)}"}}'.encode())
  finally:
    ser.close()

def GetState(entity):
  return entity["state"]

def GetEntity(id):
  req = requests.get(f'http://supervisor/core/api/states/{id}', headers=HEADERS)
  return req.json()

def GetCPUTemp():
  e = GetEntity("sensor.cpu_temperature")
  return GetState(e) + " F"

def GetHostUptime():
  req = requests.get(f'http://supervisor/host/info', headers=HEADERS)
  info = req.json()
  secs =  time.time() - (info["data"]["boot_timestamp"] // 1000 // 1000)
  mins = (int)(secs // 60)
  hrs = (int)(mins // 60)
  days = (int)(hrs // 24)
  if (mins < 60):
    return f"{mins} minute{'s'[:mins^1]}"
  elif (hrs < 24):
    return f"{hrs} hour{'s'[:hrs^1]}"
  else:
    return f"{days} day{'s'[:days^1]}"

def GetHostInternet():
  req = requests.get(f'http://supervisor/network/info', headers=HEADERS)
  info = req.json()
  internet = info["data"]["host_internet"]
  return "Up" if internet else "Down"

def GetAlarm():
  e = GetEntity("alarm_control_panel.alarm")
  return GetState(e).capitalize()

def GetPlaceholder():
	return "???"

def main():
  print(f"Opening serial connection to {LCD_DEVICE}", flush=True)
  ser = serial.Serial()
  ser.port=LCD_DEVICE
  ser.baudrate=9600
  ser.parity=serial.PARITY_NONE
  ser.stopbits=serial.STOPBITS_ONE
  ser.bytesize=serial.EIGHTBITS
  ser.xonxoff=serial.XOFF
  ser.rtscts=False
  ser.dsrdtr=False

  stats = [
    ("CPU Temp", GetCPUTemp),
    ("Alarm", GetAlarm),
    ("Host Uptime", GetHostUptime),
    ("Host Internet", GetHostInternet),
  ]

  statOffset = 0

  event = threading.Event()

  print("Setting up GPIO pins")
  def my_callback(channel):
    event.set()

  print(f"GPIO version = {GPIO.VERSION}")
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(24, GPIO.FALLING, callback=my_callback, bouncetime=200)

  while True:
    # get the next message
    WriteStat(ser, stats[statOffset][0], stats[statOffset][1])
    
    # wait for a timeout or signal
    if (event.wait(5)):
      event.clear()

    # increment to next stat
    statOffset = (statOffset + 1) % len(stats)

main()
