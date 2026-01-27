import subprocess
import os

# Adjust path if needed
VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

def run_vbox_cmd(args):
    cmd = [VBOX_MANAGE] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")
    return result

def create_vm(name, ssh_port, dashboard_ip_offset):
    # 1. Create VM
    run_vbox_cmd(["createvm", "--name", name, "--ostype", "Ubuntu_64", "--register"])
    
    # 2. Settings
    run_vbox_cmd(["modifyvm", name, "--memory", "2048", "--vram", "16", "--cpus", "2"])
    run_vbox_cmd(["modifyvm", name, "--audio", "none"])
    
    # 3. Network
    # Adapter 1: NAT with Port Forwarding for SSH (Reliable for control)
    run_vbox_cmd(["modifyvm", name, "--nic1", "nat"])
    run_vbox_cmd(["modifyvm", name, "--natpf1", f"ssh-rule,tcp,,{ssh_port},,22"])
    
    # Adapter 2: Host-Only (For "Static IP" feel and inter-vm comms if needed)
    # We need to find the name of the host-only adapter.
    # If not found, we usually stick to NAT.
    # Let's just stick to NAT for simplicity and robustness in this script.
    
    # 4. Storage
    # Create HDD
    base_folder_cmd = run_vbox_cmd(["list", "systemproperties"])
    # simplified path assumption
    user_home = os.path.expanduser("~")
    vm_folder = os.path.join(user_home, "VirtualBox VMs", name)
    hdd_path = os.path.join(vm_folder, f"{name}.vdi")
    
    run_vbox_cmd(["createhd", "--filename", hdd_path, "--size", "20000"]) # 20GB
    
    # Controller
    run_vbox_cmd(["storagectl", name, "--name", "SATA", "--add", "sata", "--controller", "IntelAhci"])
    run_vbox_cmd(["storageattach", name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", hdd_path])
    
    # DVD (IDE)
    run_vbox_cmd(["storagectl", name, "--name", "IDE", "--add", "ide"])
    # We leave it empty for now as we didn't find the ISO. User must mount it.
    run_vbox_cmd(["storageattach", name, "--storagectl", "IDE", "--port", "0", "--device", "0", "--type", "dvddrive", "--medium", "emptydrive"])

    print(f"VM {name} created. SSH Port: {ssh_port}")

def main():
    print("Checking VBoxManage...")
    ver = run_vbox_cmd(["--version"])
    if ver.returncode != 0:
        print("Cannot find VBoxManage. Please check path.")
        return

    create_vm("UbuntuServer1", "2221", 101)
    create_vm("UbuntuServer2", "2222", 102)

    print("\n\nSETUP COMPLETE")
    print("1. Please Open VirtualBox.")
    print("2. Go to Settings -> Storage -> IDE Controller -> Empty -> Choose your Ubuntu Server ISO.")
    print("3. Start the VMs and install Ubuntu Server.")
    print("4. IMPORTANT: During installation, create user 'usuario' with password 'password' (or update config.json).")
    print("5. After installation, the Dashboard will connect via localhost:2221 and localhost:2222.")

if __name__ == "__main__":
    main()
