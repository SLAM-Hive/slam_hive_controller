# slam_hive_controller

This is a middle controller module of SLAM Hive, using mainly in cluster and aliyun modes. This module is also used for dataset pre-processing.


Dockerfile
 - Used for docker image building
module_b_pod.yaml
 - - Used for creating a Kubernetes Pod (similar to a docker container); This container is a middle module between slam hive web and Kubernetes
project
 - core codes of controller

## project
controller_xxx_run.py
 - used to call controller_xxx.py
controller_xxx.py
 - controller_workstation
	 - used for downsample dataset
 - controller.py
	 - used in cluster mode
		 - transfer algorithm image, dataset, configs from master to work node
		 - pre-process dataset
		 - create task container in this node
		 - transfer results to master node
 - controller_aliyun.py
	 - used in aliyun mode
		 - similar to cluster mode
dataset_preprocess.py
 - used for dataset process -- data down-sample
	 - two main parts: dataset framerate and image resolution
		 - read the original rosbag
		 - handle each message according to the dataset pro-processing config
		 - write the new rosbag
