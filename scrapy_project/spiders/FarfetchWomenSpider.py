import scrapy
import logging
from scrapy_project.items import FarfetchBrandProjectItem
from urllib.parse import urlparse, parse_qs
from scrapy_project.utils import HostIP
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import json


class ProductsSimpleSpider(scrapy.Spider):
    name = 'farfetch_women'
    allowed_domains = ['farfetch.cn', 'farfetch.com']
    threads = 10
    pid= os.getpid()
    host_ip=HostIP()
    loacl_ip=host_ip.get_host_ip()
    # threads=1
    listPageUrl='https://www.farfetch.com/cn/plpslice/listing-api/products-facets?page={}&c-designer={}'

    def __init__(self,brand_id,beginPage,ver,*args,**kwargs):
        self.beginPage=beginPage
        self.currentPage=beginPage
        self.ver=ver
        self.brand_id = brand_id
        self.start_urls = [self.listPageUrl.format(self.currentPage,self.brand_id)]
        self.main_url='www.farfetch.com'
        logger.info('start_url %s',self.start_urls[0])

    def parse(self, response):
        resObj = json.loads(response.body)
        page_url= response.url
        logger.info('page_parse_url %s',page_url)
        currentPage = int(parse_qs(urlparse(response.url).query)['page'][0])
        nextPage = currentPage + self.threads
        totalPages = int(resObj['totalPages'])
        logger.debug('totalPages %s', totalPages)
        page_product_cnt = len(resObj['products'])
        if page_product_cnt == 0:
            logger.warning('此品牌无女士数据,结束此爬虫%s', page_url)
            exit()
        for i, product in enumerate(resObj['products']):
            # item = ScrapyProjectItem()
            product_info={}
            url = 'https://www.farfetch.com' + product['url']
            logger.info('第 %s 页 %s 个产品 url  %s ', self.currentPage, i, url)
            logger.info('主页面%s', page_url)
            product_info['site_name'] = 'www.farfetch.com'
            product_info['site_url'] = url
            product_info['product_id'] = product['id']
            product_info['brand_id'] = product['brand']['id']
            product_info['brand_name'] = product['brand']['name']
            product_info['product_name'] = product['shortDescription']
            product_info['initialPrice'] = product['priceInfo']['initialPrice']
            product_info['finalPrice'] = product['priceInfo']['finalPrice']
            product_info['currency_code'] = product['priceInfo']['currencyCode']
            product_info['images'] = product['images']
            product_info['sex'] = product['gender']
            product_info['page_url'] = page_url
            product_info['page_num'] = page_url.split('page=')[-1].split('&')[0]
            product_info['original_main_data'] = json.dumps(product,ensure_ascii=False)
            product_info['current_page_cnt'] = i
            product_info['merchant_id'] = product['merchantId']
            product_info['stock_total'] = product['stockTotal']
            product_info['totalPages'] = totalPages
            product_info['page_product_cnt'] = page_product_cnt
            yield scrapy.Request(url, callback=self.parseDetail,meta=product_info)

        if int(self.currentPage) < int(totalPages):

            self.currentPage=int(self.currentPage)+1
            logger.debug('farfetch_url page %s', currentPage)
            yield scrapy.Request(self.listPageUrl.format(self.currentPage,self.brand_id), callback=self.parse, headers={'Referer': ' https://www.farfetch.com/cn/shopping/women/items.aspx'})

    def parseDetail(self, response):
        product_info = response.meta
        logger.info('正在爬取第 %s 页%s 第 %s 件商品 %s url',product_info['page_num'],product_info['page_url'],product_info['current_page_cnt'],response.url)
        content = str(response.body.decode(encoding='utf-8'))
        material = ''.join(response.css('p[class="_7f3f86"]::text').getall())
        wash_care = ''.join(response.css('dd[class="_cdcda5"]::text').getall())
        shippingFromMessage = ''.join(response.css('span[data-tstid="shippingFromInformationMessage"]::text').getall())
        startKeyword = "<script>window['__initialState_slice-pdp__'] = "
        endKeyword = "</script>"
        content = content[content.find(startKeyword) + len(startKeyword):]
        content = content[:content.find(endKeyword)]
        content = content.strip()
        resObj = json.loads(content)
        page_url=response.meta.get('page_url')
        available_dic = resObj['productViewModel']['sizes']['available']
        images = resObj['productViewModel']['images']['main']
        # print(images,'>>>>>>>>>><<<<')
        img_urls = ''
        for i in images:
            img_urls = img_urls + '|' + i['zoom']
        # print(img_urls)
        for available in available_dic.values():
            item = FarfetchBrandProjectItem()
            details = resObj['productViewModel']['details']
            designerDetails = resObj['productViewModel']['designerDetails']
            item['site_name'] = product_info['site_name']
            item['site_url'] = product_info['site_url']
            item['supplier_tag'] = available['storeId']  # 供应商id
            item['origin_design_id'] = designerDetails['designerStyleId']
            item['farfetch_brand_id'] = self.brand_id
            item['brand_name'] = product_info['brand_name']
            item['product_id'] = product_info['product_id']
            item['product_name'] = product_info['product_name']
            item['qty'] = available['quantity']  # 库存
            item['initial_price'] = product_info['initialPrice']  # 初始价格
            item['final_price'] = product_info['finalPrice']  # 最终价格
            item['currency_code'] = product_info['currency_code']  # 货币编码
            item['img_url'] = img_urls  # 图片url
            item['colors'] = details['colors']
            item['size_id'] = available['sizeId']  # size_id
            item['size'] = available['description']  # 尺码描述
            specification = {}
            item['sex'] = product_info['sex']
            cleanScaleDescription = resObj['productViewModel']['sizes']['cleanScaleDescription']
            specification['sizeSyestm'] = cleanScaleDescription
            item['specification'] = json.dumps(specification, ensure_ascii=False)
            item['producer_country'] = details['madeInLabel']  # 生产国
            item['detail_desc'] = details['description']  # 设计细节
            item['material'] = material
            item['care'] = wash_care
            item['shipping_message'] = shippingFromMessage
            categories = resObj['productViewModel']['categories']
            item['category_id'] = ','.join(list(categories['all'].keys()))
            item['category'] = ','.join(list(categories['all'].values()))
            yield item
