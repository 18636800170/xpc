import logging

import requests
from celery import Celery

SMS_API = 'http://sms-api.luosimao.com/v1/send.json'
SMS_USER = 'api'
SMS_KEY = 'd4c73a2afa7864d061e8d8e9a11a5f19'
SMS_API_AUTH = (SMS_USER, "key-%s" % SMS_KEY)
# 使用ｓｅｌｅｒｙ实现异步加载
app = Celery("tasks", broker="redis://127.0.0.1")
logger = logging.getLogger(__name__)


@app.task
def send_sms_code(phone, code):
    logger.info("task start ...")
    message = "您的验证码是：%s，请在十分钟之内输入此验证码。【千锋教育】" % code
    requests.post(SMS_API, data={
        "mobile": phone,
        "message": message,
    }, auth=SMS_API_AUTH)
    logger.info("send sms to %s :%s" % (phone, message))
