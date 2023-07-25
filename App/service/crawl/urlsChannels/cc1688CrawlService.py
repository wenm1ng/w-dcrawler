# coding: utf-8
import operator
import re, os.path, time, urllib.parse

import requests
from App.common.webRequest import WebRequest
from Configs import defaultApp, site
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from scrapy.selector import Selector
from App.common.url.baseUrlHandle import baseUrlHandle
import json, gevent
from App.service.system.classContextService import classContextService
from urllib.parse import urlparse

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis

from App.common.userAgent import userAgent

import hashlib
import datetime
from lxml import etree

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_desc(url):
    if not url:
        return ''
    resp = requests.get(url, timeout=8)
    offer_details_re = re.findall('var offer_details=(.*);', resp.text)
    if not offer_details_re:
        offer_details_re = re.findall("var desc='(.*?)';", resp.text)
    return offer_details_re


class cc1688CrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = '1688'

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
        pass

    """
     # 保存文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月16日 10:11:43
    """

    def saveHtmlResult(self, url, isExtend=0):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()

        itemid = re.search("https://detail.1688.com/offer/(\d+).html.*?", url).group(1)  # 唯一id
        md5str = itemid
        itemid_validity = commonRedisClass.zscoreValByKey('1688_info', '{}'.format(md5str))
        now_time = time.time()
        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.ali1688_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/1688_info/_doc/{itemid}'.format(itemid=md5str))
        #         data = commonElasticSearchClass.getSourceByIndexKey(index='1688_info', doc_type="_doc", id=md5str)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #         return
        header = {
            'Authority': 'detail.1688.com',
            'method': 'GET',
            # 'Path': '/offer/616382181546.html',
            'Scheme': 'https',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            # 'Content-Type': 'charset=gbk',
            # 'Cookie': '_uab_collina=160775891033030647351532; cna=MilbGEYJX2QCAS9rVY1Rvi/N; UM_distinctid=17655e626ab4d6-0010eee1158fcc-c791039-1fa400-17655e626ac9db; taklid=0e44eec3fed84db186d450598cc48c41; cookie2=113aa6f5327a11ee97a1e53b0d30dbde; t=1005c1682a791cc067f0abbf3f13bfa8; _tb_token_=ee51eb5d5e3fd; xlly_s=1; _m_h5_tk=752c4770e98fb0dbae19687f8b14e690_1608038608013; _m_h5_tk_enc=a2b8b5b47896927287ed8e852fdefa74; lid=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj; ali_apache_track=c_mid=b2b-4293795368a374d|c_lid=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj|c_ms=1|c_mt=3; ali_apache_tracktmp=c_w_signed=Y; last_mid=b2b-4293795368a374d; CNZZDATA1253659577=954988728-1607758317-https%253A%252F%252Fdetail.1688.com%252F%7C1608033021; _is_show_loginId_change_block_=b2b-4293795368a374d_false; _show_force_unbind_div_=b2b-4293795368a374d_false; _show_sys_unbind_div_=b2b-4293795368a374d_false; _show_user_unbind_div_=b2b-4293795368a374d_false; __rn_alert__=false; alicnweb=touch_tb_at%3D1608034303604%7ChomeIdttS%3D82275062466567210651994194792170869619%7ChomeIdttSAction%3Dtrue%7Clastlogonid%3D%25E5%2594%25AF%25E7%2588%25B1%25E4%25BD%25A0_nsj; cookie1=UUBb0lE3SfPz39x3jLuqSu9f33APcSjcbV5HvTBMplE%3D; cookie17=Vy6xzT2X0Wxc4Q%3D%3D; sg=j82; csg=eb814da2; unb=4293795368; uc4=nk4=0%40r8C%2B%2B81RI2zkYR04heAJg4Cu0AK%2F&id4=0%40VXkWSvzFADd%2FtZaKPupSSqPYeUiu; __cn_logon__=true; __cn_logon_id__=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj; _nk_=%5Cu552F%5Cu7231%5Cu4F60_nsj; _csrf_token=1608034613610; ali_ab=47.107.85.141.1608034623562.4; ad_prefer="2020/12/15 20:22:38"; h_keys="%u767e%u8d27"; JSESSIONID=320875A6800D47C71A2E90C48FB612D3; tfstk=c041BwMrCdv1G8j2751EgscXaCica-RSGGMg1lXyugTDKLNnpsqezYsmkovvJ0hC.; l=eBjMndVmO0I7Bbc2BOfZourza77TSIRAguPzaNbMiOCPOF6e5GsAWZJTPWKwCnGVhsQDR3uKcXmBBeYBqHtInxvTZ73Kgjkmn; isg=BHNzM37dKMIcreSaYX47quSCAnedqAdqgCGnlCUQwxLJJJPGrX5LutK82lTKhF9i',#登陆的cookie
            # 'Cookie': '_uab_collina=160803673000581629999652; cna=Lp9fGE1SfAoCAS9rVY3FnBR0; xlly_s=1; x5sec=7b226c61707574613b32223a223064336638623736313637336332396661646536636166633435376333616231434b3369347634464550324c3276586a6e3969783241453d227d; UM_distinctid=17666757aaa6a3-07e5ed576cdaf9-c791039-1fa400-17666757aab733; CNZZDATA1253659577=2145433907-1608033021-https%253A%252F%252Fdetail.1688.com%252F%7C1608033021; taklid=6ac17f5d033a4e59b57cd2e516a3f0bd; cookie2=11edd877cc9cbd89b95df6e1ccbe2e51; t=317e0436c3ab76ef0b835d091d8d8712; _tb_token_=e73e8133e4085; __cn_logon__=false; JSESSIONID=B9C5D2E7D0FDBB3391FB2341559C4EED; _csrf_token=1608036669909; tfstk=cHxVBm2O2mnqEQjsJisa5F6bG7DAZ09DIuWCoF_Woxnu39QcifPOENHFUO1KqZf..; l=eBjMndVmO0I7B4LEBOfwnurza77tsIRAguPzaNbMiOCPOJCX5eDCWZJTfbLWCnGVhsGeR3uKcXmBBeYBqnDOO6XmsjDtjcDmn; isg=BJeXt6XDhDaEaQC2rconfuCeJgvh3Gs-BK0DuOnEtmbNGLda8am7j8Q6frgG8EO2; alicnweb=touch_tb_at%3D1608036747695',
            'Referer': 'https://www.1688.com/',
            'Content-Type': 'Content-type:text/html;charset=gbk',

            # 'USETYPE':0,
            # 'TARGETURL':url,
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        if isExtend == 'description':
            charsetCode = "utf-8"
            siteCharset = {}
            if '1688' in site.charset:
                siteCharset = site.charset['1688']
            if siteCharset:
                parse = urlparse(url)
                isFlag = False
                for charsetKey, charsetVal in siteCharset.items():
                    if isFlag == True:
                        break
                    for k, v in charsetVal.items():
                        if k == 'default':
                            for v1 in v:
                                if parse.netloc.find(v1) != -1:
                                    charsetCode = charsetKey
                        if k == 'point':
                            for v1 in v:
                                if v1 == parse.netloc:
                                    charsetCode = charsetKey
                                    isFlag = True
                                    break

            header['Content-Type'] = 'Content-type:text/html;charset=' + charsetCode
        stree = 'clickid=ttxlm76jm91z5kzvaadasdlke1o35095&sessionid=l17def3v8uk083yn8mrvljkmbnlcfikz'''
        for useType in '01122':
            header['USETYPE'] = useType
            header['TARGETURL'] = "https://detail.1688.com/offer/{}.html?".format(itemid) + stree
            # header['user-agent'] = userAgent().getPc()
            header[
                'user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=8)
                html = result.text(self=WebRequest)
                print('html:', len(html))

                data = self.setResult(html, url)  # 洗完的结构
                print(json.dumps(data))
                if data:
                    self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                    commonElasticSearchClass.insertDataByIndexKey(index='1688_info', id=md5str, data=data)
                    commonRedisClass.insertDataByIndexKey(redisKeyName='1688_info', redisStr=md5str)
                    self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                    return
                else:
                    continue
            except Exception as e:
                print('19行error:',e)

    """
     # 判断是否为真实连接
     # @param self
     # @param htmlText 抓取页面
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月20日 16:19:15
    """

    def isTrueHtml(self, htmlText, url):
        result = False
        if not htmlText:
            return result
        resultTextSelector = Selector(text=htmlText)
        if not resultTextSelector:
            return result
        title = resultTextSelector.xpath('//h1[@class="d-title"]/text()').extract_first()

        if title:
            return True
        return result

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):
        skuProps = ''
        part_json = ''
        base = {
            'productId': '',
            'title': '',
            'sourceUrl': '',
            'site': 'CN',
            'platform_type': 4,
            'currency': '',
            'price': float(0.00),
            'priceRange': '',
            'siteLanguage': 'zh',
            'business_years': 0,  # 商家年限
            'location': '',  # 地区
            'contact_seller': '',  # 联系卖家
            'goods_description': '',  # 货描
            'return_rate': '',  # 回头率
            'goods_deliver': '',  # 发货
            'response': '',  # 响应
            'management_model': '',  # 经营模式
            'supply_level': '',  # 供应等级
            'sales': '',  # 销量
            'collection_volume': '',  # 收藏量
            'praise_rate': '',  # 好评率
            'product_rating': '',  # 商品评分
            'comments_number': '',  # 评论数量

            "phone": '',  # 联系方式
            "merchants": '',  # 商家名称
            "weight_value": '',  # 重量值
            "weight_unit": '',  # 重量单位
            "size": '',  # 尺寸
            "size_table": '',  # 尺码表
        }
        source_html = sourceHtml
        source_html = source_html.replace('\n', '').replace('    ', '')
        res_xp = Selector(text=sourceHtml)

        phone_list = []
        # 联系方式
        mobile = re.findall('data-no="(.*?)"', sourceHtml)
        if mobile:
            phone_list.append(mobile[0])
        else:
            pass
        phone_patten = re.compile('电&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;话(.*?)</dd>', re.DOTALL)
        phone = re.search(phone_patten, sourceHtml)
        if phone:
            phone1 = re.findall('<dd>(.*?)</dd>', str(phone.group()).strip())
            phone_list.append(str(phone1[0]).replace(' ', ''))
        else:
            pass
        base['phone'] = ','.join(phone_list) if phone_list else ""

        # 商家名称
        merchants = res_xp.xpath('//a[@class="name has-tips "]/text()|//div[@class="nameArea"]/a/@title').extract_first()
        base['merchants'] = merchants

        # 商家年限
        business_years = res_xp.xpath('//span[@class="tp-year"]/text()|//span[@class="year-number"]/text()').extract_first()
        base['business_years'] = business_years

        # 重量单位
        weight = res_xp.xpath(
            '//div[@class="attributes-item mod-info kuajing-attribues"]/dl/dd/span[1]/em/text()').extract_first()  # 商品评分
        if weight:
            base['weight_value'] = str(weight).split(' ')[0]
            base['weight_unit'] = str(weight).split(' ')[1]

        # 尺寸
        size_unit = ['m', 'dm', 'cm', 'mm', 'M', 'DM', 'CM', 'MM', '米', '分米', '厘米', '毫米', '英寸']
        size = res_xp.xpath(
            '//div[@class="attributes-item mod-info kuajing-attribues"]/dl/dd/span[3]/em/text()').extract_first()  # 商品评分

        if size:
            for item in size_unit:
                if item in size:
                    base['size'] = str(size).replace(' ', '').strip()

        # get product_id
        product_id = res_xp.xpath('//meta[@name="b2c_auction"]/@content').extract_first()
        if product_id:
            base['productId'] = product_id

        # get product_title
        product_title = res_xp.xpath('//h1[@class="d-title"]/text()').extract_first()
        if product_title:
            base['title'] = product_title

        base['sourceUrl'] = url
        platformSite = baseUrlHandle(url).getPlatformAndSite()

        # get platform_type and site
        if platformSite:
            base['site'] = platformSite['site']
            base['platform_type'] = platformSite['platformType']

        # get currency
        currency = res_xp.xpath('//meta[@property="og:product:currency"]/@content').extract_first()
        if currency:
            base['currency'] = currency

        # get price, 如果存在活动价则取活动价，否则取原价
        iDetailData = re.findall('var iDetailData = (.*?)};', source_html)
        if iDetailData:
            part_json = iDetailData[0]
            if part_json:
                skuProps = re.findall('skuProps:(.*?),skuMap:', part_json)

        if not skuProps:
            if part_json:
                skuProps = re.findall('skuProps":(.*),"skuMap', part_json)

        skuPropsDic = {}
        skuMapDic = {}

        # 收藏量
        scl = res_xp.xpath('//div[@class="obj-fav"]//span/text()').extract_first()  # 收藏数
        collectionNums = int(''.join(list(filter(str.isdigit, scl))) if scl else 0)
        base['collection_volume'] = collectionNums

        # 总销量
        # saleCount_res = re.findall('.*saleCount.*"(\d+?)"', source_html)
        # totalSaleNums = saleCount_res[0] if saleCount_res else ''  # 这个是总销量，还有个sku销量
        # base['sales'] = totalSaleNums

        # 商品评分
        grade = res_xp.xpath('//span[@class="star-score"]/text()').extract_first()  # 商品评分
        base['product_rating'] = grade

        # 评价总数
        pls = re.findall('totalRate":"(\d+)",', source_html)  # 评论总数
        commentNums = int(pls[0]) if pls else 0
        base['comments_number'] = commentNums

        # 库存
        stock = re.findall('"stock":(\d+),"', source_html)
        stock = int(stock[0]) if stock else 0
        base['stock'] = stock

        if 'supplierinfo' in source_html:
            companyName = res_xp.xpath(
                '//div[@class="company-name"]/a/text()|//div[@class="nameArea"]/a[@class="name"]/@title').extract_first()  # 供应商

            sincerity = res_xp.xpath(
                '//span[@class="year-number"]/text()|//span[@class="tp-year"]/text()').extract_first()  # 诚信通
            sincerity = int(sincerity) if sincerity else 0
            contactSeller = res_xp.xpath(
                '//a[@class="link name"]/text()|//div[@class="contactSeller"]/a/text()').extract_first()  # 联系人
            if not contactSeller:
                contactSeller_re = re.findall('name:"(.*?)"',sourceHtml)
                contactSeller = [contactSeller_re[0] if contactSeller_re else ''][0]
            base['contact_seller'] = contactSeller

            ww_nick = res_xp.xpath(
                '//span[@class="disc"]//span[contains(@class,"wangwang")]/@data-nick|//div[@class="contactSeller"]/span[contains(@class,"wangwang")]/@data-nick').extract_first()  # 旺旺昵称
            # wangwangNickName = urllib.parse.unquote(ww_nick)
            # wangwangLink = 'https://amos.alicdn.com/getcid.aw?v=3&groupid=0&s=1&charset=utf-8&uid={}&site=cnalichn'.format(
            #     ww_nick)  # 旺旺跳转链接

            sup_lever = res_xp.xpath('//div[contains(@class,"supply-grade")]//img|//div[@class="sellerinfo-ui-html-fragment  "]//img').extract()  # 供应等级
            supplyLevel = len(sup_lever) if sup_lever else 0
            base['supply_level'] = supplyLevel

            managementModel = res_xp.xpath('//span[@class="biz-type-model"]/text()').extract_first()  # 经营模式
            managementModel = managementModel.strip() if managementModel else ''
            base['management_model'] = managementModel

            belongArea = res_xp.xpath('//div[contains(@class,"address")]/span/text()').extract_first()  # 所在地址
            base['location'] = belongArea

            '''货描'''
            hm = res_xp.xpath('//div[contains(@class,"description-show-hm") and not(contains(@style,"none"))]')
            hm_bfb = hm.xpath('./span/text()').extract_first()  # 货描
            hm_qs = hm.xpath('./img/@class').extract_first()
            hm_trend = self.judgeCommodityTrend(goodsDescript=hm_qs)  # 货描趋势
            descriptionOfGoods = {
                "value": hm_bfb,
                "trend": hm_trend
            }
            # base['goods_description'] = descriptionOfGoods
            base['goods_description'] = hm_bfb

            '''响应'''
            xy = res_xp.xpath('//div[contains(@class,"description-show-xy") and not(contains(@style,"none"))]')
            xy_bfb = xy.xpath('./span/text()').extract_first()  # 响应
            xy_qs = xy.xpath('./img/@class').extract_first()
            xy_trend = self.judgeCommodityTrend(goodsDescript=xy_qs)  # 响应趋势
            repercussions = {
                'value': xy_bfb,
                'trend': xy_trend
            }
            # base['response'] = repercussions
            base['response'] = xy_bfb

            '''发货'''
            fh = res_xp.xpath('//div[contains(@class,"description-show-fh") and not(contains(@style,"none"))]')
            fh_bfb = fh.xpath('./span/text()').extract_first()  # 发货
            fh_qs = fh.xpath('./img/@class').extract_first()
            fh_trend = self.judgeCommodityTrend(goodsDescript=fh_qs)  # 响应趋势
            deliverGoods = {
                'value': fh_bfb,
                'trend': fh_trend
            }
            # base['goods_deliver'] = deliverGoods
            base['goods_deliver'] = fh_bfb

            '''回头'''
            ht = res_xp.xpath('//span[contains(@class,"description-value-ht")]')  # 回头
            ht_bfb = ht.xpath('./text()').extract_first()  # 回头
            ht_qs = ht.xpath('./img/@class').extract_first()
            ht_trend = self.judgeCommodityTrend(goodsDescript=ht_qs)  # 响应趋势
            returnRate = {
                'value': ht_bfb,
                'trend': ht_trend
            }
            # base['return_rate'] = returnRate
            base['return_rate'] = ht_bfb

        # 判断是否存在多属性信息
        # if skuProps:
        #     skuPropsDic = json.loads(skuProps[0])
        #     skuMap = re.findall('skuMap:(.*?),end', part_json)
        #     if not skuMap:
        #         skuMap = re.findall('skuMap":(.*?),},"end', part_json)
        #     skuMapDic = json.loads(skuMap[0])
        #     sorted_x = sorted(skuMapDic.items(), key=operator.itemgetter(0))
        #     skuMapDic = {}
        #     for sorted_x_i in sorted_x:
        #         print(sorted_x_i)
        #         skuMapDic.update({sorted_x_i[0]: sorted_x_i[1]})
        # print(json.dumps(skuMapDic))

            image_name_url_relation = {}  # 主图和颜色名字关系
            product_attr = {}  # 产品属性

        # 获取价格范围
        if 'priceRange' in part_json:
            price_module_str = re.findall('priceRange:(.*]),p', part_json)
            if not price_module_str:
                price_module_str = re.findall('priceRange":(.*]),"p', part_json)
            price_module = eval(price_module_str[0]) if price_module_str else []
            max_price = price_module[0][-1]
            min_price = price_module[-1][-1]
            if max_price > min_price:
                price = max_price
                price_range = "{}~{}".format(min_price, max_price)
            else:
                price = min_price
                price_range = "{}~{}".format(max_price, min_price)
        else:
            price_temp = re.findall('price"?:"(.*?)"', part_json)
            if price_temp:
                if isinstance(price_temp, list):
                    if '-' in price_temp[0]:
                        price = price_temp[0].split('-')[1]
                        price_range = str(price_temp[0].split('-'))
                    else:
                        price = price_temp[0]
                        price_range = str(price_temp[0])
                else:
                    price = price_temp
                    price_range = str(price_temp)
            else:
                price = ''
                price_range = ''
        # 如果有多属性才处理
        # if skuPropsDic:
        #     for spd in skuPropsDic:
        #         prop_key = spd['prop']  # 属性名称
        #         prop_val = spd['value']  # 属性值 []
        #         for one_val in prop_val:
        #             # 获取具体颜色
        #             name = one_val['name'] if "name" in one_val else ''
        #             imageUrl = one_val['imageUrl'] if "imageUrl" in one_val else ''
        #             image_name_url_relation[name] = imageUrl
        #             product_attr[name] = prop_key
        if price:
            base['price'] = price
        else:
            price_temp = re.findall("refPrice:'(.*?)',", source_html)
            if price_temp:
                base['price'] = price_temp[0]
            else:
                price_re = re.findall('currentPrices":\[{"price":"(.*?)","beginAmount', source_html)
                base['price'] = price_re[0] if price_re else 0
        if price_range:
            price_range = str(price_range).replace('[','').replace(']','').replace("'",'').replace(",",'~').replace(" ",'')
        else:
            price_table = res_xp.xpath('//*[@id="mod-detail-price"]//td/@data-range').extract()
            price_range_list = []
            for i in price_table:
                price_range = json.loads(str(i))
                if price_range:
                    price_range_list.append(price_range['price'])
                else:
                    pass
            if price_range_list:
                price_range = str(min(price_range_list)) + '~' + str(max(price_range_list))
            else:
                price_range = ''
        base['priceRange'] = price_range
        image = []
        # 获取原图
        small_images = []
        small_image_list = res_xp.xpath('//ul[@class="nav nav-tabs fd-clr"]/li').extract()
        imageTemp = []
        for i in range(0, len(small_image_list)):
            small_image_re = re.findall('original.*?(https:.*?.jpg)', small_image_list[i])
            small_image = small_image_re[0] if small_image_re else ''
            if small_image:
                if i == (len(small_image_list) - 1):
                    imageTemp.append(small_image)
                    # image.append({
                    #     'type': 2,
                    #     'imgUrl': defaultApp.specialSegmentationSymbol.join(imageTemp)
                    # })
                else:
                    imageTemp.append(small_image)

        if imageTemp:
            for i in range(0, len(imageTemp)):
                if i == 0:
                    image.append({
                        'type': 0,
                        'imgUrl': imageTemp[0]
                    })
                else:
                    image.append({
                        'type': 2,
                        'imgUrl': imageTemp[i]
                    })

        # 获取描述
        part_description_html = res_xp.xpath(
            '//div[@class="region-custom region-detail-feature region-takla ui-sortable region-vertical"]').extract_first()
        desc_url = res_xp.xpath('//div[@id="desc-lazyload-container"]/@data-tfs-url').extract_first()

        # 去获取描述url提供的地址信息
        extension = {}

        product_title = res_xp.xpath('//h1[@class="d-title"]/text()').extract_first()

        if not product_title:
            # logger.info("没有获取到标题，重新切换代理进行获取,结束该次爬取")
            # sentinelServMaster.rpush(self.redis_key, task)
            data = self.new_style(sourceHtml,base)
            return data

        main_attr_res = res_xp.xpath('//div[@id="mod-detail-attributes"]/@data-feature-json').extract_first()
        if main_attr_res:
            main_attr_json = eval(main_attr_res)
        else:
            main_attr_json = ''
        main_attr = []

        descriptionText = ""
        for o_s in main_attr_json:
            pkey_m = o_s['name']
            attr_val_m = o_s['value']
            main_sku_attr_data = {
                'pkey': pkey_m,
                'productId': product_id,
                'pval': attr_val_m,
                'unit': ''
            }
            if '尺寸' in pkey_m or '规格' in pkey_m:
                if 'L' not in attr_val_m:
                    for item in size_unit:
                        if item in attr_val_m:
                            base['size'] = attr_val_m
                        else:
                            continue
                else:
                    continue
            if '品牌' in pkey_m:
                base['brand'] = attr_val_m
            main_attr.append(main_sku_attr_data)

            descriptionTextlist = []
            for attr in main_attr_json:
                infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=attr['name'],value=attr['value'])
                descriptionTextlist.append(infostr)
            descriptionText = ''.join(descriptionTextlist)# '<ul>' + ''.join(descriptionTextlist) + '</ul>'
            extension['descriptionText'] = descriptionText
        offer_details_re = get_desc(desc_url)
        offer_details = offer_details_re[0] if offer_details_re else ''
        detail_content = ''
        print(2222,offer_details_re)
        if offer_details:
            if 'content' in str(offer_details):
                offer_details_dic = json.loads(offer_details)
                detail_content = offer_details_dic['content']
            else:
                detail_content = offer_details
        # HTML = etree.HTML(sourceHtml)
        # desctext1 = ""
        # desctext1_xpath = HTML.xpath('//div[@class="widget-custom offerdetail_ditto_otherAttr"]')[0]
        # if desctext1_xpath:
        #     desctext1 = etree.tostring(desctext1_xpath).decode()
        #
        # desctext2 = ""
        # desctext2_xpath = HTML.xpath('//div[@class="widget-custom offerdetail_ditto_attributes"]')[0]
        # if desctext2_xpath:
        #     desctext2 = etree.tostring(desctext2_xpath).decode()
        # description_text = desctext1 + desctext2
        # extension['description_text'] = description_text

        extension['description'] = descriptionText + str(detail_content).replace("var desc='",'')

        # 组装变体数据
        variableList = []
        if 'skuProps' in source_html:

            iDetailData = re.findall('var iDetailData = (.*?)};', source_html)
            if iDetailData:

                skuProps_se = re.findall('skuProps"?:(.*?),"?skuMap',
                                         iDetailData[0])
                skuProps = skuProps_se[0].replace('\n', '').replace(' ', '').replace(',skuMap', '').replace(',"skuMap',
                                                                                                            '')  # .split(':', 1)[1]
                skuProps = eval(skuProps)
                skuMaps = re.findall('skuMap"?:(.*?),"?end', str(iDetailData[0]))

                if skuMaps:
                    skuMap = str(skuMaps[0]).replace(' ', '')
                    try:
                        skuMaps = json.loads(skuMap)
                    except:
                        skuMaps = json.loads(skuMap[:-2])
                else:
                    skuMaps = eval(str(skuMaps[0]).replace(' ', ''))
                variable_list, product_attr = self.variable_result(skuProps, skuMaps)
                for val in variable_list:
                    # for skm, val in dict(skuMapDic).items():
                    attr_vals = val['name'].split('&gt;')
                    sku_id = val['skuId']
                    sku_sale_count = val['saleCount']  # 变体销量
                    sku_can_book_count = val['canBookCount']  # 变体库存
                    infos = []  # 属性
                    if 'discountPrice' in val:
                        sku_price = val['discountPrice']  # 折扣价
                    elif 'price' in val:
                        sku_price = val['price']  # 没有折扣价就用这个原价
                    if not sku_price:
                        sku_price = base['price']

                    main_image_sku = val['imageUrl']

                    for attr_val in attr_vals:
                        pkey = product_attr[attr_val]
                        sku_attr_data = {
                            'pkey': pkey,
                            'productId': sku_id,
                            'pval': attr_val,
                            'unit': '',
                        }
                        infos.append(sku_attr_data)
                    result = self.entity(sku_id, product_title, currency, sku_price, price_range, infos, main_image_sku,
                                         sku_can_book_count, sku_sale_count)
                    variableList.append(result)

        # 获取新增需求的额外数据
        # extra_data = self.get_extra_data(source_html, res_xp)
        product_data = {}
        # product_data['part_description_html'] = part_description_html
        # product_data['site'] = 'asdasdsadsadsadsad'
        # product_data['product_id'] = product_id
        # # product_data['source_html'] = source_html
        # product_data['token'] = 'adasdadsdad'
        # product_data['small_image'] = small_image
        # product_data['product_title'] = product_title
        # product_data['source_url'] = 'adsdasdsada'
        # product_data['main_attr'] = main_attr
        product_data['extra_data'] = []
        product_data['base'] = base
        product_data['images'] = image
        product_data['attributes'] = main_attr
        product_data['variableList'] = variableList
        product_data['is_valid'] = 1
        # product_data['token'] = str(self.getToken(self))
        product_data['extra'] = ''
        product_data['extension'] = extension
        # print('\n'*2)
        # print(product_data)
        # print('+'*50)
        return product_data

        # print(product_data)

        # with open(self.relayServiceClass.getFileNameByUrl(url=url), 'w', encoding='utf8') as f:
        #     f.write(result.text())

        # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
        # result = self.parse_description(desc_req, product_data)
        # result_json = json.dumps(result)
        # sentinelServMaster.lpush(self.item_key, result_json)

    def variable_result(self,skuProps,skuMaps):
        """组装变体"""
        variable_list = []
        product_attr = {}
        for spd in skuProps:
            prop_key = spd['prop']  # 属性名称
            prop_val = spd['value']  # 属性值 []
            for one_val in prop_val:
                name = one_val['name'] if "name" in one_val else ''
                product_attr[name] = prop_key

        prop_list = []
        if len(skuProps) == 2:
            item1 = skuProps[0]
            item2 = skuProps[1]
            prop_list.append(item1['prop'])
            prop_list.append(item2['prop'])
            for v in item1['value']:
                for i in item2['value']:
                    if '&gt;' in str(skuMaps):
                        name = v['name'] + '&gt;' + i['name']
                    else:
                        name = v['name']
                    if name in str(skuMaps):
                        try:
                            value = skuMaps[name]
                        except:
                            continue
                        if 'imageUrl' in str(v):
                            imageUrl = v['imageUrl']
                        else:
                            imageUrl = ''
                        if 'price' in str(value):
                            price = value['price']
                        else:
                            price = ''
                        if 'discountPrice' in str(value):
                            discountPrice = value['discountPrice']
                        else:
                            discountPrice = ''
                        item_dict = {
                            'name': name,
                            'imageUrl': imageUrl,
                            'skuId': value['skuId'],
                            'saleCount': value['saleCount'],
                            'canBookCount': value['canBookCount'],
                            'price': price,
                            'discountPrice': discountPrice,
                        }
                        variable_list.append(item_dict)
                    else:
                        print('name不存在skuMaps:', name,skuMaps)
        else:
            for item in skuProps[0]['value']:
                name = item['name']
                if name in skuMaps:
                    try:
                        value = skuMaps[name]
                    except:
                        continue
                    if 'imageUrl' in str(item):
                        imageUrl = item['imageUrl']
                    else:
                        imageUrl = ''
                    if 'price' in str(value):
                        price = value['price']
                    else:
                        price = ''
                    if 'discountPrice' in str(value):
                        discountPrice = value['discountPrice']
                    else:
                        discountPrice = ''
                    item_dict = {
                        'name': name,
                        'imageUrl': imageUrl,
                        'skuId': value['skuId'],
                        'saleCount': value['saleCount'],
                        'canBookCount': value['canBookCount'],
                        'price': price,
                        'discountPrice': discountPrice,
                    }
                    variable_list.append(item_dict)
                else:
                    print('name不存在skuMaps:', name,skuMaps)
        return variable_list, product_attr

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
                    "type": 3,
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

    def replaceCharEntity(self, htmlstr):
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

    def new_style(self, html, base):
        data = {}
        attributes = []

        re2 = re.compile("window.__INIT_DATA=(.*?)</script>", re.DOTALL)
        re_html = re.search(re2, html).group()
        if re_html:
            re_html = re_html.replace('window.__INIT_DATA=', '').replace('</script>', '')
            data2 = json.loads(re_html)

            # 销量
            saledCount = data2['globalData']['tempModel'].get('saledCount')
            companyName = data2['globalData']['tempModel'].get('companyName')
            title = data2['globalData']['tempModel'].get('offerTitle')
            productId = data2['globalData']['tempModel'].get('offerId')
            # 变体,商家
            offerDomain = data2['globalData'].get('offerDomain')
            price_range = data2['globalData']['skuModel'].get('skuPriceScale')

            # 橱窗图
            images = ''

            # 样式/颜色,身高
            skuProps = data2['globalData']['skuModel'].get('skuProps')
            # 规格,大小
            skuProps1 = data2['globalData']['skuModel'].get('skuInfoMap')
            skuProps2 = data2['globalData']['skuModel'].get('skuInfoMapOriginal')
            # print(saledCount,companyName)
            # print(offerId,price_range,title)
            data2_data = data2['data']
            for k, v in data2_data.items():

                if type(v.get('data')) == dict:
                    for kk, vv in v['data'].items():
                        if kk == 'offerImgList':
                            images = vv
                        if not saledCount and kk == 'saleNum':
                            saledCount = vv
                        if not offerDomain and kk == 'offerDomain':
                            offerDomain = vv

                elif isinstance(v.get('data'),list):
                    for item in v['data']:
                        item_dict = {}
                        item_dict['pkey'] = item['name']
                        item_dict['productId'] = item['fid']
                        item_dict['pval'] = item['value']
                        item_dict['unit'] = ''
                        attributes.append(item_dict)
                        if item['name'] == '品牌':
                            base['brand'] = item['value']
                else:
                    pass

            if not images:
                images = data2['globalData'].get('images')
            variableList = []
            sku_img_dict = {}
            dict_item = {}
            if offerDomain:
                data3 = json.loads(offerDomain)
                # 年限
                tpYear = data3['sellerModel'].get('tpYear')
                base['business_years'] = tpYear
                base['location'] = data3['detailDescription']['freightInfo'].get('location')

                if not price_range:
                    price_range = data3['sellerModel'].get('priceDisplay')
                if not skuProps1:
                    skuProps1 = data3['sellerModel'].get('skuMap')
                weight = data3['detailDescription']['freightInfo'].get('unitWeight')
                base['weight_value'] = weight
                detailUrl = data3['offerDetail']['detailUrl']
                offer_details_re = get_desc(detailUrl)
                offer_details = offer_details_re[0] if offer_details_re else ''
                detail_content = ''
                if offer_details:
                    if 'content' in str(offer_details):
                        offer_details_dic = json.loads(offer_details)
                        detail_content = offer_details_dic['content']
                    else:
                        detail_content = offer_details
                descriptionTextlist = []
                for attr in attributes:
                    infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=attr['pkey'], value=attr['pval'])
                    descriptionTextlist.append(infostr)
                descriptionText = ''.join(descriptionTextlist)  # '<ul>' + ''.join(descriptionTextlist) + '</ul>'

                extension = {
                    "description": '',
                    "descriptionText": descriptionText
                }
                extension['description'] = descriptionText + str(detail_content).replace("var desc='", '')

                for item in data3['offerDetail']['skuProps']:
                    for ite in item['value']:
                        dict_item[ite['name']] = item['prop']
                        if ite.get('imageUrl'):
                            sku_img_dict[ite['name']] = ite['imageUrl']

                for item in data3['tradeModel']['skuMap']:
                    sku_dict = {}
                    # print(item)
                    base_i = {
                        "currency": "CNY",
                        "price": item.get("price"),
                        "priceRange": item.get("price"),
                        "productId": item["skuId"],
                        "sales": item["saleCount"],
                        "stock": item["canBookCount"],
                        "title": title,
                    }
                    attributes_i = []
                    sku_images = []
                    for i in str(item["specAttrs"]).split('&gt;'):
                        # print(i)
                        sku_attr_data = {
                            'pkey': dict_item[i] if i in dict_item else '',
                            'productId': item["skuId"],
                            'pval': i,
                            'unit': '',
                        }
                        if i in sku_img_dict:
                            sku_attr_img = {"imgUrl": sku_img_dict[i], "type": 3}
                            if sku_attr_img not in sku_images:
                                sku_images.append(sku_attr_img)
                        attributes_i.append(sku_attr_data)
                    sku_dict['attributes'] = attributes_i
                    sku_dict['base'] = base_i
                    sku_dict['images'] = sku_images

                    variableList.append(sku_dict)
            img_list = []
            for i, img in enumerate(images):
                img_dict = {}
                if i == 0:
                    img_dict['type'] = 0
                else:
                    img_dict['type'] = 2
                img_dict['imgUrl'] = img
                img_list.append(img_dict)

            base['title'] = title
            base['productId'] = productId
            base['priceRange'] = str(price_range).replace('-', '~')
            base['sales'] = saledCount
            data['images'] = img_list
            data['variableList'] = variableList
            data['extension'] = extension
            data['base'] = base
            data['attributes'] = attributes
            data['is_valid'] = 1
            data['extra_data'] = []
            data['extra'] = ""
            return data
        else:
            return ''
