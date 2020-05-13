# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from collections import OrderedDict
from scrapy import Item
# import six

import scrapy


class FarfetchBrandProjectItem(scrapy.Item):
    site_name = scrapy.Field()
    site_url = scrapy.Field()
    supplier_tag = scrapy.Field()
    origin_design_id = scrapy.Field()
    farfetch_brand_id = scrapy.Field()
    brand_name = scrapy.Field()
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    qty = scrapy.Field()
    initial_price = scrapy.Field()
    final_price = scrapy.Field()
    currency_code = scrapy.Field()
    img_url = scrapy.Field()
    colors = scrapy.Field()
    size = scrapy.Field()
    size_id = scrapy.Field()
    specification = scrapy.Field()
    category = scrapy.Field()
    category_id = scrapy.Field()
    sex = scrapy.Field()
    shipping_message = scrapy.Field()
    material = scrapy.Field()
    care = scrapy.Field()
    detail_desc = scrapy.Field()
    producer_country = scrapy.Field()



