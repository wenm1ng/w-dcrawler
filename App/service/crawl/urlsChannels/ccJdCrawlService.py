# coding: utf-8
import html
import re, os.path, time, urllib.parse

import demjson
from App.common.webRequest import WebRequest
from Configs import defaultApp
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from scrapy.selector import Selector
from App.common.url.baseUrlHandle import baseUrlHandle
import gevent
from App.service.system.classContextService import classContextService

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import json
from lxml import etree
import hashlib
import datetime
import requests
import itertools
from functools import reduce

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def filliter(infolist):
    infolist = [x.strip() for x in infolist if x.strip() != '']
    return infolist


def get_sku_mapping(HTML):
    sku_mapping = []
    skulist = re.search('.*?colorSize: (\[.*?\]),', HTML)
    if skulist:
        sku_mapping = json.loads(skulist.group(1))
    else:
        pass
    return sku_mapping


def get_jd_price(skuid):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    try:
        resp = requests.get('https://p.3.cn/prices/mgets?skuIds=J_{}'.format(skuid), headers=headers)
        print(resp.text)
        price_data = json.loads(resp.text)[0]
        jd_price = price_data['p']
    except:
        jd_price = ""

    return jd_price


def get_desc(url):
    if not url:
        return ''
    desc = ''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'downlink': '10',
        'ect': '4g',
        'rtt': '50',
        'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
    }
    try:
        desc = requests.get(url, headers=headers, timeout=5).text
    except Exception as e:
        print(33, e)
        pass
    return desc


class ccJdCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Jd'

    """
     # 设置对象
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:56:10
    """

    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        if not self.relayServiceClass:
            self.relayServiceClass = relayServiceClass

    """
     # 获取数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def appendCurlRequest(self):
        urls = classContextService().getVarByName(name=self.relayServiceClass.__class__.__name__ + '_originalUrls')
        if urls:
            if self.channleName not in urls.keys():
                return
            for url in urls[self.channleName]:
                if url not in urls[self.channleName]:
                    continue
                self.saveHtmlResult(urls[self.channleName][url])

    """
     # 获取数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def appendExtendCurlRequest(self):
        return

    """
     # 保存文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月16日 10:11:43
    """

    def saveHtmlResult(self, url):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()
        itemid = re.search('https://item.jd.com/(\d+).html.*?', url).group(1)
        md5str = hashlib.md5(itemid.encode(encoding='UTF-8')).hexdigest()
        itemid_validity = commonRedisClass.zscoreValByKey('jd_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.soukuan_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/jd_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='jd_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return

        header = {
        }
        for useType in '01122':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['cookie'] = '__jda=122270672.1632795304018887328063.1632795304.1632795304.1632795304.1; __jdv=122270672^|direct^|-^|none^|-^|1632795304019; __jdc=122270672; __jdu=1632795304018887328063; shshshfp=1e5b4ffbc25025e4958e015e145c249b; shshshfpa=2f7c03c7-0714-0944-4cb4-4fec0580b935-1632795304; areaId=19; shshshfpb=o7NWhOLZHjYxr4isVwOoxcQ^%^3D^%^3D; ipLoc-djd=19-1607-4773-62121; __jdb=122270672.4.1632795304018887328063^|1.1632795304; shshshsID=09ee86607e62746110b20639273db5f0_4_1632795574544; 3AB9D23F7A4B3C9B=3PX3FEN7GCIXXXNB672ES33IGBQO5UC5EPGC2F7DIGQ7B2PREJESQOYE46KCTPIOGVGYJNZK6XPHKR5ZZD24FDUE4U; token=ad0b37fa5b812085a2cbd10a39010078,2,907108; __tk=ZcYTXpXFXpk5YDuyYzJyuDXzYpvTZsuFYsXzYzn3Xz2yvSinvciTXk,2,907108'
            header['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            # header['cookie'] = 'shshshfp=c1eea22b83fdff17b4822ad76a860cd9; shshshfpa=46cca4e7-1f18-cbbc-e992-ac0822738b11-1632793462; __jdv=122270672|direct|-|none|-|1632793462575; __jda=122270672.16327934625751760755734.1632793463.1632793463.1632793463.1; __jdc=122270672; __jdu=16327934625751760755734; shshshfpb=a96tUApAs8Mexxv4b12PyIg%3D%3D; areaId=19; ipLoc-djd=19-1607-4773-62121; token=b0a9a2e5b3f557bc67d90e541d95d587,2,907107; wlfstk_smdl=d5vrdr8818npvzi9e0td7bybcsvew039; __tk=kzjwkce1kcuTlUBhlcaDjUkoJUkpJUt5kDa5jibpJUSyIsJoJUG5kS,2,907107; __jdb=122270672.5.16327934625751760755734|1.1632793463; shshshsID=51e10e78d38a2a4add96a7bb76ed5dbd_3_1632794085573; 3AB9D23F7A4B3C9B=YWQCCGW52TMXE5LJBXE4NR3DPER3LZMEX4XYXJRRNSXDWRDPOWJSFF6NFNPQJNEDKEUMDXWY6K4JXLXS5BCURXIAJ4'
            header['user-agent'] = userAgent().getPc()

            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)

                html = result.text(self=WebRequest)
                if len(html)<500:
                    continue
                data = self.setResult(html, url)  # 洗完的结构
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                commonElasticSearchClass.insertDataByIndexKey(index='jd_info', id=md5str, data=data)
                commonRedisClass.insertDataByIndexKey(redisKeyName='jd_info', redisStr=md5str)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
            except Exception as e:
                print(e)

    """
     # 判断是否为真实连接
     # @param self
     # @param htmlText 抓取页面
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月20日 16:19:15
    """

    def isTrueHtml(self, htmlText, url):
        print(url)
        result = False
        if not htmlText:
            return result
        resultTextSelector = etree.HTML(htmlText)
        if not resultTextSelector:
            return result
        productTitle = resultTextSelector.xpath('/html/head/title/text()')[0]
        print(productTitle)
        if productTitle:
            return True

    """
     # 当前url的数据保存至文件
     # @param self
     # @return string
     # @author     foolminx    foolminx@163.com
     # @date    2020-01-21 14:43:25
    """

    def setUrlsResult(self, url, company_code, user_id):
        return

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):
        print(url)
        data = {
            'base': {
                "productId": "",
                "title": "",
                "brand": '',
                "sourceUrl": "",
                "site": "",
                "currency": "CNY",
                "price": "",
                "priceRange": "",
                "siteLanguage": "zh",
                "business_years": 0,  # 商家年限
                "location": "",  # 地区
                "contact_seller": "",  # 联系卖家
                "goods_description": "",  # 货描
                "return_rate": "",  # 回头率
                "goods_deliver": "",  # 发货
                "response": "",  # 响应
                "management_model": "",  # 经营模式
                "supply_level": "",  # 供应等级
                "sales": "",  # 销量
                "collection_volume": "",  # 收藏量
                "praise_rate": "",  # 好评率
                "product_rating": "",  # 商品评分
                "comments_number": 0,  # 评论数量
                "quantity": "",
                "mall_id": "",
                "mall_link": "",
                "mall_name": "",
                "weight_value": '',  # 重量值
                "weight_unit": '',  # 重量单位
                "size": ''  # 尺寸
            },
            'extra_data': [],
            'images': [],
            'attributes': [],
            'variableList': [],
            'is_valid': '',
            'extra': '',
            'extension': {
                'descriptionText': "",
                'description': ""
            }
        }

        data['base']['sourceUrl'] = url

        sourceHtml_xpath = etree.HTML(sourceHtml)
        html_xpath = sourceHtml_xpath.xpath('//script[@charset="gbk"]')
        if html_xpath == None:
            return

        data_str = etree.tostring(html_xpath[0]).decode()
        need_data_re = re.search('var pageConfig = ({[\s\S]*?});', data_str)
        if need_data_re == None:
            return
        need_data = need_data_re.group(1)

        need_data = html.unescape(need_data)

        need_data = demjson.decode(need_data)

        itemid = need_data['product']['skuid']
        data['base']['productId'] = itemid

        title = need_data['product']['name']
        data['base']['title'] = title

        brand = need_data['product']['brand']
        data['base']['brand'] = brand

        yuanjia = get_jd_price(itemid)
        if yuanjia:
            data['base']['price'] = yuanjia

        mall_link_xpath = sourceHtml_xpath.xpath('//div[@class="popbox-inner"]/div/h3/a/@href')
        if mall_link_xpath:
            mall_link = mall_link_xpath[0]
            mall_link = 'https:' + mall_link
            data['base']['mall_link'] = mall_link

        mall_name_xpath = sourceHtml_xpath.xpath('//div[@class="popbox-inner"]/div/h3/a/text()')
        if mall_name_xpath:
            mall_name = mall_name_xpath[0]
            mall_name = mall_name
            data['base']['mall_name'] = mall_name

        # product_rating
        product_ratings = sourceHtml_xpath.xpath('//div[@class="score-parts"]/div')
        score_list = []
        for score in product_ratings:
            scores = score.xpath('.//em/@title')
            score_list.append(scores[0])

        if score_list:
            product_rating = str(score_list[0]).replace('分','')
            goods_deliver = str(score_list[1]).replace('分', '')
            goods_description = str(score_list[-1]).replace('分', '')
            data['base']['product_rating'] = product_rating
            data['base']['goods_deliver'] = goods_deliver
            data['base']['goods_description'] = goods_description

        info2 = []
        descriptionTextlist = []
        propsCut_data = sourceHtml_xpath.xpath('//ul[@class="parameter2 p-parameter-list"]//li/text()')
        for attr_data in propsCut_data:
            attr_data = attr_data.split('：')
            key = attr_data[0]
            value = attr_data[1]

            data_i = {
                "productId": str(itemid),
                "pkey": key,
                "pval": value,
                "unit": ""
            }
            info2.append(data_i)
            infostr = '<li title="{value}">{key}:&nbsp;{value}</li>'.format(key=attr_data[0], value=attr_data[1])
            descriptionTextlist.append(infostr)
        descriptionText = '<ul>' + ''.join(descriptionTextlist) + '</ul>'
        data['attributes'] = info2
        data['extension']['descriptionText'] = descriptionText


        imglist2 = []
        images = sourceHtml_xpath.xpath('//ul[@class="lh"]/li/img/@src')
        for i in images:
            imgUrl = re.sub('\d+x\d+_', '350x449_', "https:" + i)
            img_i = {
                "type": "0",
                # "imgUrl": imgUrl.replace('','.com/n0/')
                "imgUrl": re.sub('.com/n\d/', '.com/n0/',imgUrl)
            }
            imglist2.append(img_i)
        descurl = 'https:' + need_data['product']['desc']
        print(descurl)
        desc = get_desc(descurl)

        imglist = []
        if desc:
            desc_html = json.loads(desc)['content']
            detill_img_list = re.findall('background-image:url\((.*?)\)', desc_html)
            if detill_img_list == []:
                print('desc1')
                desc_html = etree.HTML(desc_html)
                desc_html_img = desc_html.xpath('//img/@data-lazyload')
                for img in desc_html_img:
                    img_i = {
                        "type": "1",
                        "imgUrl": img
                    }
                    imglist2.append(img_i)
                    imgstr = '<img src="{}">'.format(img) + '<br/>'
                    imglist.append(imgstr)
            else:
                print('desc2')
                for i in detill_img_list:
                    img = i if 'https:' in i else 'https:' + i
                    img_i = {
                        "type": "1",
                        "imgUrl": "https://"+img  if "https:" not in img else img
                    }
                    imglist2.append(img_i)

                    imgstr = '<img src="{}">'.format(img) + '<br/>'
                    imglist.append(imgstr)

        description = '<div>' + ''.join(imglist) + '</div>'
        data['extension']['description'] =descriptionText+ description
        data['images'] = imglist2
        variable_img_dict = {}
        variable_img_xp = sourceHtml_xpath.xpath('//*[@id="choose-attr-1"]/div[2]/div')
        for i in variable_img_xp:
            data_sku = i.xpath('./@data-sku')
            data_img = i.xpath('.//img/@src')
            if data_sku and data_img:
                var_img = 'https:' + str(data_img[0]).replace('/n9/','/n1/').replace('s40x40_','')
                item_dict = {
                    "type":"3",
                    "imgUrl":var_img
                }
                variable_img_dict[data_sku[0]] = item_dict

        variableList2 = []
        count = 0
        sku_mapping = get_sku_mapping(sourceHtml)
        for i,v in enumerate(sku_mapping):
            skuid = v['skuId']
            vable_price = get_jd_price(skuid)

            base_i = {
                "productId": str(itemid) + str(i),
                "title": title,
                "currency": "CNY",
                "price": vable_price,
                # "price": float(yuanjia),
                "priceRange": '',
                "stock": '',
                "sales": ''
            }
            attributes_i = []
            images_i = []
            del v['skuId']
            for j, k in v.items():
                attr_i = {
                    "pkey": j,
                    "productId": str(skuid) + '{}{}'.format(i,count),
                    "pval": k,
                    "unit": ""
                }
                if '毛重' in j or "重量" in j or 'kg' in j or 'g' in j:
                    data['base']['weight_value'] = k
                if '尺寸' in j:
                    data['base']['size'] = k
                count += 1
                attributes_i.append(attr_i)
            if str(skuid) in variable_img_dict:
                images_i.append(variable_img_dict[str(skuid)])

            vdata = {
                "base": base_i,
                "attributes": attributes_i,
                "images": images_i
            }
            variableList2.append(vdata)
        data['variableList'] = variableList2
        return data

    def judgeCommodityTrend(self, goodsDescript):
        '''
        判断商品描述是上升趋势还是下降趋势：trend = rise 上升， =decline 下降
        '''
        if not goodsDescript:
            return ''
        if 'Smaller' in goodsDescript:
            trend = 'decline'
        elif 'Higher' in goodsDescript:
            trend = 'rise'
        else:
            trend = ''
        return trend

    def resetClassVar(self):
        self.proxyIpPortList = []

    def test(self):
        print('----------------')

    def entity(self, productId, product_title, currency, price, priceRange, infos, main_image, quantity, saleNums):
        data = {
            "base": {
                "productId": productId,
                "title": product_title,
                "currency": currency,
                "price": price,
                "priceRange": priceRange,
                "stock": quantity,
                "sales": saleNums
            },

            "attributes": infos,
            "images": [
                {
                    "type": 0,
                    "imgUrl": main_image,
                },
            ],
        }
        return data

    """
             # 去除html中的各种标签，保留文字数据
             # @param htmlstr html字符串
             # @return string
             # @author hongxuanqi
        """

    def filter_tags(self, htmlstr):
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', htmlstr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replaceCharEntity(s)  # 替换实体
        # 去除连续的空格和换行，将连续的换行替换成一个换行
        s = re.sub(' {2,}', '', s)
        s = re.sub('( \n)', '', s)
        s = re.sub('\n{2,}', '\n', s).strip()

        return s

    def replaceCharEntity(htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如&gt;
            key = sz.group('name')  # 去除&;后entity,如&gt;为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    pass
