import paramiko
import threading
import time
import socket

class ShellSession:
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shell = None
        self.output_buffer = ""
        self.lock = threading.Lock()
        self.last_activity = time.time()

    def connect(self):
        try:
            self.client.connect(self.ip, port=self.port, username=self.user, password=self.password)
            self.shell = self.client.invoke_shell()
            self.shell.setblocking(0)
            return True, "Connected"
        except Exception as e:
            return False, str(e)

    def send_command(self, cmd):
        if not self.shell:
            return False
        self.shell.send(cmd + "\n")
        self.last_activity = time.time()
        return True

    def read_output(self):
        if not self.shell:
            return ""
        
        data = ""
        try:
            while True:
                chunk = self.shell.recv(1024).decode('utf-8')
                if not chunk:
                    break
                data += chunk
        except:
            pass
        
        # Strip ANSI escape codes (colors, cursor moves, bracketed paste)
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_data = ansi_escape.sub('', data)
        return clean_data

class ShellManager:
    def __init__(self, vm_manager):
        self.vm_manager = vm_manager
        self.sessions = {} # {server_id: ShellSession}

    def get_session(self, server_id):
        # Create if not exists (or reconnect)
        if server_id not in self.sessions:
            # Get creds from existing vm_manager config
            server = next((s for s in self.vm_manager.servers if s['id'] == server_id), None)
            if not server:
                return None
            
            session = ShellSession(server['ip'], server['ssh_port'], server['ssh_user'], server['ssh_password'])
            success, msg = session.connect()
            if success:
                self.sessions[server_id] = session
            else:
                return None # Or raise error
        
        return self.sessions[server_id]

    def send_input(self, server_id, text):
        session = self.get_session(server_id)
        if session:
            session.send_command(text)
            return True
        return False

    def get_output(self, server_id):
        session = self.get_session(server_id)
        if session:
            return session.read_output()
        return ""
