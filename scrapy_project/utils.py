# -*- coding: utf-8 -*-

import requests
import logging
import time
import json
import datetime
import hmac
import hashlib
import base64
import urllib
import socket
# logging.getLogger("requests").setLevel(logging.INFO)
import logging
from dingtalkchatbot.chatbot import DingtalkChatbot
import random
#LOG_FORMAT = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
#logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info('>>>>>>>>>>>>>>>>>>')

username = ""
password = ""
api_key = ''
order_id = ''
api_url = "".format(order_id)
access_token = ''

secret = ''

webhook='https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'

class HostIP:
    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


def get_proxies():
    try_times = 0
    proxy_ip = ''
    proxies = ''
    status_code = -1
    while try_times < 20:
        r = requests.get(api_url)
        status_code = r.status_code
        # status_code=-1
        if status_code != 200:
            try_times = try_times + 1
            logger.error("fail to get proxy %s times,try again", try_times)
            continue
        try:
            json_data= r.json()['data']
            proxy_ip = json_data['proxy_list'][0]
            today_left_count= json_data['today_left_count']
            #today_left_count= 51
            if int(today_left_count) <= 50:
                will_start_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:10")
                rand_sec= random.randint(1,60)
                sleep_time = (datetime.datetime.strptime(will_start_time, "%Y-%m-%d %H:%M:%S")-datetime.datetime.now()).seconds + rand_sec

                host_name, ip_address = print_machine_info()
                msg = 'host_name {} ip_address {}  代理IP 剩余量小于 {} ,程序即将休眠 {} 秒'.format(host_name,ip_address,today_left_count,sleep_time)
                logger.warning('IP 剩余 %s, 即将休眠 %s 秒',today_left_count,sleep_time)
                dingdingmessage(msg, secret, webhook)
                time.sleep(sleep_time)
                start_msg = '程序启动'
                dingdingmessage(start_msg, secret, webhook)
                continue
            proxies = {
                "https": "https://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': proxy_ip}
            }
        except Exception as e:
            host_name, ip_address = print_machine_info()
            msg = 'hostname:{} ip:{} 错误 {} ip耗尽或者请求过快, 重试次数 {}'.format(host_name, ip_address, e, try_times)
            dingdingmessage(msg, secret, webhook)
            time.sleep(60)
            continue
        break
    if status_code == 200:
        logger.info('get proxy_ip %s ', proxy_ip)
        return proxies, proxy_ip
    else:
        logger.error('fail to get proxy 10 times ')
        raise Exception('fail to get proxy 10 times ')


def check_valid_time(ip):
    check_url = 'https://dps.kdlapi.com/api/getdpsvalidtime?orderid={}&signature={}&proxy={}'.format(order_id, api_key, ip)
    logger.debug('check_url %s', check_url)
    r = requests.get(check_url)
    if r.status_code != 200:
        logger.error("fail to get proxy")
        return -1
    r.enconding = "utf-8"  # 设置返回内容的编码
    r_data=json.loads(r.content.decode())
    valid_time = r_data['data'][ip]
    return valid_time


def get_valid_proxies(ip):
    logger.info('获取ip 有效时间 %s ', ip)
    while True:
        valid_time = check_valid_time(ip)
        if valid_time != -1:
            break
        else:
            time.sleep(0.5)
    logger.info('ip有效时间 %s %s', ip, valid_time)
    if valid_time > 10:
        proxies = {
            "https": "https://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': ip}
        }
        return proxies, ip
    else:
        proxies, proxy_ip = get_proxies()
        logger.info('切换新ip %s 成功', proxy_ip)
        return proxies, proxy_ip


def get_valid_ip(ip):
    logger.info('获取ip 有效时间 %s ', ip)
    while True:
        valid_time=check_valid_time(ip)
        if valid_time != -1:
            break
        else:
            time.sleep(0.5)
    logger.info('ip有效时间 %s %s', ip, valid_time)
    if valid_time > 10:
        return ip
    else:
        proxies, proxy_ip = get_proxies()
        logger.info('切换新ip %s 成功', proxy_ip)
        return proxy_ip


def dingdingmessage(msg, secret, webhook, is_at_all=False):
    timestamp = round(time.time() * 1000)
    secret = secret
    secret_enc = secret.encode(encoding='utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode(encoding='utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    webhook = webhook.format(access_token, timestamp, sign)
    xiaoding = DingtalkChatbot(webhook)
    cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg_format = '{} {}'.format(cur_time, msg)
    xiaoding.send_text(msg=msg_format, is_at_all=is_at_all)


def print_machine_info():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return host_name, ip_address


if __name__ == '__main__':
    proxies, proxy_ip = get_proxies()
    print('proxy_ip', proxy_ip)
    # time.sleep(2)
    # proxies,proxy_ip = get_proxies()
    # print('proxy_ip',proxy_ip)
    # for i in range(10):
    #     proxy_ip = get_valid_proxies(proxy_ip)
    #     print('proxy_ip {} {}'.format(i,proxy_ip))
