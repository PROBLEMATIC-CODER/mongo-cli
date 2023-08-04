import yaml
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from utils.text_colors import RED,RESET,GREEN,YELLOW
from mongo_port_checker import *
from create_config import create_config_yaml


def update_port(command,main):
    try:
        command = command.replace('change port', '').strip()
        key = 'recent_port'
        if command.isdigit():
            running = check_mongo_running(int(command))
            if(running == True):
                try:
                    with open('config.yaml', 'r') as f:
                        data = yaml.safe_load(f)
                        if(data[key] == command):
                            print(GREEN + "\nPort has been updated"+RESET)
                            return True
                    data[key] = command
                    with open('config.yaml', 'w') as f:
                        yaml.dump(data, f)
                    print(
                        GREEN + "\nPort has been updated successfully, restarting the process...."+RESET)
                    main()
                    return True
                except FileNotFoundError:
                    create_config_yaml()
                    update_port(f'change port {command}')
            else:
                print(RED + "\nFailed to connect and update with the given port."+RESET)
                return False

        else:
            print(RED + "\nInvalid port name" + RESET)
        return False
    except Exception as e:
        print(RED + "\nFailed to connect and update with the given port"+RESET)
        return False


def get_recent_port():
    try:
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
        if(data == None):
            return None

        return data.get("recent_port")
    except (FileNotFoundError, yaml.YAMLError):

        return None


def save_port(port):
    try:
        data = {'recent_port': int(port)}
        with open('config.yaml', "w") as f:
            yaml.dump(data, f)
            return True
    except (FileNotFoundError):
        return False


def remove_port(main):
    try:
        key = 'recent_port'
        with open('config.yaml', 'r') as f:
            data = yaml.load(f,Loader=yaml.FullLoader)
            if(data is None):
                print(YELLOW+"\nRecent port not found"+RESET)
                return True
        if data is not None and key in data:
            del data[key]

        with open('config.yaml', 'w') as f:
            yaml.dump(data, f)

        print(GREEN + '\nRemoved the recent port, restarting the process...'+RESET)
        main()
        return True

    except (FileNotFoundError):
        create_config_yaml()
        print(GREEN + '\nRemoved recent port successfully'+RESET)
        return True

