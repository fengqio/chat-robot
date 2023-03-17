import base64
import hashlib
import hmac
import json
from functools import wraps

import openai
import requests
from flask import request, make_response, Flask
from flask_limiter import Limiter
from util.log import logger
from config import config
from flask_limiter.util import get_remote_address

app = Flask(__name__)
model_engine = "gpt-3.5-turbo"
retry_times = 2

config_info = config.read_sys_config_path()
openai.api_key = config_info.get('open-ai', 'api_key')
openai.proxy = config_info.get('open-ai', 'proxy')
robot_secret = config_info.get('ding-robot', 'robot_secret')
valid_sign = config_info.getboolean('ding-robot', 'valid_sign')
limiter = Limiter(
    key_func=lambda: request.path,
    default_limits=[config_info.get('open-ai', 'rate_limit')],
)

limiter.init_app(app)


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
    logger.info(f"senderStaffId:{senderStaffId} senderNick:{senderNick} content:{prompt}")
    content = ''
    for i in range(retry_times):
        try:
            completion = openai.ChatCompletion.create(
                model=model_engine,
                messages=[{"role": "user", "content": prompt}],
            )
            content = completion.choices[0].message.content
            break
        except Exception as e:
            logger.info(f"failed retry, msg:{e.user_message}")
            continue

    logger.info(f"receive chat-gpt response: {content}")
    if len(content) > 1:
        send_dingding(content, webhook, senderStaffId)
    return {"ret": 200}


def send_dingding(answer, webhook, atUserIds):
    data = {
        "msgtype": "text",
        "text": {
            "content": answer
        },
        "at": {
            "atUserIds": [
                atUserIds
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
    timestamp = headers.get('timestamp')
    sign = headers.get('sign')
    if not timestamp or not sign:
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
