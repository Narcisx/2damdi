from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from vm_manager import VMManager
from shell_manager import ShellManager
import os

app = Flask(__name__, static_folder='.')
CORS(app) # Enable CORS for all routes
vm_manager = VMManager()
shell_manager = ShellManager(vm_manager)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/servers')
def get_servers():
    return jsonify(vm_manager.get_servers())

@app.route('/api/config')
def get_config():
    return jsonify(vm_manager.get_server_config())

@app.route('/api/server/<name>/start', methods=['POST'])
def start_server(name):
    success, message = vm_manager.start_vm(name)
    return jsonify({"success": success, "message": message})

@app.route('/api/server/<name>/stop', methods=['POST'])
def stop_server(name):
    success, message = vm_manager.stop_vm(name)
    return jsonify({"success": success, "message": message})

@app.route('/api/server/<name>/restart', methods=['POST'])
def restart_server(name):
    success, message = vm_manager.restart_vm(name)
    return jsonify({"success": success, "message": message})

@app.route('/api/server/<name>/screenshot')
def get_screenshot(name):
    timestamp = request.args.get('t')
    path = vm_manager.get_screenshot(name)
    if path and os.path.exists(path):
        try:
            # send_file(path) keeps file open?
            # We can use a trick: delete it after response is sent?
            # Or read into bytesIO and send?
            
            # Read to memory
            with open(path, 'rb') as f:
                data = f.read()
            
            # Now delete file
            os.remove(path)
            
            from io import BytesIO
            return send_file(BytesIO(data), mimetype='image/png')
        except Exception as e:
            print(f"Error serving screenshot: {e}")
            return "Error", 500
    else:
        return "Screenshot not available", 404

@app.route('/api/server/<id>/stats')
def get_stats(id):
    stats = vm_manager.get_stats(id)
    return jsonify(stats)

@app.route('/api/server/<id>/command', methods=['POST'])
def run_command(id):
    data = request.json
    command = data.get('command')
    # Use ShellManager for persistent session
    success = shell_manager.send_input(id, command)
    return jsonify({"success": success})

@app.route('/api/server/<id>/console/output')
def get_console_output(id):
    output = shell_manager.get_output(id)
    return jsonify({"output": output})

@app.route('/api/server/<name>/type', methods=['POST'])
def type_text(name):
    data = request.json
    text = data.get('text')
    success, msg = vm_manager.type_text(name, text)
    return jsonify({"success": success, "message": msg})

@app.route('/api/server/<id>/ssh_exec', methods=['POST'])
def ssh_exec(id):
    data = request.json
    command = data.get('command')
    # Synchronous execution
    output = vm_manager.execute_command(id, command)
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
