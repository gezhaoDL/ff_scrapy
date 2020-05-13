# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import logging
import os
import csv
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import pymysql
from scrapy.exceptions import DropItem
from .items import MonitorProjectItem,FarfetchBrandProjectItem,FarfetchRawProjectItem


class MySQLTwistedPipeline(object):
    def __init__(self, pool):
        self.dbpool = pool

    @classmethod
    def from_settings(cls, mysql_conf):
        """
        这个函数名称是固定的，当爬虫启动的时候，scrapy会自动调用这些函数，加载配置数据。
        :param settings:
        :return:
        """
        params = dict(
            host='',
            port=3306,
            db='',
            user='',
            passwd='',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        #
        # params = dict(
        #     host='localhost',
        #     port=3306,
        #     db='warehouse',
        #     user='root',
        #     passwd='12345678',
        #     charset='utf8',
        #     cursorclass=pymysql.cursors.DictCursor,
        #     use_unicode=True
        # )

        # 创建一个数据库连接池对象，这个连接池中可以包含多个connect连接对象。
        # 参数1：操作数据库的包名
        # 参数2：链接数据库的参数
        db_connect_pool = adbapi.ConnectionPool('pymysql', **params)

        # 初始化这个类的对象
        obj = cls(db_connect_pool)
        return obj

    def process_item(self, item, spider):
        """
        在连接池中，开始执行数据的多线程写入操作。
        :param item:
        :param spider:
        :return:
        """
        # 参数1：在线程中被执行的sql语句
        # 参数2：要保存的数据
        if item is not None:
            result = self.dbpool.runInteraction(self.insert_main, item)
            # 给result绑定一个回调函数，用于监听错误信息
            result.addErrback(self.error)

    def error(self, reason):
        print('--------', reason)
    # 上面这两步分别是数据库的插入语句，以及执行插入语句。这里把插入的数据和sql语句分开写了，跟合在一起写效果是一样的
    def insert_main(self, cursor, item):
        logger.info('正在插入数据')
        insert_sql = '''
            insert into farfetch_brand_all_cn (
            site_name,
            site_url,
            supplier_tag,
            origin_design_id,
            farfetch_brand_id,
            brand_name,
            product_id,
            product_name,
            qty,
            initial_price,
            final_price,
            currency_code,
            img_url,
            colors,
            size,
            size_id,
            specification,
            category,
            category_id,
            sex,
            shipping_message,
            material,
            care,
            detail_desc,
            producer_country
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        cursor.execute(insert_sql, (
            str(item.setdefault('site_name','')),
            str(item.setdefault('site_url','')),
            str(item.setdefault('supplier_tag','')),
            str(item.setdefault('origin_design_id','')),
            str(item.setdefault('farfetch_brand_id','')),
            str(item.setdefault('brand_name','')),
            str(item.setdefault('product_id','')),
            str(item.setdefault('product_name','')),
            str(item.setdefault('qty','')),
            str(item.setdefault('initial_price','')),
            str(item.setdefault('final_price', '')),
            str(item.setdefault('currency_code','')),
            str(item.setdefault('img_url','')),
            str(item.setdefault('colors','')),
            str(item.setdefault('size','')),
            str(item.setdefault('size_id', '')),
            str(item.setdefault('specification', '')),
            str(item.setdefault('category', '')),
            str(item.setdefault('category_id', '')),
            str(item.setdefault('sex','')),
            str(item.setdefault('shipping_message','')),
            str(item.setdefault('material','')),
            str(item.setdefault('care','')),
            str(item.setdefault('detail_desc', '')),
            str(item.setdefault('producer_country', ''))
        ))


class CsvPipeline(object):
    def __init__(self):
        # csv文件的位置,无需事先创建
        logger.info('CsvPipeline')
        store_file_main = os.path.dirname(__file__) + '/data/farfetch/raw_data/farfetch_raw_data.csv'
        # store_file_sub = os.path.dirname(__file__) + '/spiders/farfetch_sub.csv'
        logger.info("***************************************************************")
        # 打开(创建)文件

        self.file_main = open(store_file_main, 'a+', encoding="utf-8",newline = '')
        # self.file_sub = open(store_file_sub, 'a+', encoding="utf-8",newline = '')
        # csv写法
        self.writer_mian = csv.writer(self.file_main, dialect="excel")
        # self.writer_sub = csv.writer(self.file_sub, dialect="excel")

    def process_item(self, item, spider):
        # 判断字段值不为空再写入文件
        logger.info("正在写入原始数据至csv......")
        if isinstance(item,FarfetchRawProjectItem):
            # 主要是解决存入csv文件时出现的每一个字以‘，’隔离
            #print("正在写入main......%s",item)
            self.writer_mian.writerow([
                item['site_name'],
                item['site_url'],
                item['product_id'],
                item['brand_name'],
                item['original_main_data'],
                item['resObj']])

        return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.file_main.close()
        # self.file_sub.close()


