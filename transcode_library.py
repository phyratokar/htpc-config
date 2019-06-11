import os
from datetime import datetime
import argparse
import subprocess
import shutil
from pymediainfo import MediaInfo


def get_absolute_paths(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def is_video(file_path):
    fileInfo = MediaInfo.parse(file_path)
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            return True
    return False


def get_quality_tag(file_path):
    fileInfo = MediaInfo.parse(file_path)
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            if track.width == 1920:
                return " - WEB-DL-1080p"
            else:
                return " - WEB-DL-720p"


def is_transcoded(file_path):
    return os.path.isfile(os.path.splitext(file_path)[0] + '.istranscoded')


def is_transcoding(file_path):
    return os.path.isfile(os.path.splitext(file_path)[0] + '.transcodelog')


def transcode_single(file_path):
    docker_command = ["docker", "run", "--user", "1000:1000", "-v", "/home/srv-user/media:/home/srv-user/media", "--rm", "jlesage/handbrake:latest", "HandBrakeCLI"]
    docker_command.append("-i")
    docker_command.append(file_path)
    docker_command.extend(["-o", "/home/srv-user/media/temp.mp4", "-f", "av_mp4", "-e", "x264", "-q", "25", "--vfr", "-E", "copy:ac3,copy:aac", "-Y", "1080", "-X", "1920", "--optimize"])

    transcode_log = open(os.path.splitext(file_path)[0] + '.transcodelog', 'w')
    result = subprocess.run(docker_command, stderr=transcode_log)
    result.check_returncode()

    os.remove(file_path)
    new_file_path = os.path.splitext(file_path)[0] + get_quality_tag(file_path) + '.mp4'

    shutil.move('/home/srv-user/media/temp.mp4', new_file_path)

    with open(os.path.splitext(new_file_path)[0] + '.istranscoded', 'w'):
        pass


def transcode(root_dir, max_hours, log_path):
    if os.path.isfile(log_path):
        logfile = logfile = open(log_path, 'a')
    else:
        logfile = logfile = open(log_path, 'w')
        logfile.write('Time,Event,File\n')
    start_time = datetime.now()
    file_paths = get_absolute_paths(root_dir)
    for file_path in file_paths:
        if not is_transcoding(file_path) and not is_transcoded(file_path) and is_video(file_path):
            logfile.write('{},start,{}\n'.format(datetime.now().isoformat(' ', 'seconds'), file_path))
            transcode_single(file_path)
            logfile.write('{},end,{}\n'.format(datetime.now().isoformat(' ', 'seconds'), file_path))
            if (datetime.now() - start_time).seconds >= max_hours*3600:
                break

    logfile.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str)
    parser.add_argument('--max_hours', type=int)
    parser.add_argument('--logfile', type=str, default='/home/srv-user/transcode.log')

    args = parser.parse_args()

    transcode(args.root_dir, args.max_hours, args.logfile)