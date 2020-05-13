# -*- coding: utf-8 -*-
import os
import pandas as pd
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import subprocess
import time
import hmac
import hashlib
import base64
import urllib
import socket
# from dingtalkchatbot.chatbot import DingtalkChatbot
import datetime
import socket
import logging
log_format = '%(asctime)s[%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger()

access_token = ''
secret = ''
webhook = ''
mysql_conf = {}


def print_machine_info():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return host_name, ip_address


class Shell(object):
    def runCmd(self, cmd, stdout=subprocess.PIPE):
        res = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=subprocess.STDOUT)
        sout, serr = res.communicate()
        return res.returncode, sout, serr, res.pid


def hive_sql_exeute(sql):
    shell = Shell()
    hive_sql = '''hive -e ''' + ''' " ''' + sql + '''  " '''
    logger.info('hive_sql %s', hive_sql)
    result = shell.runCmd(hive_sql)

    if result[0] == 0:
        print(result[1])
        if 'Time taken' in str(result[1]):
            logger.info('执行成功')
            return 0
        else:
            raise Exception('执行失败.', result[1])

    else:
        raise Exception('执行失败')


def read_mysql_table(mysql_conf, read_sql):
    engine = create_engine(
        'mysql://' + mysql_conf['username'] + ':' + mysql_conf['password'] + '@' + mysql_conf[
            'host'] + '/' + mysql_conf['database_name'] + '?charset=UTF8MB4', echo=False)
    sql_cmd = read_sql
    mysql_table = pd.read_sql(sql_cmd, con=engine)
    return mysql_table


def load_csv_to_hive(path, tablename, dt, hour=None):
    load_file_cmd_hour = ''' load data local inpath '{}' overwrite into table {} partition(dt='{}',hour='{}') '''
    load_file_cmd_day = ''' load data local inpath '{}' overwrite into table {} partition(dt='{}') '''
    if hour is not None:
        cmd = load_file_cmd_hour.format(path, tablename, dt, hour)
    else:
        cmd = load_file_cmd_day.format(path, tablename, dt)
    hive_sql_exeute(cmd)


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


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def print_machine_info():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return host_name,ip_address

if __name__ == '__main__':
    host_name,ip_address=print_machine_info()
    msg='host_name:{},ip:{}'.format(host_name,ip_address)
    logger.info('msg %s',msg)
    dingdingmessage(msg, secret, webhook)

