# chat-robot

钉钉chat-gpt机器人



## 快速开始

需要准备的：

 	1. 申请一个**OpenAi API key**, 从[openai platform](https://platform.openai.com/account/api-keys) 生成
 	2. 设置钉钉机器人
     - 登录钉钉开放平台，创建机器人
     - 设置钉钉机器人消息接收地址
     - [可选] 获取钉钉机器人 AppSecret，用于校验钉钉请求



## 部署服务

python 版本最低需要 3.9.x

```python
# 安装依赖
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

配置 config.ini

```ini
[server]
port = 8080
[open-ai]
api_key = your openai api key
proxy = http proxy if need
# 限流，默认 15 per minute
rate_limit = 
[ding-robot]
# 可选，是否校验钉钉消息中的 sign，开启校验需配置 robot_secret，值为钉钉机器人 AppSecret
valid_sign = True or False
robot_secret = robot app secret
```

