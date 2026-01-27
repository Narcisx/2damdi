import subprocess
import paramiko
import json
import time
from threading import Lock

# You might need to adjust this path if VBoxManage is not in system PATH
VBOX_MANAGE_CMD = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

class VMManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.servers = self._load_config()
        self.vbox_lock = Lock() # Serialize VBoxManage calls

    def _run_vbox(self, args):
        """Helper to run VBoxManage with locking"""
        with self.vbox_lock:
            return subprocess.run([VBOX_MANAGE_CMD] + args, capture_output=True, text=True)

    def _run_vbox_check(self, args):
        """Helper to run VBoxManage with locking and check=True behavior"""
        with self.vbox_lock:
            subprocess.run([VBOX_MANAGE_CMD] + args, check=True)

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return []

    def get_servers(self):
        # Update status for each server
        for server in self.servers:
            server['status'] = self._get_vbox_status(server.get('name'))
        return self.servers

    def get_server_config(self):
        # Return servers without checking status (instant)
        return self.servers

    def _get_vbox_status(self, vm_name):
        try:
            # list running vms to check if it's running
            result = self._run_vbox(["showvminfo", vm_name, "--machinereadable"])
            
            if result.returncode != 0:
                print(f"Error checking VM info for {vm_name}: {result.stderr}")
                return "unknown"
            
            # Simple check in output
            if 'VMState="running"' in result.stdout:
                return "running"
            elif 'VMState="poweredoff"' in result.stdout:
                return "stopped"
            elif 'VMState="saved"' in result.stdout:
                return "saved"
            elif 'VMState="paused"' in result.stdout:
                return "paused"
            else:
                return "stopped" # Default fallback
        except FileNotFoundError:
            return "error_vbox_missing"
        except Exception as e:
            print(f"Error checking status for {vm_name}: {e}")
            return "error"

    def start_vm(self, vm_name):
        try:
            self._run_vbox_check(["startvm", vm_name, "--type", "headless"])
            return True, "VM started"
        except Exception as e:
            return False, str(e)

    def stop_vm(self, vm_name):
        try:
            # Try ACPI shutdown first for graceful exit
            self._run_vbox_check(["controlvm", vm_name, "acpipowerbutton"])
            return True, "ACPI Shutdown signal sent"
        except Exception as e:
            try:
                # Force poweroff if needed
                self._run_vbox_check(["controlvm", vm_name, "poweroff"]) 
                return True, "VM Forced Poweroff"
            except Exception as e2:
                return False, str(e2)

    def restart_vm(self, vm_name):
        try:
            self._run_vbox_check(["controlvm", vm_name, "reset"])
            return True, "VM Restarted (Reset)"
        except Exception as e:
            return False, str(e)

    def take_screenshot(self, vm_name):
        try:
            # Save to current directory as <vm_name>.png
            filename = f"{vm_name}.png"
            # VBoxManage controlvm <uuid|vmname> screenshotpng <filename>
            subprocess.run([VBOX_MANAGE_CMD, "controlvm", vm_name, "screenshotpng", filename], check=True)
            return filename
        except Exception as e:
            print(f"Error taking screenshot for {vm_name}: {e}")
            return None

    def get_ssh_client(self, server_config):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # Prioritize key auth if path provided
            if server_config.get('ssh_key_path'):
                 client.connect(server_config['ip'], port=server_config.get('ssh_port', 22), 
                                username=server_config['ssh_user'], 
                                key_filename=server_config['ssh_key_path'], timeout=3)
            else:
                client.connect(server_config['ip'], port=server_config.get('ssh_port', 22),
                               username=server_config['ssh_user'], 
                               password=server_config['ssh_password'], timeout=3)
            return client
        except Exception as e:
            print(f"SSH Connect Error to {server_config['ip']}: {e}")
            return None

    def get_stats(self, server_id):
        server = next((s for s in self.servers if s['id'] == server_id), None)
        if not server:
            return None
        
        # Only try SSH if VM is running (check vbox status first or assume from caller)
        # But for valid stats, we need SSH
        client = self.get_ssh_client(server)
        if not client:
            return {"cpu": 0, "ram": 0, "disk": 0, "error": "SSH Connection Failed"}

        try:
            # Multi-command to get stats
            # 1. CPU: usage from top (batch mode, 1 iteration) or parsing /proc/stat (harder). 
            # Simple approach: top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
            # 2. Memory: free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }'
            # 3. Disk: df -h / | awk 'NR==2 {print $5}' | sed 's/%//'
            
            cmd_cpu = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'" # us + sy
            cmd_mem = "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'"
            cmd_disk = "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'"

            stdin, stdout, stderr = client.exec_command(f"{cmd_cpu}; {cmd_mem}; {cmd_disk}")
            output = stdout.read().decode().strip().split('\n')
            
            cpu = float(output[0]) if len(output) > 0 and output[0] else 0
            ram = float(output[1]) if len(output) > 1 and output[1] else 0
            disk = float(output[2]) if len(output) > 2 and output[2] else 0

            return {"cpu": cpu, "ram": ram, "disk": disk}

        except Exception as e:
            return {"cpu": 0, "ram": 0, "disk": 0, "error": str(e)}
        finally:
            client.close()

    def execute_command(self, server_id, command):
        server = next((s for s in self.servers if s['id'] == server_id), None)
        if not server:
            return "Server not found"
        
        client = self.get_ssh_client(server)
        if not client:
            return "Could not connect via SSH"

        try:
            stdin, stdout, stderr = client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            client.close()
            return out + err
        except Exception as e:
            client.close()
            return f"Error executing command: {e}"

    def restart_vm(self, vm_name):
        try:
            # Usage: VBoxManage controlvm <uuid|vmname> reset
            subprocess.run([VBOX_MANAGE_CMD, "controlvm", vm_name, "reset"], check=True)
            return True, "VM Restarted (Reset)"
        except Exception as e:
            return False, str(e)

    def get_screenshot(self, vm_name):
        try:
            import os
            import time
            # Save to current directory temporarily with unique name
            # Format: screenshot_<vm_name>_<timestamp>.png
            timestamp = int(time.time() * 1000)
            filename = f"screenshot_{vm_name}_{timestamp}.png"
            path = os.path.abspath(filename)
            
            # Remove old screenshots for this VM first to avoid bloat
            # (In a real app, maybe use a temp dir or cleaner)
            # For now, we rely on server.py to delete after send, 
            # OR we just let them accumulate and clean up periodically?
            # Better: clean up old ones here? No, expensive.
            # Best: server.py handles cleanup after sending.
            
            # VBoxManage controlvm <uuid|vmname> screenshotpng <filename>
            self._run_vbox_check(["controlvm", vm_name, "screenshotpng", path])
            return path
        except Exception as e:
            # It might fail if VM is not running
            return None

    def type_text(self, vm_name, text):
        try:
            # Replaces spaces with specific VBox code if needed, but keyboardputstring handles most
            # VBoxManage controlvm <vm> keyboardputstring <text>
            
            # Use lock to prevent overlapped typing instructions
            
            # KEYBOARD LAYOUT FIX (ES-ES Guest):
            # 'VBoxManage keyboardputstring' assumes host input maps 1:1 to US layout.
            # On Spanish layout, the key for '-' (minus) is located where '/' is on US.
            # If we send '-', VBox presses the US minus key, which is ''' on ES.
            # To get '-', we must press the key that VBox thinks is '/', which maps to '-' on ES.
            safe_text = text.replace("-", "/")
            
            self._run_vbox_check(["controlvm", vm_name, "keyboardputstring", safe_text])
            
            # Send Enter
            # Scancode for Enter: 1c (press) 9c (release)
            self._run_vbox_check(["controlvm", vm_name, "keyboardputscancode", "1c", "9c"])
            
            return True, "Typed text + Enter"
        except Exception as e:
            print(f"Error typing to {vm_name}: {e}")
            return False, str(e)
