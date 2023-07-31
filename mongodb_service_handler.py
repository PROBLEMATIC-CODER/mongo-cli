import threading
import pyuac
import platform
import time
from lib.utils.text_colors import GREEN, RED, RESET, YELLOW

OS = platform.system().lower()
supported = OS == 'windows'


def show_waiting_dots(wait_message, max_dots):
    print(YELLOW + f"\n{wait_message} the MongoDB service" +
          RESET, end='', flush=True)
    dots = ''
    while admin_thread_done == False:
        for _ in range(max_dots):
            dots += '.'
            print(
                YELLOW + f'\r{wait_message} the MongoDB service {dots:<{max_dots}}' + RESET, end='', flush=True)
            time.sleep(0.2)
        for _ in range(max_dots):
            dots = ''
            print(
                YELLOW + f'\r{wait_message} the MongoDB service {dots:<{max_dots}}' + RESET, end='', flush=True)
            time.sleep(0.2)


def start_mongodb_service():
    try:
        if not supported:
            print(
                RED + "\nMongoDB service management is only supported in Windows operating system!" + RESET)
            return {'type': 'not supported', 'status': False}
        else:
            global admin_thread_done
            admin_thread_done = False

            def run_as_admin_thread():
                global admin_thread_done
                pyuac.runAsAdmin(['net', 'start', 'MongoDB'], False)
                admin_thread_done = True

            admin_thread = threading.Thread(
                target=run_as_admin_thread)
            admin_thread.start()

            waiting_thread = threading.Thread(
                target=show_waiting_dots, args=('Starting', 3))
            waiting_thread.start()

            admin_thread.join()

            admin_thread_done = True
            waiting_thread.join()

            print(GREEN + "\n\nSuccessfully started the MongoDB service" + RESET)
            return {'type': 'success', 'status': True}
    except Exception as e:
        print(RED + "\nUnable to start the MongoDB service" + RESET)
        return {'type': 'error', 'status': False, 'message': str(e)}


def stop_mongodb_service():
    try:
        if not supported:
            return {'type': 'not supported', 'status': False}
        else:
            global admin_thread_done
            admin_thread_done = False
            rc = None

            def run_as_admin_thread():
                global admin_thread_done
                rc = pyuac.runAsAdmin(['net', 'stop', 'MongoDB'], False)
                admin_thread_done = True

            admin_thread = threading.Thread(
                target=run_as_admin_thread)
            admin_thread.start()

            waiting_thread = threading.Thread(
                target=show_waiting_dots, args=('Stopping', 3))
            waiting_thread.start()

            admin_thread.join()

            admin_thread_done = True
            waiting_thread.join()
            print(GREEN + "\nSuccessfully stopped the MongoDB service, run 'start mongo' command to start MongoDB service" +
                  RESET)
            return {'type': 'success', 'status': True}
    except Exception as e:
        print(RED + "\nUnable to stop the MongoDB service"+RESET)
        return {'type': 'error', 'status': False, 'message': str(e)}


def restart_mongodb_service():
    try:
        if not supported:
            return {'type': 'not supported', 'status': False}

        global admin_thread_done
        admin_thread_done = False

        def run_as_admin_thread():
            global admin_thread_done
            pyuac.runAsAdmin(['net', 'restart', 'MongoDB'], False)
            time.sleep(10)
            admin_thread_done = True

        admin_thread = threading.Thread(
            target=run_as_admin_thread)
        admin_thread.start()

        waiting_thread = threading.Thread(
            target=show_waiting_dots, args=('Restarting', 3))
        waiting_thread.start()

        admin_thread.join()

        admin_thread_done = True
        waiting_thread.join()

        print(GREEN + "\nSuccessfully restarted the MongoDB service"+RESET)
        return {'type': 'success', 'status': True}

    except Exception as e:
        print(RED + "\nUnable to restart the MongoDB service"+RESET)
        return {'type': 'error', 'status': False, 'message': str(e)}


# start_mongodb_service()
