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
import subprocess

import utils
from utils import get_cpu_infos, put_all_files_in_remote_dir, get_all_files_in_remote_dir

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







def get_all_files_in_remote_dir(sftp, remote_dir, local_dir):

    # create folder in local path
    if not os.path.exists(local_dir):
        os.mkdir(local_dir)
    else :
        # wait for real finish
        return


    # 去掉路径字符串最后的字符'/'，如果有的话
    if remote_dir[-1] == '/':
        remote_dir = remote_dir[0:-1]

    # 获取当前指定目录下的所有目录及文件，包含属性值
    files = sftp.listdir_attr(remote_dir)
    for x in files:
        # remote_dir目录中每一个文件或目录的完整路径
        filename = remote_dir + '/' + x.filename
        # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
        if S_ISDIR(x.st_mode):
            get_all_files_in_remote_dir(sftp, filename, local_dir + '/' + x.filename)
        else:
            # get
            sftp.get(filename, local_dir + '/' + x.filename)

    for_test_path = local_dir + "/for_test"
    for_test_file = open(for_test_path, 'w')
    for_test_file.close()
    

def put_all_files_in_remote_dir(sftp, local_dir, remote_dir):

    # create folder in local path
    flag = True
    try:
        sftp.stat(remote_dir)
    except IOError:
        flag = False
    
    if flag: # not exists
        sftp.mkdir(remote_dir)


    # 去掉路径字符串最后的字符'/'，如果有的话
    if remote_dir[-1] == '/':
        remote_dir = remote_dir[0:-1]
    if local_dir[-1] == '/':
        local_dir = local_dir[0:-1]

    # 获取当前指定目录下的所有目录及文件，包含属性值
    files = os.listdir(local_dir)
    for x in files:
        filename = local_dir + '/' + x.filename
        # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
        if os.path.isdir(filename):
            put_all_files_in_remote_dir(sftp, filename, remote_dir + '/' + x.filename)
        else:
            # get
            sftp.put(filename, remote_dir + '/' + x.filename)

###########################################################################################################
# 获取自己的pod名称

## kubernetes
config.load_kube_config()

#create statefulSet
v1_App = client.AppsV1Api()
v1_Core = client.CoreV1Api()

pod_name = os.getenv('MY_POD_NAME')
pod_namespace = os.getenv('MY_POD_NAMESPACE')
host_ip = os.getenv('MY_POD_HOST_IP')
master_inner_ip = os.getenv('MASTER_INNER_IP')
node_name = os.getenv('MY_NODE_NAME')
print('pod_name: ', pod_name)
print('pod_namespace: ', pod_namespace)
print('host_ip: ', host_ip)
print('master inner ip: ',master_inner_ip)
print(node_name)
# node name:  task-batch22-0001
node_index = int(node_name.split('-')[2])

# 通过在创建pod的时候注入环境变量


# task - batch_mappingtask_id - 0,1...
task_id = pod_name.split('-')[1]
sub_task_id = pod_name.split('-')[2]

local_batch_mappingtask_root_path = "/slamhive/batch_mappingtask"

 

# scp to the master node  
trans = paramiko.Transport(
    sock=(master_inner_ip, 10000)
)
trans.connect(
    username="root",
    password="slam-hive1"
)
sftp = paramiko.SFTPClient.from_transport(trans)

host_dest_batch_mappingtask_root_path = "/slamhive/batch_mappingtask/" + task_id
subTask_id_list = []



# 可能需要执行多个task taskAssign.txt
# taskAssign_path = "/slamhive/batch_mappingtask/" + task_id + "/taskAssign.txt"
taskAssign_path = "/slamhive/batch_mappingtask/" + task_id + "/subTask_Aliyun.json"

with open(taskAssign_path, 'r', encoding = 'utf-8') as f:
    content = yaml.load(f, Loader=yaml.FullLoader)
    task_node = content['task_node']
    
    for key, value in task_node.items():
        if value == node_index:
            subTask_id_list.append(key)



# start to run every task one by one

for i in range(len(subTask_id_list)):


    ###################################################################### CPU info
    # 读取cpu信息
    CPU_type, CPU_cores = get_cpu_infos()
    # 写入文件，然后传输回对应路径
    cpu_info_path = "/slamhive/result/" + subTask_id_list[i] + "/cpu_info.txt"
    # 创建文件
    cpu_info_file = open(cpu_info_path,'w')

    text_content = "CPU_type:" + CPU_type + "\n" + "CPU_cores:" + str(CPU_cores)
    cpu_info_file.write(text_content)

    cpu_info_file.close()

    ## put the file to the master
    sftp.put(cpu_info_path, "/SLAM-Hive/slam_hive_results/mapping_results/" + subTask_id_list[i] + "/cpu_info.txt")
    #########################################################################

    detailed_result_path = os.path.join("/slamhive/result", subTask_id_list[i])

    configName = ""
    filelists = os.listdir(detailed_result_path)
    for fi in filelists:
        if os.path.splitext(fi)[1] == '.yaml':#目录下包含.json的文件
            configName = fi
    print("config name is:",configName)

    # 已经获取了对应的yaml配置文件 开始创建docker
    localConfigPath = os.path.join(detailed_result_path, configName)
    print("config local path:",localConfigPath)
    with open(localConfigPath, 'r', encoding = 'utf-8') as f:
        config_dict = yaml.load(f, Loader = yaml.FullLoader)


        dataset_dest_path = os.path.join("/slamhive/dataset", config_dict['slam-hive-dataset'])

        # dataset resize

        resultPath = os.path.join("/SLAM-Hive/slam_hive_results/mapping_results/" + subTask_id_list[i])
        scriptsPath = os.path.join("/SLAM-Hive/slam_hive_algos", config_dict['slam-hive-algorithm'] + '/slamhive')


        # 将slamhive文件夹拷贝到一个单独的目录
        slamhive_from_path = "/slamhive/algo/" + config_dict['slam-hive-algorithm'] + '/slamhive'
        slamhive_to_path = "/slamhive/result/" + subTask_id_list[i] + "/slamhive"
        # if not os.path.exists(slamhive_to_path) :
        #     os.mkdir(slamhive_to_path)
        import shutil
        if not os.path.exists(slamhive_to_path):
            shutil.copytree(slamhive_from_path, slamhive_to_path)

        scriptsPath = resultPath + "/slamhive"

        configPath = os.path.join(resultPath, configName)
        
        
        # datasetPath = os.path.join('/SLAM-Hive-Test/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset']) # 数据集的路径（主机下）
        dataset_frequency = config_dict['dataset-frequency']
        dataset_resolution = config_dict['dataset-resolution']
        dataset_check = False

        datasetPath = os.path.join('/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset'])
        datasetPath_new = os.path.join('/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset'] + "_" + configName)

        skip_list = [config_dict['slam-hive-dataset'] + ".bag"]

        if dataset_frequency != None or dataset_resolution != None:
        #if len(dataset_frequency) != 0 or len(dataset_resolution) != 0:
            # need to change dataset
            dataset_check = True
            
            datasetPath_local = os.path.join('/slamhive/dataset', config_dict['slam-hive-dataset'])
            datasetPath_local_new = os.path.join('/slamhive/dataset', config_dict['slam-hive-dataset'] + "_" + configName)
            print('datasetPath_local: '+ datasetPath_local)
            print('datasetPath_local_new: '+ datasetPath_local_new)
            if not os.path.exists(datasetPath_local_new):
                # 如果目标路径不存在原文件夹的话就创建
                os.makedirs(datasetPath_local_new)
            if os.path.exists(datasetPath_local):
                # 如果目标路径存在原文件夹的话就先删除
                shutil.rmtree(datasetPath_local_new)
            shutil.copytree(datasetPath_local, datasetPath_local_new, ignore = shutil.ignore_patterns(*skip_list))

            dataset_bag_path_local = datasetPath_local + "/" + config_dict['slam-hive-dataset'] + ".bag"
            dataset_bag_path_local_new = datasetPath_local_new + "/" + config_dict['slam-hive-dataset'] + ".bag"
            dataset_preprocess.dataset_preprocess(dataset_bag_path_local, dataset_bag_path_local_new, localConfigPath)
            datasetPath = datasetPath_new
            # subprocess.run("bash -c 'chmod -R 777 " + datasetPath_local_new + " ;", shell=True) meiyong
        
        
        algoTag = config_dict['slam-hive-algorithm']    # algo 镜像名称
        localResultsPath = os.path.join('/slamhive/result', subTask_id_list[i])  # contianer视角下的result路径
        

        print('scriptsPath: '+ scriptsPath)
        print('algoTag: '+ algoTag)
        print('datasetPath: '+ datasetPath)
        print('resultPath: '+ resultPath)
        print('configPath: '+ configPath)
        print('loacalResultPath: ' + localResultsPath)
        # container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath)



        container(scriptsPath, algoTag, datasetPath, resultPath, configPath, localResultsPath, subTask_id_list[i], host_ip)
time.sleep(3600)