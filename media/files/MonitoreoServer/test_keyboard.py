import subprocess
import time

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAME = "UbuntuServer1"

def send_text(text):
    print(f"Typing: {text}")
    subprocess.run([VBOX_MANAGE, "controlvm", VM_NAME, "keyboardputstring", text])

def send_enter():
    print("Pressing Enter")
    # Scancode for Enter: 1C (Press), 9C (Release)
    subprocess.run([VBOX_MANAGE, "controlvm", VM_NAME, "keyboardputscancode", "1c", "9c"])

if __name__ == "__main__":
    print(f"Sending input to {VM_NAME}...")
    send_text("echo Hello from Python")
    time.sleep(1)
    send_enter()
    print("Done. Check the VirtualBox window.")
