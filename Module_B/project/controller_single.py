import docker, time, os, yaml, requests, json, datetime, csv
import numpy as np
from kubernetes import client, config

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)

import yaml

import paramiko

import dataset_preprocess

import shutil, subprocess

import init_config
import utils
from utils import get_cpu_infos, put_all_files_in_remote_dir, get_all_files_in_remote_dir, pre_transfer_data, transfer_CPU_info, pre_transfer_result_folder, pre_handle_dataset

def container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath, host_ip):
    # mount datasetPath, resultPath, configPath to image
    # Create Container
    client = docker.from_env()
    print("===========Start Container: [slam-hive-algorithm:" + algoTag + "]===========")
    volume = {scriptsPath:{'bind':'/slamhive','mode':'rw'},
            datasetPath:{'bind':'/slamhive/dataset','mode':'ro'},
            resultPath:{'bind':'/slamhive/result','mode':'rw'},
            configPath:{'bind':'/slamhive/config.yaml','mode':'ro'}}
    import random
    algo = client.containers.run("slam-hive-algorithm:" + algoTag, command='/bin/bash', detach=True, tty=True, volumes=volume )
    # time.sleep(360000)
    print("================Running Task=================")
    # algo_exec = algo.exec_run('bash /slamhive/mappingtask.sh', tty=True, stream=True)
    # algo_exec = algo.exec_run('sleep 360000', tty=True, stream=True)
    algo_exec = algo.exec_run('python3 /slamhive/mapping.py', tty=True, stream=True)



    # 将cadvisor所需要的信息都输出到一个文件中

    cadvisor_config_path = "/slamhive/detailedResult/" + "/cadvisor_config.txt"
    # 创建文件
    cadvisor_config_file = open(cadvisor_config_path,'w')

    text_content = "ip:" + host_ip + " " + "containerid:" + algo.id
    cadvisor_config_file.write(text_content)

    cadvisor_config_file.close()




    # cadvisor_config_file = open(cadvisor_config_path, 'r')
    # content = cadvisor_config_file.read()
    # t_ip = content.split(' ')[0].split(':')[1]
    # t_id = content.split(' ')[1].split(':')[1]
    # print("host ip:", t_ip, "container id:", t_id)
    # cadvisor_config_file.close()



    # 创建log文件
    log_path = "/slamhive/detailedResult/" + "/log.txt"
    log_file = open(log_path, 'a+')

    log_file.write(configPath)


    while True:
        try:
            # print(next(algo_exec).decode())

            #剔除掉 rosbag的信息
            #  [RUNNING]  Bag Time: 1403636610.507568   Duration: 31.561362 / 187.749443 
            now_str = next(algo_exec).decode()
            if "[RUNNING]  Bag Time" in now_str :
                continue
            # print(now_str)
            log_file.write(now_str)

        except StopIteration:
            break

    log_file.close()
# 写完所有finished

    algo.stop()
    algo.remove()
    print("==================Mapping Task Finished====================")
    ##############33
    time.sleep(3600)


# 获取自己的pod名称
## kubernetes
config.load_kube_config()
#create statefulSet
v1_App = client.AppsV1Api()
v1_Core = client.CoreV1Api()

pod_name = os.getenv('MY_POD_NAME')
pod_namespace = os.getenv('MY_POD_NAMESPACE')
host_ip = os.getenv('MY_POD_HOST_IP')
print('pod_name: ', pod_name)
print('pod_namespace: ', pod_namespace)
print('host_ip: ', host_ip)

# 通过在创建pod的时候注入环境变量

## 假设已经提取好了信息
# task-999-0

task_id = pod_name.split('-')[1]


## scp xxx/
trans = paramiko.Transport(
    sock=(init_config["MASTER_INNER_IP"],init_config['SSH_PORT'])
)
trans.connect(
    username=init_config["MASTER_USER"],
    password=init_config["MASTER_PASSWORD"]
)
sftp = paramiko.SFTPClient.from_transport(trans)



dest_cpu_info_path = "/SLAM-Hive/slam_hive_results/mapping_results/" + task_id + "/cpu_info.txt"
transfer_CPU_info(sftp=sftp,cpu_info_path = "/slamhive/detailedResult/cpu_info.txt", dest_cpu_info_path=dest_cpu_info_path)


detailed_result_path = "/slamhive/detailedResult" # os.path.join("/slamhive/detailedResult", sub_task_id)
localConfigPath, configName = pre_transfer_result_folder(task_id=task_id, sftp=sftp, detailed_result_path=detailed_result_path)


with open(localConfigPath, 'r', encoding = 'utf-8') as f:
    config_dict = yaml.load(f, Loader = yaml.FullLoader)

    pre_transfer_data(task_id=task_id, sftp=sftp, localConfigPath=localConfigPath)


    # 将slamhive文件夹拷贝到一个单独的目录
    slamhive_from_path = "/slamhive/algo/" + config_dict['slam-hive-algorithm'] + '/slamhive'
    slamhive_to_path = "/slamhive/detailedResult/" + "slamhive"  ## 不记得这个是干嘛的了；需要将slamhivea文件夹手动拷贝过来吗
    if not os.path.exists(slamhive_to_path):
        shutil.copytree(slamhive_from_path, slamhive_to_path)

    

    
    # need to change dataset
    datasetPath = pre_handle_dataset(
        localConfigPath=localConfigPath,
        configName=configName,
        yaml_path=os.path.join("/slamhive/detailedResult", configName)
        )

    # in nodex
    resultPath = os.path.join("/SLAM-Hive/slam_hive_results/mapping_results/" + task_id)
    # scriptsPath = os.path.join("/SLAM-Hive/slam_hive_algos", config_dict['slam-hive-algorithm'] + '/slamhive')
    configPath = os.path.join(resultPath, configName)
    scriptsPath = resultPath + "/slamhive"
    algoTag = config_dict['slam-hive-algorithm']    # algo 镜像名称
    localResultsPath = '/slamhive/detailedResult' # os.path.join('/slamhive/detailedResult', sub_task_id)  # contianer视角下的result路径
    

    print('scriptsPath: '+ scriptsPath)
    print('algoTag: '+ algoTag)
    print('datasetPath: '+ datasetPath)
    print('resultPath: '+ resultPath)
    print('configPath: '+ configPath)
    print('loacalResultPath: ' + localResultsPath)
    # container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath)


    # get the work node physical infos

    # get_physical_infos()
    # executor.submit(get_physical_infos)
    # get_physical_infos(host_ip)
    client = docker.from_env()
    while True:
        check = True
        time.sleep(2)
        try:
            image_check = client.images.get("slam-hive-algorithm:" + config_dict['slam-hive-algorithm'])
        except docker.errors.ImageNotFound:
            check = False
        if check == True:
            break
    print("--- image load successfully! ---")

    container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath, host_ip)
