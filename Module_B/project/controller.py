import docker, time, os, yaml, requests, json, datetime, csv
import numpy as np
from kubernetes import client, config

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)

import yaml

import paramiko

from stat import S_ISDIR

from pathlib import Path

import dataset_preprocess

import init_config
import subprocess

import utils
from utils import get_cpu_infos, put_all_files_in_remote_dir, get_all_files_in_remote_dir, pre_transfer_data, pre_transfer_result_folder, transfer_CPU_info, pre_handle_dataset

def container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath, real_task_id, host_ip):
    # mount datasetPath, resultPath, configPath to image
    # Create Container
    client = docker.from_env()
    print("===========Start Container: [slam-hive-algorithm:" + algoTag + "]===========")
    volume = {scriptsPath:{'bind':'/slamhive','mode':'rw'},
            datasetPath:{'bind':'/slamhive/dataset','mode':'ro'},
            resultPath:{'bind':'/slamhive/result','mode':'rw'},
            configPath:{'bind':'/slamhive/config.yaml','mode':'ro'}}
    import random
    algo = client.containers.run("slam-hive-algorithm:" + algoTag, command='/bin/bash', detach=True, tty=True, volumes=volume, name = "mappingtask_" + real_task_id)
    print("================Running Task=================")
    # algo_exec = algo.exec_run('bash /slamhive/mappingtask.sh', tty=True, stream=True)


    
    

    algo_exec = algo.exec_run('python3 /slamhive/mapping.py', tty=True, stream=True)



    # 将cadvisor所需要的信息都输出到一个文件中

    cadvisor_config_path = "/slamhive/result/" + real_task_id + "/cadvisor_config.txt"
    # 创建文件
    cadvisor_config_file = open(cadvisor_config_path,'w')

    text_content = "ip:" + host_ip + " " + "containerid:" + algo.id
    cadvisor_config_file.write(text_content)

    cadvisor_config_file.close()

    ## put the file to the master
    sftp.put(cadvisor_config_path, "/SLAM-Hive/slam_hive_results/mapping_results/" + real_task_id + "/cadvisor_config.txt")


    cadvisor_config_file = open(cadvisor_config_path, 'r')
    content = cadvisor_config_file.read()
    t_ip = content.split(' ')[0].split(':')[1]
    t_id = content.split(' ')[1].split(':')[1]
    print("host ip:", t_ip, "container id:", t_id)
    cadvisor_config_file.close()



    # 创建log文件
    log_path = "/slamhive/result/" + real_task_id + "/log.txt"
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
            log_file.write(now_str)
        except StopIteration:
            break

    log_file.close()
    sftp.put(log_path, "/SLAM-Hive/slam_hive_results/mapping_results/" + real_task_id + "/log.txt")

# 写完所有finished

    # final_results_src_path = '/slamhive/result/' + real_task_id
    # final_results_dest_path = '/SLAM-Hive/slam_hive_results/mapping_results/' + real_task_id

    traj_flag = True
    traj_path = os.path.join("/slamhive/result", real_task_id, "traj.txt")
    traj_flag_path = os.path.join("/slamhive/result", real_task_id, "traj_flag.txt")
    if not Path(traj_path).is_file():
        traj_flag = False
    else :
        # 判断轨迹文件中是否有内容
        if not os.path.getsize(traj_path):
            traj_flag = False

    if traj_flag == False:
        # 轨迹生成失败
        f = open(traj_flag_path, 'w')
        f.write("False")
        f.close()
    else :
        f = open(traj_flag_path, 'w')
        f.write("True")
        f.close()
    

    # TODO not in image
    # just copy traj.txt; maybe other generated file need to tranform
    # so can bianli folder

    traj_src_path = '/slamhive/result/' + real_task_id + "/traj.txt"
    traj_dest_path = '/SLAM-Hive/slam_hive_results/mapping_results/' + real_task_id + "/traj.txt"
    traj_flag_src_path = '/slamhive/result/' + real_task_id + "/traj_flag.txt"
    traj_flag_dest_path = '/SLAM-Hive/slam_hive_results/mapping_results/' + real_task_id + "/traj_flag.txt"
    if traj_flag:
        sftp.put(traj_src_path, traj_dest_path)
    sftp.put(traj_flag_src_path, traj_flag_dest_path)

    # finished
    sftp.put("/slamhive/result/" + real_task_id + "/finished", '/SLAM-Hive/slam_hive_results/mapping_results/' + real_task_id + "/finished")

    algo.stop()
    algo.remove()
    print("==================Mapping Task Finished====================")
    ##############33
    

def pre_get_batch_config(task_id):
    # have should be the save_path, but for test, change the to name, to check if the file transport successfully
    host_src_batch_mappingtask_root_path = "/SLAM-Hive/slam_hive_results/batch_mappingtask/" + task_id
    host_dest_batch_mappingtask_root_path = "/slamhive/batch_mappingtask/" + task_id
    print("------ get batchMappingTask config ------")
    get_all_files_in_remote_dir(sftp, host_src_batch_mappingtask_root_path, host_dest_batch_mappingtask_root_path)
    # get subTask.txt
    print("------ successful ------")
    subTask_id_list = []
    subTaskConfig_id_list = []
    with open(os.path.join(host_dest_batch_mappingtask_root_path, "subTask.txt"), 'r', encoding = 'utf-8') as f:
        content = f.read()
        subTaskConfig_id_list = content.split('\n')[0].split(';')
        subTask_id_list = content.split('\n')[1].split(';')
    real_task_config_id_list = subTaskConfig_id_list[int(sub_task_id)].split(',')
    real_task_id_list = subTask_id_list[int(sub_task_id)].split(',')
    return real_task_config_id_list, real_task_id_list


###########################################################################################################
# 获取自己的pod名称

## kubernetes
config.load_kube_config()


pod_name = os.getenv('MY_POD_NAME')
pod_namespace = os.getenv('MY_POD_NAMESPACE')
host_ip = os.getenv('MY_POD_HOST_IP')

task_id = pod_name.split('-')[1]
sub_task_id = pod_name.split('-')[2]
local_batch_mappingtask_root_path = "/slamhive/batch_mappingtask"

 

# scp to the master node  
trans = paramiko.Transport(
    sock=(init_config["MASTER_INNER_IP"],init_config['SSH_PORT'])
)
trans.connect(
    username=init_config["MASTER_USER"],
    password=init_config["MASTER_PASSWORD"]
)
sftp = paramiko.SFTPClient.from_transport(trans)



real_task_config_id_list, real_task_id_list = pre_get_batch_config(task_id)

for i in range(real_task_config_id_list):
    real_task_config_id = real_task_config_id_list[i] # 没用上
    real_task_id = real_task_id_list[i]
    
    

    transfer_CPU_info(sftp=sftp, cpu_info_path="/slamhive/result/" + real_task_id + "/cpu_info.txt", dest_cpu_info_path="/SLAM-Hive/slam_hive_results/mapping_results/" + real_task_id + "/cpu_info.txt")



    detailed_result_path = os.path.join("/slamhive/result", real_task_id)
    localConfigPath, configName = pre_transfer_result_folder(task_id=real_task_id, sftp=sftp, detailed_result_path=detailed_result_path)

    with open(localConfigPath, 'r', encoding = 'utf-8') as f:
        config_dict = yaml.load(f, Loader = yaml.FullLoader)

        pre_transfer_data(task_id=real_task_id, sftp=sftp, localConfigPath=localConfigPath)


        
        # scriptsPath = os.path.join("/SLAM-Hive/slam_hive_algos", config_dict['slam-hive-algorithm'] + '/slamhive')


        # 将slamhive文件夹拷贝到一个单独的目录
        slamhive_from_path = "/slamhive/algo/" + config_dict['slam-hive-algorithm'] + '/slamhive'
        slamhive_to_path = "/slamhive/result/" + real_task_id + "/slamhive"
        import shutil
        if not os.path.exists(slamhive_to_path):
            shutil.copytree(slamhive_from_path, slamhive_to_path)


        
        ## TODO
        ## 这里需要想一个方法：如何判断该是否存在相同的已经预处理过的数据集（因为按照原来的命名规则，无法区分预处理后的数据集的依据的参数是否相同）


        # need to change dataset
        datasetPath = pre_handle_dataset(
            localConfigPath=localConfigPath,
            configName=configName,
            yaml_path=localConfigPath
            )
        

        resultPath = os.path.join("/SLAM-Hive/slam_hive_results/mapping_results/" + real_task_id)
        scriptsPath = resultPath + "/slamhive"
        configPath = os.path.join(resultPath, configName)
        algoTag = config_dict['slam-hive-algorithm']    # algo 镜像名称
        localResultsPath = os.path.join('/slamhive/result', real_task_id)  # contianer视角下的result路径
        

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

        container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath, real_task_id, host_ip)
time.sleep(3600)