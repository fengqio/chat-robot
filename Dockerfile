FROM python:3.10.10
MAINTAINER fengqi cq4547@gmail.com
ADD . /opt/chat-bot
WORKDIR /opt/chat-bot
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
CMD ["python", "/opt/chat-bot/main.py"]