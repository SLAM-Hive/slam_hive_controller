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


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Ecs20140526Client:
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
    def create_client_with_sts(
        access_key_id: str,
        access_key_secret: str,
        security_token: str,
    ) -> Ecs20140526Client:
        """
        使用STS鉴权方式初始化账号Client，推荐此方式。
        @param access_key_id:
        @param access_key_secret:
        @param security_token:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret,
            # 必填，您的 Security Token,
            security_token=security_token,
            # 必填，表明使用 STS 方式,
            type='sts'
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Ecs
        config.endpoint = f'ecs.cn-zhangjiakou.aliyuncs.com'
        return Ecs20140526Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        # 请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET。
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html
        client = Sample.create_client(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
        create_image_request = ecs_20140526_models.CreateImageRequest(
            region_id='cn-zhangjiakou',
            instance_id='111',
            image_name='task_xxx',
            description='description of the image',
            platform='Ubuntu',
            architecture=''
        )
        runtime = util_models.RuntimeOptions()
        resp = client.create_image_with_options(create_image_request, runtime)
        ConsoleClient.log(UtilClient.to_jsonstring(resp))

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        # 请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET。
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html
        client = Sample.create_client(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
        create_image_request = ecs_20140526_models.CreateImageRequest(
            region_id='cn-zhangjiakou',
            instance_id='111',
            image_name='task_xxx',
            description='description of the image',
            platform='Ubuntu',
            architecture=''
        )
        runtime = util_models.RuntimeOptions()
        resp = await client.create_image_with_options_async(create_image_request, runtime)
        ConsoleClient.log(UtilClient.to_jsonstring(resp))


if __name__ == '__main__':
    Sample.main(sys.argv[1:])
