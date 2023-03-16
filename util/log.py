import logging
from logging.config import dictConfig

logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
                  '%(asctime)s %(levelname)-8s %(module)-12s[%(lineno)d] %(message)s'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG},
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'f',
            'filename': './chat-bot.log',
            'mode': 'a',
            'level': logging.DEBUG}

    },
    root={
        'handlers': ['h', 'file'],
        'level': logging.INFO,
    },
)

dictConfig(logging_config)
logger = logging.getLogger()

#
# formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)-12s[%(lineno)d] %(message)s')
#
# logFile = './chat-bot.log'
# # 创建一个FileHandler,并将日志写入指定的日志文件中
# fileHandler = logging.FileHandler(logFile, mode='a')
# fileHandler.setLevel(logging.INFO)
# fileHandler.setFormatter(formatter)
#
# # 或者创建一个StreamHandler,将日志输出到控制台
# streamHandler = logging.StreamHandler()
# streamHandler.setLevel(logging.INFO)
# streamHandler.setFormatter(formatter)
#
# # 定义日志滚动条件，这里按日期-天保留日志
# timedRotatingFileHandler = handlers.TimedRotatingFileHandler(filename=logFile, when='D')
# timedRotatingFileHandler.setLevel(logging.INFO)
# timedRotatingFileHandler.setFormatter(formatter)
#
# # 添加Handler
# logger.addHandler(fileHandler)
# logger.addHandler(streamHandler)
# logger.addHandler(timedRotatingFileHandler)
