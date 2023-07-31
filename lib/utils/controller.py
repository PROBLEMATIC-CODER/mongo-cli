import subprocess
import sys
import shutil


def save_changes(file_path):
    with open(file_path, 'r') as file:
        lines = file.read()
    with open(file_path, 'w') as file:
        file.write(lines)
    file.close()


def restart_controller_child(path):
    try:
        save_changes(path)
        subprocess.run(f'C:/Python/Python310/python.exe "{path}"')
        sys.exit()
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with error: {e}")
        return False
