import asyncio
import warnings
import logging
from datetime import datetime
from sniper import sniper
import csv
from colorama import *
import time
from importfiles import webhookinput, delay, rpc, license_key, autolist
import sys
import os
import uuid
import re
import requests
import json
clear = lambda: os.system('cls')
def log(content):
    print('[{}] {}'.format(datetime.utcnow(),content))
if webhookinput == "":
    log(Fore.RED+"Please fill config.json...")
    time.sleep(3)
    sys.exit()
elif delay == "":
    log(Fore.RED+"Please fill config.json...")
    time.sleep(3)
    sys.exit()
elif license_key == "":
    log(Fore.RED+"Please fill config.json...")
    time.sleep(3)
    sys.exit()
elif rpc == "":
    log(Fore.RED+"Please fill config.json...")
    time.sleep(3)
    sys.exit()
else:
    log(Fore.GREEN+"Loaded all settings... launching")
    time.sleep(1)



asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
tasks = []
with open('tasks.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tasks.append(asyncio.ensure_future(*[sniper(row["PUBLIC_KEY"],row["SECRET_KEY"],row["COLLECTION_NAME"], row["BUY_PRICE"], row["PROXIES"]).search()]))

async def run():
    await asyncio.gather(*tasks)

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    if __name__ == "__main__":


        clear()
        while True:
            print(Fore.RED+r"""▄▄▄██▀▀▀██▓  ▄████     ███▄ ▄███▓ ██▓ ███▄    █ ▄▄▄█████▓
   ▒██  ▓██▒ ██▒ ▀█▒   ▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █ ▓  ██▒ ▓▒
   ░██  ▒██▒▒██░▄▄▄░   ▓██    ▓██░▒██▒▓██  ▀█ ██▒▒ ▓██░ ▒░
▓██▄██▓ ░██░░▓█  ██▓   ▒██    ▒██ ░██░▓██▒  ▐▌██▒░ ▓██▓ ░ 
 ▓███▒  ░██░░▒▓███▀▒   ▒██▒   ░██▒░██░▒██░   ▓██░  ▒██▒ ░ 
 ▒▓▒▒░  ░▓   ░▒   ▒    ░ ▒░   ░  ░░▓  ░ ▒░   ▒ ▒   ▒ ░░   
 ▒ ░▒░   ▒ ░  ░   ░    ░  ░      ░ ▒ ░░ ░░   ░ ▒░    ░    
 ░ ░ ░   ▒ ░░ ░   ░    ░      ░    ▒ ░   ░   ░ ░   ░      
 ░   ░   ░        ░           ░    ░           ░      """)
            init(autoreset=True)
            print(Fore.RED+"1.magic eden sniper"+Style.RESET_ALL)
            while True:
                try:
                    choice = input(Fore.RED+f"Choose option: "+Style.RESET_ALL)
                    break
                except:
                    pass
            if choice == "1":
                clear()
                
                asyncio.get_event_loop().run_until_complete(run())
                break
            else:
                print(Fore.RED+"Invalid option"+Style.RESET_ALL)
                time.sleep(3)
                clear()