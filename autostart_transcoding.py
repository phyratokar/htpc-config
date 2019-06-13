import os
import subprocess


def get_server_ip():
    command = ["ping", "-c", "1", "192.168.86.145"]
    result = subprocess.run(command)
    if result.returncode > 0:
        return '192.168.0.3'
    else:
        return '192.168.86.145'


def mount_volume(server_ip):
    command = ["sudo", "mount", "//{}/media".format(server_ip), "/home/srv-user/media"]
    result = subprocess.run(command)
    result.check_returncode()


def start_transcoding():
    command = ["python3", "/home/srv-user/htpc-config/transcode_library.py", "--root_dir", "/home/srv-user/media"]
    result = subprocess.run(command)
    result.check_returncode()

if __name__ == '__main__':
    mount_volume(get_server_ip())
    start_transcoding()
