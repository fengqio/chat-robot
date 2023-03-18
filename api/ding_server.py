import base64
import hashlib
import hmac
import json
from functools import wraps

import openai
import requests
from flask import request, make_response, Flask
from flask_limiter import Limiter

from api.chat_user_context import ChatUserContext, chatWithRetry
from util.log import logger
from config import config
from flask_limiter.util import get_remote_address

app = Flask(__name__)

config_info = config.read_sys_config_path()
openai.api_key = config_info.get('open-ai', 'api_key')
openai.proxy = config_info.get('open-ai', 'proxy', fallback='')
enable_context = config_info.getboolean('open-ai', 'enable_context', fallback=False)
chat_context_size = config_info.getint('open-ai', 'chat_context_size', fallback=0)

robot_secret = config_info.get('ding-robot', 'robot_secret')
valid_sign = config_info.getboolean('ding-robot', 'valid_sign', fallback=False)
limiter = Limiter(
    key_func=lambda: request.path,
    default_limits=[config_info.get('open-ai', 'rate_limit', fallback='5 per minute')],
)

limiter.init_app(app)

contex_dict = {}

def set_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers['Content-Type'] = 'application/json'
        return resp

    return decorated_function


@app.route("/ding", methods=['post'])
@set_headers
def dingMsg():
    if not request.data:
        return {"ret": 500}
    data = json.loads(request.data.decode('utf-8'))
    logger.info(f"receive dingding message: {data}")

    if valid_sign and not is_valid_sign(request.headers):
        logger.info(f"valid sign failed")
        return {"ret": 500}

    prompt = data['text']['content']
    webhook = data['sessionWebhook']
    senderStaffId = data['senderStaffId']
    senderNick = data['senderNick']

    if enable_context:
        if senderStaffId not in contex_dict:
            context = ChatUserContext(senderStaffId, senderNick, 10)
            contex_dict[senderStaffId] = context
        else:
            context = contex_dict[senderStaffId]
        content = context.chat(prompt)
    else:
        content = chatWithRetry(senderNick, senderStaffId, [{"role": "user", "content": prompt}])
    if len(content) > 1:
        send_dingding(content, webhook, senderStaffId)
    return {"ret": 200}


@app.route("/ding/context", methods=['post'])
@set_headers
def dingContextMsg():
    data = json.loads(request.data.decode('utf-8'))
    userId = data['userId']
    userName = data['userName']
    prompt = data['text']['content']
    if userId not in contex_dict:
        context = ChatUserContext(userId, userName, 10)
        contex_dict[userId] = context
    else:
        context = contex_dict[userId]
    answer = context.chat(prompt)
    return {"answer": answer}


def send_dingding(answer, webhook, at_user_ids):
    data = {
        "msgtype": "text",
        "text": {
            "content": answer
        },
        "at": {
            "atUserIds": [
                at_user_ids
            ],
            "isAtAll": False
        }
    }
    try:
        r = requests.post(webhook, json=data)
        logger.info("send_dingding result: " + str(r.json()))
    except Exception as e:
        logger.error(e)


# timestamp = str(round(time.time() * 1000))
# secret_enc = robot_secret.encode('utf-8')
# string_to_sign = '{}\n{}'.format(timestamp, robot_secret)
# string_to_sign_enc = string_to_sign.encode('utf-8')
# hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
# sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
# notify_url = f"https://oapi.dingtalk.com/robot/send?access_token={dd_token}&timestamp={timestamp}&sign={sign}"


def is_valid_sign(headers):
    if not headers.get('timestamp') or not headers.get('sign'):
        return False
    secret_enc = robot_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(headers['timestamp'], robot_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    newSign = base64.b64encode(hmac_code)
    return headers['sign'] == newSign.decode('utf-8')


@app.errorhandler(429)
def ratelimit_handler(e):
    data = json.loads(request.data.decode('utf-8'))
    logger.info(f"receive dingding message: {data}")
    if 'sessionWebhook' in data and 'senderStaffId' in data:
        send_dingding("[一团乱麻]头好痒，好像要长出脑子了", data['sessionWebhook'], data['senderStaffId'])
    logger.info(f"ratelimit_handler error ip:{get_remote_address()}, uri:{request.path} msg: {e.description}")
    return {"ret": 429}
