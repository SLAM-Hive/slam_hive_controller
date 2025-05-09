# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys

from typing import List

from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient


from Tea.core import TeaCore

from alibabacloud_darabonba_number.client import Client as NumberClient
from alibabacloud_darabonba_env.client import Client as EnvClient
from alibabacloud_darabonba_array.client import Client as ArrayClient


class Esc_Create:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Ecs20140526Client:
        ## def xxx() -> xxx   to mark the type of the return value
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Ecs
        config.endpoint = f'ecs.cn-zhangjiakou.aliyuncs.com'
        return Ecs20140526Client(config)


    @staticmethod
    def create_esc(
        client, disk_parameter_dict, esc_parameter_dict
    ) -> List:
        # 请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET。
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html
        client = Esc_Create.create_client(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
        system_disk = ecs_20140526_models.RunInstancesRequestSystemDisk(
            size = disk_parameter_dict['size'], ##1
            category = disk_parameter_dict['category'],  ##2
            disk_name = disk_parameter_dict['disk_name'], ##3
            performance_level = disk_parameter_dict['performance_level'], ####4
        )
        run_instances_request = ecs_20140526_models.RunInstancesRequest(
            region_id = esc_parameter_dict['region_id'], ##1
            image_id = esc_parameter_dict['image_id'], ##2
            instance_type = esc_parameter_dict['instance_type'], ##3
            security_group_id = esc_parameter_dict['security_group_id'], ##4
            v_switch_id='vsw-8vb03rdujwwm1d5qal2gy',###
            instance_name = esc_parameter_dict['instance_name'], ##5
            description = esc_parameter_dict['description'], ##6
            internet_max_bandwidth_in = esc_parameter_dict['internet_max_bandwidth_in'],##7
            internet_max_bandwidth_out = esc_parameter_dict['internet_max_bandwidth_out'],##8
            host_name = esc_parameter_dict['host_name'],##9
            password = esc_parameter_dict['password'], ## 10
            # zone_id = '',
            internet_charge_type='PayByTraffic',
            # Object, 可选,
            system_disk=system_disk,
            spot_strategy='NoSpot',
            # spot_price_limit = esc_parameter_dict['spot_price_limit'], ##11
            io_optimized='optimized',
            amount = esc_parameter_dict['amount'] , ## 13
            min_amount=1,
            instance_charge_type = esc_parameter_dict['instance_charge_type'] ##12
        )
        runtime = util_models.RuntimeOptions()
        # 1.1 buy one server: work node1
        resp = client.run_instances_with_options(run_instances_request, runtime)
        ConsoleClient.log(UtilClient.to_jsonstring(resp))

        # instance id: list[]
        return resp.body.instance_id_sets.instance_id_set

    @staticmethod
    def describe_instance_status(
        client: Ecs20140526Client,
        region_id: str,
        instance_ids: List[str],
    ) -> List[str]:
        """
        查询实例状态
        """
        request = util_models.DescribeInstanceStatusRequest(
            region_id=region_id,
            instance_id=instance_ids
        )
        ConsoleClient.log(f'实例: {instance_ids}, 查询状态开始。')
        responces = client.describe_instance_status(request)
        instance_status_list = responces.body.instance_statuses.instance_status
        ConsoleClient.log(f'实例: {instance_ids}, 查询状态成功。状态为: {UtilClient.to_jsonstring(instance_status_list)}')
        status_list = {}
        for instance_status in instance_status_list:
            status_list = ArrayClient.concat(status_list, [
                instance_status.status
            ])
        return status_list



    

