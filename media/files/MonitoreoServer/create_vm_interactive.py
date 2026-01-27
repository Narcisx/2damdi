import subprocess
import os
import time
import sys

# Default Paths (Adjust if needed)
VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
DEFAULT_ISO = r"c:\Users\usuario\Desktop\ubuntu-24.04.3-live-server-amd64.iso"

def run_vbox_cmd(args):
    cmd = [VBOX_MANAGE] + args
    print(f"   [VBox] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   [Error] {result.stderr.strip()}")
    return result

def create_and_install_vm():
    print("\n=== INTERACTIVE VM CREATOR FOR DASHBOARD ===")
    print("This script will create a VirtualBox VM and install Ubuntu Server automatically.\n")

    # 1. Gather Inputs
    vm_name = input("1. Enter VM Name (e.g., MyServer1): ").strip()
    if not vm_name:
        print("Error: VM Name is required.")
        return

    ssh_port = input("2. Enter SSH Port for localhost (e.g., 2223): ").strip()
    if not ssh_port.isdigit():
        print("Error: Port must be a number.")
        return

    username = input("3. Enter New VM Username: ").strip()
    password = input("4. Enter New VM Password: ").strip()
    
    iso_path = input(f"5. Enter Path to Ubuntu ISO [Default: {DEFAULT_ISO}]: ").strip()
    if not iso_path:
        iso_path = DEFAULT_ISO

    if not os.path.exists(iso_path):
        print(f"\nError: ISO file not found at: {iso_path}")
        return

    print("\n--- Summary ---")
    print(f"VM Name: {vm_name}")
    print(f"SSH Port: {ssh_port}")
    print(f"User/Pass: {username} / {password}")
    print(f"ISO: {iso_path}")
    
    confirm = input("\nProceed? (y/n): ").lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # 2. Create VM Logic (Merged from setup_vms.py)
    print(f"\n[1/3] Creating VM '{vm_name}'...")
    run_vbox_cmd(["createvm", "--name", vm_name, "--ostype", "Ubuntu_64", "--register"])
    run_vbox_cmd(["modifyvm", vm_name, "--memory", "2048", "--vram", "32", "--cpus", "2", "--graphicscontroller", "vmsvga"])
    run_vbox_cmd(["modifyvm", vm_name, "--nic1", "nat"])
    run_vbox_cmd(["modifyvm", vm_name, "--natpf1", f"ssh-rule,tcp,,{ssh_port},,22"])
    
    # Storage
    user_home = os.path.expanduser("~")
    vm_folder = os.path.join(user_home, "VirtualBox VMs", vm_name)
    hdd_path = os.path.join(vm_folder, f"{vm_name}.vdi")
    
    # Check if HDD exists to avoid overwrite error if VM folder existed
    if not os.path.exists(hdd_path):
         run_vbox_cmd(["createhd", "--filename", hdd_path, "--size", "20000"])

    run_vbox_cmd(["storagectl", vm_name, "--name", "SATA", "--add", "sata", "--controller", "IntelAhci"])
    run_vbox_cmd(["storageattach", vm_name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", hdd_path])
    
    # 3. unattended Install Logic (Merged from setup_unattended.py)
    print(f"\n[2/3] Configuring Unattended Install...")
    
    # Ensure VM is off
    run_vbox_cmd(["controlvm", vm_name, "poweroff"])
    time.sleep(1)

    cmd_install = [
        "unattended", "install", vm_name,
        f"--iso={iso_path}",
        f"--user={username}",
        f"--password={password}",
        f"--full-user-name={username}",
        "--country=US",
        "--time-zone=UTC",
        f"--hostname={vm_name}.local",
        "--post-install-command=sudo apt-get update && sudo apt-get install -y openssh-server",
    ]
    
    res = run_vbox_cmd(cmd_install)
    
    if res.returncode == 0:
        print(f"\n[3/3] Starting Installation...")
        run_vbox_cmd(["startvm", vm_name, "--type", "gui"])
        print("\n✅ SUCCESS: VM is booting and installing automatically!")
        print("please wait 5-10 minutes for installation to finish.")
        print(f"once done, update your config.json with: IP=127.0.0.1, Port={ssh_port}, User={username}")
    else:
        print("\n❌ Error configuring unattended install.")

if __name__ == "__main__":
    create_and_install_vm()
