import serial
import requests
import sys
import time
import os

BEARER_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
LCD_DEVICE = sys.argv[1]

HEADERS = {'Authorization': f'Bearer {BEARER_TOKEN}','Content-Type': 'application/json'}

def WriteStat(ser, label, entityCallback):  
  try:
    WriteMessage(ser, label, entityCallback())
  except BaseException as err:
    print(f'Error writing stat for {label}. {err=}', flush=True)
    try:
      WriteMessage(ser, label, GetPlaceholder())
    except BaseException as err2:
      print(f'Error in exception handler for {label}. {err2=}', flush=True)
  finally:
    time.sleep(5)

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

  while True:
    WriteStat(ser, "CPU Temp", GetCPUTemp)
    WriteStat(ser, "Alarm", GetAlarm)
    WriteStat(ser, "Host Uptime", GetHostUptime)

main()
