import paramiko
import time

def test_conn(port):
    print(f"Testing connectivity to localhost:{port}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect('127.0.0.1', port=port, username='usuario', password='password', timeout=5)
        print(f"SUCCESS: Connected to port {port}")
        stdin, stdout, stderr = client.exec_command("uptime")
        print(f"Output: {stdout.read().decode().strip()}")
        client.close()
    except Exception as e:
        print(f"FAILURE on port {port}: {e}")

if __name__ == "__main__":
    test_conn(2221)
    test_conn(2222)
