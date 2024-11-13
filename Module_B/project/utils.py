import subprocess
import os
from stat import S_ISDIR
import yaml,shutil

import dataset_preprocess

# return cpu_type and cpu_cores
def get_cpu_infos():
    cmd = "cat /proc/cpuinfo | grep 'model name' | sort | uniq | awk -F '[:]' '{print $2}'"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    # 去除结果字符串前后的空白字符（包括换行符）
    cleaned_result = result.stdout.strip()
    # 存储结果到变量
    CPU_type = cleaned_result
    cmd = "cat /proc/cpuinfo | grep flags | grep ' lm ' | wc -l"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    cleaned_result = result.stdout.strip()
    try:
        CPU_cores = int(cleaned_result)
    except Exception as e:
        CPU_cores = -1
    
    return CPU_type, CPU_cores


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


##############################################################################################
##############################################################################################

def transfer_CPU_info(sftp, cpu_info_path, dest_cpu_info_path):
        ###################################################################### CPU info
    # 读取cpu信息
    CPU_type, CPU_cores = get_cpu_infos()
    # 写入文件，然后传输回对应路径
    
    with open(cpu_info_path,'w') as cpu_info_file:
        text_content = "CPU_type:" + CPU_type + "\n" + "CPU_cores:" + str(CPU_cores)
        cpu_info_file.write(text_content)

    ## put the file to the master
    sftp.put(cpu_info_path, dest_cpu_info_path)
    #########################################################################sk_id + "/cpu_info.txt")


## results folder (have config file)
def pre_transfer_result_folder(task_id, sftp, detailed_result_path):
    # single和batch的result路径不一样
    # detailed_result_path = os.path.join("/slamhive/result", task_id)
    detailed_result_src_path = "/SLAM-Hive/slam_hive_results/mapping_results/" + task_id
    print("------ get mapping_results folder "+ task_id +" ------")
    get_all_files_in_remote_dir(sftp, detailed_result_src_path, detailed_result_path)
    print("------ successful ------")



    configName = ""
    filelists = os.listdir(detailed_result_path)
    for fi in filelists:
        if os.path.splitext(fi)[1] == '.yaml':#目录下包含.json的文件
            configName = fi
    print("config name is:",configName)

    # 已经获取了对应的yaml配置文件 开始创建docker
    localConfigPath = os.path.join(detailed_result_path, configName)
    return localConfigPath, configName

####
# transfer data from master node

## algorithm image
## dataset folder
## return config name
def pre_transfer_data(task_id, sftp, localConfigPath):


    with open(localConfigPath, 'r', encoding = 'utf-8') as f:
        config_dict = yaml.load(f, Loader = yaml.FullLoader)

        # copy algo and dataset

        # store the image.tar in the related algo folder


        algo_src_path = os.path.join("/SLAM-Hive/slam_hive_algos", config_dict['slam-hive-algorithm'])
        algo_dest_path = os.path.join("/slamhive/algo", config_dict['slam-hive-algorithm'])
        if os.path.exists(algo_dest_path):
            print("------algo folder already in node------")
        else:
            print("------ get algo folder ------")
            get_all_files_in_remote_dir(sftp, algo_src_path, algo_dest_path)
            os.system("docker load < " + algo_dest_path + "/image.tar")

            print("------ successful ------")


        dataset_src_path = os.path.join("/SLAM-Hive/slam_hive_datasets", config_dict['slam-hive-dataset'])
        dataset_dest_path = os.path.join("/slamhive/dataset", config_dict['slam-hive-dataset'])
        if os.path.exists(dataset_dest_path):
            print("------ dataset folder already in node------")
        else:
            print("------ get dataset folder ------")
            get_all_files_in_remote_dir(sftp, dataset_src_path, dataset_dest_path)

            print("------ successful ------")

def pre_handle_dataset(localConfigPath,configName, yaml_path):
    with open(localConfigPath, 'r', encoding = 'utf-8') as f:
        config_dict = yaml.load(f, Loader = yaml.FullLoader)


        # need to change dataset

        dataset_frequency = config_dict['dataset-frequency']
        dataset_resolution = config_dict['dataset-resolution']
        dataset_check = False

        datasetPath = os.path.join('/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset'])
        datasetPath_new = os.path.join('/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset'] + "_" + configName)

        skip_list = [config_dict['slam-hive-dataset'] + ".bag"]

        if dataset_frequency != None or dataset_resolution != None:
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
            dataset_preprocess.dataset_preprocess(dataset_bag_path_local, dataset_bag_path_local_new)
            datasetPath = datasetPath_new
        return datasetPath

