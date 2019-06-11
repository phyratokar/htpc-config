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


def is_transcoded(file_path):
    return os.path.isfile(os.path.dirname(file_path) + '/.transcoded')


def transcode_single(file_path):
    docker_command = 'docker run --rm jlesage/handbrake:latest '
    docker_command += '-i {} '.format(file_path)
    docker_command += '-o temp.mp4 '
    docker_command += '-f av_mp4 '
    docker_command += '-e x264 '
    docker_command += '-q 70 '
    docker_command += '--vfr '
    docker_command += '-E copy:ac3'

    result = subprocess.run(docker_command)
    result.check_returncode()

    os.remove(file_path)
    new_file_path = file_path[:-3] + 'mp4'

    shutil.move('temp.mp4', new_file_path)

    with open(os.path.dirname(new_file_path) + '/.transcoded', 'w'):
        pass


def transcode(root_dir, max_hours):
    start_time = datetime.now()
    file_paths = get_absolute_paths(root_dir)
    for file_path in file_paths:
        if not is_transcoded(file_path) and is_video(file_path):
            print('Starting transcoding of {}'.format(file_path))
            transcode_single(file_path)
            print('Completed transcoding {}'.format(file_path))
            if (datetime.now() - start_time).seconds >= max_hours*3600:
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str)
    parser.add_argument('--max_hours', type=int)

    args = parser.parse_args()

    transcode(args.root_dir, args.max_hours)