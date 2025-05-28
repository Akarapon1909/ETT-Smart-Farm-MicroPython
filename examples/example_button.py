from ETSmartFarm import Button
import time

def main():
    btn_reader = Button()
    while True:
        states = btn_reader.read_buttons()
        print("Pin states:", states)
        time.sleep(0.5)

if __name__ == "__main__":
    main()