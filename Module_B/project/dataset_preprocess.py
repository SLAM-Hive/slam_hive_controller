import rosbag, yaml
import cv2
from cv_bridge import CvBridge



def dataset_preprocess(input_bagfile, output_bagfile, yaml_path):
    bridge = CvBridge()

    # input_bagfile = '/slamhive/dataset/kitti_2011_09_30_drive_0027_synced_full/kitti_2011_09_30_drive_0027_synced.bag'
    # output_bagfile = '/slamhive/dataset/kitti_2011_09_30_drive_0027_synced_full/kitti_2011_09_30_drive_0027_synced_new.bag'

    # read topic name from yaml file
    config_raw = open(yaml_path,'r',encoding="UTF-8").read()
    config_dict = yaml.load(config_raw, Loader=yaml.FullLoader)
    dataset_frequency_dict = config_dict["dataset-frequency"]
    dataset_resolution_dict = config_dict["dataset-resolution"]
    topics_to_reduce = {}  # 需要降低频率的话题列表
    reduction_factor = []  # 降低的频率因子，例如将频率降低为原来的一半
    count = []
    t_number = 0
    if dataset_frequency_dict != None:
        for key, value in dataset_frequency_dict.items():
            topics_to_reduce.update({key: t_number})
            reduction_factor.append(value)
            count.append(0)
            t_number+=1

    # only image type
    topics_to_reduce_resolution = {}
    reduction_factor_resolution = []
    t_number = 0
    if dataset_resolution_dict != None:
        for key, value in dataset_resolution_dict.items():
            topics_to_reduce_resolution.update({key: t_number})
            reduction_factor_resolution.append(value)
            t_number += 1
        
    # topics_to_reduce_resolution = {"/kitti/camera_gray_left/image_raw":0}
    # reduction_factor_resolution = [1.0]
    print(topics_to_reduce)
    print(reduction_factor)
    print(count)
    print(topics_to_reduce_resolution)
    print(reduction_factor_resolution)

    # 打开原始bag文件和新的bag文件
    with rosbag.Bag(input_bagfile, 'r') as input_bag, rosbag.Bag(output_bagfile, 'w') as output_bag:
        # 遍历原始bag文件中的所有消息
        for topic, msg, t in input_bag.read_messages():
            # 检查话题是否需要降低频率
            if topic in topics_to_reduce.keys():
                # 检查是否需要保留该消息
                if count[topics_to_reduce[topic]] % reduction_factor[topics_to_reduce[topic]] == 0:
                    # 将满足条件的消息写入新的bag文件

                    # check if need to reduce the resolution
                    if topic in topics_to_reduce_resolution.keys():
                        original_encoding = msg.encoding  # 获取原始编码方式
                        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                        # print(reduction_factor_resolution[topics_to_reduce_resolution[topic]])
                        reduce_image = cv2.resize(cv_image, (int(cv_image.shape[1] * reduction_factor_resolution[topics_to_reduce_resolution[topic]]), int(cv_image.shape[0] * reduction_factor_resolution[topics_to_reduce_resolution[topic]])))
                        reduce_msg = bridge.cv2_to_imgmsg(reduce_image, encoding=original_encoding)
                        # print("origin msg: ", cv_image.shape[1], cv_image.shape[0])
                        # print("new msg: ", reduce_image.shape[1], reduce_image.shape[0])
                        # output_bag.write(topic, msg, t)
                        old_msg = msg
                        msg = reduce_msg


                        msg.header = old_msg.header

                        ###########################
                        # need to give timestamp
                        ###########################
                        # msg.header.stamp = t
                    output_bag.write(topic, msg, t)
                    count[topics_to_reduce[topic]] = 0
                count[topics_to_reduce[topic]] += 1
            else:
                # 对于其他话题，直接写入新的bag文件
                # also resolution check
                if topic in topics_to_reduce_resolution.keys():
                    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                    original_encoding = msg.encoding # add
                    print(original_encoding)
                    # print("sfsdsd", reduction_factor_resolution[topics_to_reduce_resolution[topic]])
                    reduce_image = cv2.resize(cv_image, (int(cv_image.shape[1] * reduction_factor_resolution[topics_to_reduce_resolution[topic]]), int(cv_image.shape[0] * reduction_factor_resolution[topics_to_reduce_resolution[topic]])))
                    reduce_msg = bridge.cv2_to_imgmsg(reduce_image, encoding=original_encoding) # add
                    # print("origin msg: ", cv_image.shape[1], cv_image.shape[0])
                    # print("new msg: ", reduce_image.shape[1], reduce_image.shape[0])
                    # output_bag.write(topic, msg, t)
                    old_msg = msg
                    msg = reduce_msg


                    msg.header = old_msg.header
                    ###########################
                    # need to give timestamp
                    ###########################
                    # msg.header.stamp = t
                    # 可能会导致导致丢失frameid 以及 stamp好像有点问题
                output_bag.write(topic, msg, t)
    #$ 在上述代码中，你需要将input.bag替换为原始bag文件的路径，output.bag替换为新的bag文件的路径


def dataset_preprocess1(input_bagfile, output_bagfile, yaml_path):
    bridge = CvBridge()

    # input_bagfile = '/slamhive/dataset/kitti_2011_09_30_drive_0027_synced_full/kitti_2011_09_30_drive_0027_synced.bag'
    # output_bagfile = '/slamhive/dataset/kitti_2011_09_30_drive_0027_synced_full/kitti_2011_09_30_drive_0027_synced_new.bag'

    # read topic name from yaml file
    config_raw = open(yaml_path,'r',encoding="UTF-8").read()
    config_dict = yaml.load(config_raw, Loader=yaml.FullLoader)
    dataset_frequency_dict = config_dict["dataset-frequency"]
    dataset_resolution_dict = config_dict["dataset-resolution"]
    topics_to_reduce = {}  # 需要降低频率的话题列表
    reduction_factor = []  # 降低的频率因子，例如将频率降低为原来的一半
    count = []
    t_number = 0
    if dataset_frequency_dict != None:
        for key, value in dataset_frequency_dict.items():
            topics_to_reduce.update({key: t_number})
            reduction_factor.append(1 / value)
            count.append(0)
            t_number+=1

    # only image type
    topics_to_reduce_resolution = {}
    reduction_factor_resolution = []
    count_resolution = []
    t_number = 0
    if dataset_resolution_dict != None:
        for key, value in dataset_resolution_dict.items():
            topics_to_reduce_resolution.update({key: t_number})
            reduction_factor_resolution.append(value)
            t_number += 1
        

    print(topics_to_reduce)
    print(reduction_factor)
    print(count)
    print(topics_to_reduce_resolution)
    print(reduction_factor_resolution)

    # 打开原始bag文件和新的bag文件
    with rosbag.Bag(output_bagfile, 'r') as input_bag:
        min_width = 9999
        min_height = 9999
        # 遍历原始bag文件中的所有消息
        for topic, msg, t in input_bag.read_messages():
            # 检查话题是否需要降低频率
                # 检查是否需要保留该消息
                # 将满足条件的消息写入新的bag文件

                # check if need to reduce the resolution
            if topic in topics_to_reduce_resolution.keys():
                cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                print(cv_image.shape[1], cv_image.shape[0])
                min_width = min(min_width, cv_image.shape[1])
                min_height = min(min_height, cv_image.shape[0])

                print(min_width,min_height)
         
def dataset_preprocess2(input_bagfile, output_bagfile, yaml_path):
    bridge = CvBridge()


    # 打开原始bag文件和新的bag文件
    with rosbag.Bag(input_bagfile, 'r') as input_bag, rosbag.Bag(output_bagfile, 'w') as output_bag:
        # 遍历原始bag文件中的所有消息
        for topic, msg, t in input_bag.read_messages():
            # 检查话题是否需要降低频率

            output_bag.write(topic, msg, t)
    #$ 在上述代码中，你需要将input.bag替换为原始bag文件的路径，output.bag替换为新的bag文件的路径

def dataset_preprocess3(input_bagfile, output_bagfile, yaml_path):
    bridge = CvBridge()


    # 打开原始bag文件和新的bag文件
    with rosbag.Bag(input_bagfile, 'r') as input_bag:
        # 遍历原始bag文件中的所有消息
        min_w = 9999
        min_h = 9999
        for topic, msg, t in input_bag.read_messages():
            # 检查话题是否需要降低频率
            if topic == "/kitti/camera_gray_left/image_raw":
                cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                # saveFile = "/SLAM-Hive/slam_hive_datasets/kitti_2011_09_30_drive_0027_synced_full/" + str(cc) + ".png"
                # cv2.imwrite(saveFile, cv_image)  # 保存图像文件

                # check timestamp
                print(cv_image.shape[1], cv_image.shape[0])
                min_w = min(min_w, cv_image.shape[1])
                min_h = min(min_h, cv_image.shape[0])
        print(min_w, min_h)
                    
            
    #$ 在上述代码中，你需要将input.bag替换为原始bag文件的路径，output.bag替换为新的bag文件的路径


# test image
# input_bagfile = "/SLAM-Hive/slam_hive_datasets/MH_01_easy/MH_01_easy.bag"
# output_bagfile = "/SLAM-Hive/slam_hive_datasets/MH_01_easy_test_encoding/MH_01_easy.bag"

# input_bagfile = "/dataset/MH_01_easy.bag"
# output_bagfile = "/dataset/MH_01_easy_new.bag"

# input_bagfile = "/SLAM-Hive/slam_hive_datasets/MH_01_easy/MH_01_easy.bag"
# output_bagfile = "/SLAM-Hive/slam_hive_datasets/MH_01_easy/MH_01_easy_new.bag"

# yaml_path = "test.yaml"
# dataset_preprocess(input_bagfile, output_bagfile, yaml_path)#