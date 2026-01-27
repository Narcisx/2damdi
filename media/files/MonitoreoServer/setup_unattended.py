import subprocess
import os
import time

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
ISO_PATH = r"c:\Users\usuario\Desktop\ubuntu-24.04.3-live-server-amd64.iso"

USER = "usuario"
PASSWORD = "password"

def run_vbox_cmd(args):
    cmd = [VBOX_MANAGE] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")
    return result

def install_vm(name):
    print(f"--- Setting up Unattended Install for {name} ---")
    
    # 1. Power off if running
    run_vbox_cmd(["controlvm", name, "poweroff"])
    time.sleep(2) # Wait for release

    # 2. Unattended Install Setup
    # Note: --install-additions might fail if the additions ISO isn't found, so we might omit it or handle warning.
    # We use --auxiliary-base-path to store the generated files (e.g. preseed) to avoid clutter or permission issues if default fails.
    # We'll stick to default first.
    
    cmd = [
        "unattended", "install", name,
        f"--iso={ISO_PATH}",
        f"--user={USER}",
        f"--password={PASSWORD}",
        f"--full-user-name={USER}",
        "--country=US",
        "--time-zone=UTC",
        f"--hostname={name}.local",
        "--post-install-command=sudo apt-get update && sudo apt-get install -y openssh-server",
    ]
    
    # Removing "--install-additions" to reduce failure points if VBoxGuestAdditions.iso is missing
    # But Guest Additions are good for performance.
    
    res = run_vbox_cmd(cmd)
    
    if res.returncode == 0:
        print(f"Unattended setup configured for {name}. Starting VM...")
        run_vbox_cmd(["startvm", name, "--type", "gui"]) # GUI so user can see what's happening if they want
    else:
        print(f"Failed to setup unattended install for {name}")

def main():
    if not os.path.exists(ISO_PATH):
        print(f"CRITICAL: ISO not found at {ISO_PATH}")
        return

    install_vm("UbuntuServer1")
    install_vm("UbuntuServer2")

    print("\n\ninstallation initiated. Please wait for the VMs to finish installing.")
    print("The VMs will reboot automatically.")
    print("Once they are at the login prompt, the Dashboard should be able to connect.")

if __name__ == "__main__":
    main()
