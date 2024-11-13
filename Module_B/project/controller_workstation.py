import dataset_preprocess
import yaml, sys, shutil, os

f1 = open("/slamhive/dataset_change_config.yaml", 'r')
content = f1.read()
datasetPath_local = content.split('\n')[0]
datasetPath_local_new = content.split('\n')[1]
f1.close()

with open("/slamhive/config.yaml", 'r', encoding = 'utf-8') as f:
    config_dict = yaml.load(f, Loader = yaml.FullLoader)
    # datasetPath = os.path.join('/SLAM-Hive-Test/SLAM-Hive/slam_hive_datasets', config_dict['slam-hive-dataset']) # 数据集的路径（主机下）
    dataset_frequency = config_dict['dataset-frequency']
    dataset_resolution = config_dict['dataset-resolution']
    dataset_check = False

    skip_list = [config_dict['slam-hive-dataset'] + ".bag"]

    if dataset_frequency != None or dataset_resolution != None:
        dataset_check = True
        if not os.path.exists(datasetPath_local_new):
            # 如果目标路径不存在原文件夹的话就创建
            os.makedirs(datasetPath_local_new)
        if os.path.exists(datasetPath_local):
            # 如果目标路径存在原文件夹的话就先删除
            shutil.rmtree(datasetPath_local_new)
        shutil.copytree(datasetPath_local, datasetPath_local_new, ignore = shutil.ignore_patterns(*skip_list))
        dataset_bag_path_local = datasetPath_local + "/" + config_dict['slam-hive-dataset'] + ".bag"
        dataset_bag_path_local_new = datasetPath_local_new + "/" + config_dict['slam-hive-dataset'] + ".bag"
        dataset_preprocess.dataset_preprocess(dataset_bag_path_local, dataset_bag_path_local_new, '/slamhive/config.yaml')
        
        f = open(datasetPath_local_new + "/finished", "w")
        f.close()
        # finished flag