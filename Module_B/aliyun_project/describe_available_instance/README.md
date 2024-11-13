# 查询某一可用区的资源列表文档示例

该项目为调用DescribeAvailableResource查询某一可用区的资源列表。您可以在某一可用区创建实例（RunInstances）或者修改实例规格（ModifyInstanceSpec）时查询该可用区的资源列表。文档示例，该示例**无法在线调试**，如需调试可下载到本地后替换 [AK](https://usercenter.console.aliyun.com/#/manage/ak) 以及参数后进行调试。

## 运行条件

- 下载并解压需要语言的代码;

- 在阿里云帐户中获取您的 [凭证](https://usercenter.console.aliyun.com/#/manage/ak)并通过它替换下载后代码中的 ACCESS_KEY_ID 以及 ACCESS_KEY_SECRET;

- 执行对应语言的构建及运行语句

## 执行步骤
下载的代码包，在根据自己需要更改代码中的参数和 AK 以后，可以在**解压代码所在目录下**按如下的步骤执行

- Java
*JDK 版本要求 1.8*
```sh
mvn clean package
java -jar target/sample-1.0.0-jar-with-dependencies.jar
```

- TypeScript
*Node 版本要求 10.x 及以上*
```sh
npm install --registry=https://registry.npm.taobao.org && tsc && node ./dist/client.js
```

- Go
*Golang 版本要求 1.13 及以上*
```sh
GOPROXY=https://goproxy.cn,direct go run ./main
```

- PHP
*PHP 版本要求 7.2 及以上*
```sh
composer install && php src/Sample.php
```

- Python
*Python 版本要求 Python3*
```sh
python3 setup.py install && python ./alibabacloud_sample/sample.py
```

- C#
*.NETCORE 版本要求 2.1及以上*
```sh
cd ./core && dotnet run
```

## 使用的 API

-  DescribeAvailableResource 调用DescribeAvailableResource查询某一可用区的资源列表。您可以在某一可用区创建实例（RunInstances）或者修改实例规格（ModifyInstanceSpec）时查询该可用区的资源列表。文档示例，可以参考：[文档](https://next.api.aliyun.com/document/Ecs/2014-05-26/DescribeAvailableResource)



## 返回示例

*实际输出结构可能稍有不同，属于正常返回；下列输出值仅作为参考，以实际调用为准*


- JSON 格式 
```js
{
	"RequestId": "0041D94C-FB92-4C49-B115-259DA1CE1923",
	"AvailableZones": {
		"AvailableZone": [
			{
				"Status": "Available",
				"RegionId": "cn-hangzhou",
				"AvailableResources": {
					"AvailableResource": [
						{
							"Type": "InstanceType",
							"SupportedResources": {
								"SupportedResource": [
									{
										"Status": "Available",
										"Value": "ecs.g5.large",
										"StatusCategory": "WithStock"
									}
								]
							}
						}
					]
				},
				"ZoneId": "cn-hangzhou-i",
				"StatusCategory": "WithStock"
			}
		]
	}
}
```
- XML 格式 
```xml
<DescribeAvailableResourceResponse>
    <RequestId>0041D94C-FB92-4C49-B115-259DA1CE1923</RequestId>
    <AvailableZones>
        <AvailableZone>
            <Status>Available</Status>
            <RegionId>cn-hangzhou</RegionId>
            <AvailableResources>
                <AvailableResource>
                    <Type>InstanceType</Type>
                    <SupportedResources>
                        <SupportedResource>
                            <Status>Available</Status>
                            <Value>ecs.g5.large</Value>
                            <StatusCategory>WithStock</StatusCategory>
                        </SupportedResource>
                    </SupportedResources>
                </AvailableResource>
            </AvailableResources>
            <ZoneId>cn-hangzhou-i</ZoneId>
            <StatusCategory>WithStock</StatusCategory>
        </AvailableZone>
    </AvailableZones>
</DescribeAvailableResourceResponse>
```


