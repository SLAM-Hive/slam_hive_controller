from aliyun_tools import Esc_Create
import os

if __name__ == '__main__':

    #### 假设：
    # 主服务器以后部署成功，现在的操作是在主服务器上（先买一个周的服务器）
    # 部署好 docker + kubernetes（注意版本）
    # 做好一系列限制条件（见文档）
    # 1个数据集 + 1个算法镜像 （先在本地跑通这个实验）
    # 同时构建g一个image，用于后续的移植
    # 已经j创建好了work node 的初始镜像

    #### 1. 准备好流程所需要的全部参数
    client = Esc_Create.create_client(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
    # 1.1 master node相关：region（cn-zhangjiakou）；局域网IP；
    MASTER_REGION = "cn-zhangjiakou"
    MASTER_IP = ""
    # 1.2 账号相关：可用区，交换机（这些暂时写死成zhangjiakou，在账号中提前创建好了这些地域的交换机）
    # 1.3 work node相关：购买数量；局域网IP；型号（暂时写死，后续可以提供选择功能）
    # 1.4 计算得到所需要购买的work node的数量，以及每个task所在的node
    

    #### 2. 购买1个work node
    # 2.1 根据上述的参数，购买一个work node
    # 2.2 等待节点运行就绪
    # 2.3 master noden将：algo image、dataset、config等通过局域网传输到work node1
    # 2.4 加入master node所在的kubernetes集群
    # 2.5 生成镜像
    # 2.6 开始task

    #### 3. 购买 其余n-1个 work node
    # 3.1 依据2.5生成的image，创建剩余的work node
    # 3.2 等待节点运行就绪
    # 3.3 加入集群
    # 3.4 开始task

    #### 4. 将结果回传给master node
    # 4.1 结束

    # Esc_Create.main(sys.argv[1:])

    # prepare: check the number that can buy

    disk_temp_dict = {}
    disk_temp_dict.update({"size": 64})
    disk_temp_dict.update({"category": 'cloud_essd'})
    disk_temp_dict.update({"disk_name": 'system_disk'})
    disk_temp_dict.update({"performance_level": 'PL1'})

    instance_temp_dict = {}
    instance_temp_dict.update({"region_id": 'cn-zhangjiakou'})
    instance_temp_dict.update({"image_id": 'ubuntu_20_04_x64_20G_alibase_20230718.vhd'})
    instance_temp_dict.update({"instance_type": 'ecs.u1-c1m1.2xlarge'})
    instance_temp_dict.update({"security_group_id": 'sg-8vbe4qm8ujcshr9xsqjm'})
    instance_temp_dict.update({"instance_name": 'slam-hive_first_test_1_[1,2]'})
    instance_temp_dict.update({"description": 'slam-hive_first_test_1'})
    instance_temp_dict.update({"internet_max_bandwidth_in": 1})
    instance_temp_dict.update({"internet_max_bandwidth_out": 1})
    instance_temp_dict.update({"host_name": 'task-1-[1,2]'})
    instance_temp_dict.update({"password": 'slam-hive1'})
    instance_temp_dict.update({"internet_charge_type": 'PayByTraffic'})
    instance_temp_dict.update({"spot_strategy": 'NoSpot'})
    # instance_temp_dict.update({"spot_price_limit": 5.0})
    instance_temp_dict.update({"instance_charge_type": 'PostPaid'})
    instance_temp_dict.update({"amount": 2})
    instance_temp_dict.update({"v_switch_id": "vsw-8vb03rdujwwm1d5qal2gy"})
    # pass a dict, containing the required paramter (4 + 13)
    
    # 1.1 buy one server: work node1 & 1.2 get the id of the work node 1
    
    instance_id_list = []
    instance_id_list = Esc_Create.create_esc(client, disk_temp_dict, instance_temp_dict)
    print("--- buy result ---")
    print(instance_id_list)

    # # 1.3 waiting for the start of the work node 1
    # # import time
    # # while True:
    # instance_status_list = Esc_Create.describe_instance_status(client, instance_temp_dict['region_id'], instance_id_list)
    # #     time.sleep(1)
    # print("--- instance status ---")
    # print(instance_status_list)

