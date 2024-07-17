# Coder  :- Naveen A. B.
# Reddit :- u/RNA3210d

# Telegram bot to monitor and control your RPi
# The teleport library enables the Raspberry Pi to communicate with the Telegram bot using the API.
# Use "sudo pip install telepot" to install telepot library
import datetime 
import telepot  
import subprocess
from telepot.loop import MessageLoop
#import RPi.GPIO as GPIO   
from time import sleep      
from gpiozero import CPUTemperature
from dotenv import load_dotenv
import os
led1 = 5  #Set the GPIO pin number of LED 1
led2 = 10 #Set the GPIO pin number of LED 2       

class GPIO_template:
    def __init__(self):
        self.BCM = None
        self.OUT = None
    def output(self, a,b):
        return None
    def setmode(self,a):
        return None
    def setup(self, a,b):
        return None

load_dotenv()

GPIO = GPIO_template()
GPIO.setmode(GPIO.BCM)     
GPIO.setup(led1, GPIO.OUT) # Declaring the output pin
GPIO.setup(led2, GPIO.OUT) # Declaring the output pin

now = datetime.datetime.now() 
temp_warning_cooldown = 3 * 60
temp_threshold = 75.0
CHAT_ID = os.getenv("CHAT_ID")


def handle(msg):
    chat_id = msg['chat']['id'] # Receiving the message from telegram
    command = msg['text']   # Getting text from the message

    past_chat_ids = []
    print ('Incoming...')
    print(command)
    if chat_id != CHAT_ID:
        if chat_id not in past_chat_ids:
            bot.sendMessage(CHAT_ID, f"Received a message from someone else than you! Message: {command}")
            past_chat_ids.append(chat_id)
    else:
        cpu = CPUTemperature()
        temp = cpu.temperature
        # Comparing the incoming message to send a reply according to it
        if command == '/help':
            bot.sendMessage (chat_id, str("ledon1 - Switch on LED 1\nledoff1 - Switch off LED 1\nledon2 - Switch on LED 2\nledoff2 - Switch off LED 2\ncpu - Get CPU info\nusb - See connected USB devices\nhi - To check if online\ntime - Returns time\ndate - Returns date\ntemp - CPU Temperature\nrepoupdate - update repositories \nupgrade - upgrade packages\nshutdown - Shutdown RPi\nreboot - Reboot RPi"))
        elif command == '/hi':
            bot.sendMessage (chat_id, str("Hi. BLEEP..BLOP.., bot is online"))
        elif command == '/time':
            bot.sendMessage(chat_id, str("Time: ") + str(now.hour) + str(":") + str(now.minute) + str(":") + str(now.second))
        elif command == '/date':
            bot.sendMessage(chat_id, str("Date: ") + str(now.day) + str("/") + str(now.month) + str("/") + str(now.year))
        elif command == '/ledon1':
            bot.sendMessage(chat_id, str("LED 1 ON"))
            GPIO.output(led1, True)
        elif command == '/ledoff1':
            bot.sendMessage(chat_id, str("LED 1 is OFF"))
            GPIO.output(led1, False)
        elif command == '/ledon2':
            bot.sendMessage(chat_id, str("LED 2 ON"))
            GPIO.output(led2, True)
        elif command == '/ledoff2':
            bot.sendMessage(chat_id, str("LED 2 is OFF"))
            GPIO.output(led2, False)
        elif command == '/temp':
            bot.sendMessage(chat_id, str("CPU temp. : ") + str(temp) + "C")
        elif command == '/repoupdate':
            bot.sendMessage(chat_id, str("Updating repos..."))
            p = subprocess.Popen("apt-get update", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, str(p))
            bot.sendMessage(chat_id, str("Update complete"))
        elif command == '/upgrade':
            bot.sendMessage(chat_id, str("Upgrading all packages..."))
            p = subprocess.Popen("apt-get upgrade -y", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, str(p))
            bot.sendMessage(chat_id, str("Upgrade complete"))
        elif command == '/shutdown':
            bot.sendMessage(chat_id, str("Shutdown command sent.."))
            subprocess.call('sudo shutdown -h now', shell=True)
        elif command == '/reboot':
            bot.sendMessage(chat_id, str("Reboot command sent.."))
            subprocess.call('sudo reboot', shell=True)
        elif command == '/cpu':
            p = subprocess.Popen("lscpu", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, p.decode('utf-8'))
        elif command == '/usb':
            p = subprocess.Popen("lsusb", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, p.decode('utf-8'))
        elif command == "/ip":
            p = subprocess.Popen("hostname -I", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, p.decode('utf-8'))
        elif command == "/sysinfo":
            cmd = """echo "CPU `LC_ALL=C top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'`% RAM `free -m | awk '/Mem:/ { printf("%3.1f%%", $3/$2*100) }'` HDD `df -h / | awk '/\// {print $(NF-1)}'`" """
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            bot.sendMessage(chat_id, p.decode('utf-8'))
# Enter your telegram token below
bot = telepot.Bot(os.getenv("TELEGRAM_API_TOKEN"))
print(bot.getMe())

# Start listening to the telegram bot and whenever a message is  received, the handle function will be called.
MessageLoop(bot, handle).run_as_thread()
print('GPIOTEL 2.00 at your service...')

while 1:
    cpu_temp = CPUTemperature().temperature
    if cpu_temp > temp_threshold:
        bot.sendMessage(CHAT_ID, f"Temperature Reached {cpu_temp}C !!!")
        sleep(temp_warning_cooldown)
    sleep(10)
