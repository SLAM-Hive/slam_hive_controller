FROM ros:noetic-perception
WORKDIR /home/code

#RUN sed -i s/archive.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list && \
#    sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list && \
#    apt-get update && apt-get upgrade -y
#
#RUN apt update && apt install -y pip

# ADD project .
COPY . .


# 运行更新命令
RUN apt-get update && apt-get upgrade -y

# 安装Python 3.7和pip
RUN apt-get install -y python3.7 python3-pip

# RUN apt-get install -y ros-melodic-cv-bridge

# # 设置Python 3.7为默认版本
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
    pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# ADD requirements.txt .

RUN pip3 install -r requirements.txt --ignore-installed

# ENTRYPOINT ["python", "test1.py"]
# CMD ["python3", "project/controller.py"]

ENTRYPOINT ["/bin/bash"]





# # 使用官方的ROS镜像作为基础
# FROM ros:melodic
# WORKDIR /home/code

# #RUN sed -i s/archive.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list && \
# #    sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list && \
# #    apt-get update && apt-get upgrade -y
# #
# #RUN apt update && apt install -y pip

# ADD test_docker-APIClient.py .
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
#     pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# ADD requirements.txt .

# RUN pip install -r requirements.txt

# # ENTRYPOINT ["python", "test1.py"]

# ENTRYPOINT ["/bin/bash"]



# # 运行更新命令
# RUN apt-get update && apt-get upgrade -y

# # 安装Python 3.7和pip
# RUN apt-get install -y python3.7 python3-pip

# # 设置Python 3.7为默认版本
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

# # 安装其他软件包和Python依赖
# RUN apt-get install -y <package1> <package2> ...
# RUN pip3 install <python_package1> <python_package2> ...

# # 设置ROS环境变量
# ENV ROS_PACKAGE_PATH /catkin_ws/src

# # 设置工作目录
# WORKDIR /catkin_ws

# # 构建ROS包
# RUN /bin/bash -c "source /opt/ros/melodic/setup.bash && catkin_make"

# # 设置启动命令
# CMD ["roslaunch", "your_package", "your_launch_file.launch"]