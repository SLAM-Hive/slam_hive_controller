import subprocess

subprocess.run("bash -c 'source /opt/ros/noetic/setup.bash; \
                python3 /home/code/project/controller_single.py;'", shell=True)