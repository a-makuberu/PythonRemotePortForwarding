import socket
import sys
import select
import paramiko
import os
import json
import threading
from datetime import datetime
import time
import chardet


SETTING_FILENAME = 'setting.json'
SETTING_IN_CODE = True

#ssh server details in dictionary
settings = {
    'ssh_server' : 'sshserver.com',
    'ssh_port' : 22,
    'username' : 'root',
    'password' : 'password',    
    'remote_bind_port' : 1022,
    'forward_host' : 'localhost',
    'forward_port' : 22,
    'ssh_log' : 'ssh.log',
    'command_interval' : 600,
    'command' : 'ipconfig',
    'stdout_log' : 'stdout.log',
    'stderr_log' : 'stderr.log',
}

def save_variables_to_json_file(filename, variables):
    with open(filename, 'w') as file:
        json.dump(variables, file)
    log(f"Variables saved to {filename}")

# Load variables from a JSON file
def load_variables_from_json_file(filename):
    with open(filename, 'r') as file:
        variables = json.load(file)
    log(f"Variables loaded from {filename}")
    return variables

def log(arg):
    log_string = '{}|{}'.format(datetime.now(),arg)
    print(log_string)
    with open(settings['stdout_log'], 'a') as file:
        file.write(log_string+'\n')
        

def handler(chan, host, port):
    #create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connect to forwarded port
    try:
        sock.connect((host, port))
        log("Forwarding to {}:{}".format(host, port))
    except Exception as e:
        log("Forwarding request to {}:{} failed: {}".format(host, port, e))
        sys.exit(1)

    #start forwarding
    try:
        while True:
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                sock.send(data)
    except KeyboardInterrupt:
        log("C-c: Port forwarding stopped.")
        sys.exit(0)    
    chan.close()
    sock.close()

#execute command intervaly and print output as threading
def execute_command_intervaly(ssh, command, interval):
    while True:
        log("Execute command: {}".format(command))
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read()
        encoding_info = chardet.detect(output)
        encoding = encoding_info['encoding']
        if encoding.lower() != 'utf-8':
            output = output.decode(encoding)
        log(output)
        time.sleep(interval)


if __name__ == "__main__":
    try:
        #load settings from file
        cwd = os.path.dirname(sys.argv[0])
        if not SETTING_IN_CODE:
            settingfile = os.path.join(cwd,SETTING_FILENAME)
            if not os.path.exists(settingfile):
                save_variables_to_json_file(settingfile, settings)
                exit()
            settings = load_variables_from_json_file(settingfile)

        #check variable is absolute path or not
        if not os.path.isabs(settings['ssh_log']):
            settings['ssh_log'] = os.path.join(cwd,settings['ssh_log'])
        if not os.path.isabs(settings['stdout_log']):
            settings['stdout_log'] = os.path.join(cwd,settings['stdout_log'])

        #setup logging
        paramiko.util.log_to_file(settings['ssh_log'])

        #setup ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(settings['ssh_server'], settings['ssh_port'], username=settings['username'], password=settings['password'])
            log("Connect to {}:{}".format(settings['ssh_server'], settings['ssh_port']))
        except Exception as e:
            log("*** Failed to connect to {}:{}: {}".format(settings['ssh_server'], settings['ssh_port'], e))
            sys.exit(1)

        #start command intervaly
        interval_thr = threading.Thread(
            target=execute_command_intervaly, args=(ssh, settings['command'], settings['command_interval'])
        )
        interval_thr.start()

        #get transport
        transport = ssh.get_transport()
        #check transport is active or not
        if not transport.is_active():
            log("Transport is not active")
            sys.exit(1)
        log("Transport is active")        

        #request port forwarding
        transport.request_port_forward('', settings['remote_bind_port'])
        log("Request port forwarding to {}:{}".format(settings['forward_host'], settings['forward_port']))

        #listen for connections
        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            thr = threading.Thread(
                target=handler, args=(chan, settings['forward_host'], settings['forward_port'])
            )
            thr.setDaemon(True)
            thr.start()    
    except e:
        with open(settings['stderr_log'], 'a') as file:
            file.write('{}|{}'.format(datetime.now(),e))
        sys.exit(1)
