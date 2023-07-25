# -*- coding: utf-8 -*-
import itertools
from functools import reduce
import random
import re, os.path, time, urllib.parse

from App.common.webRequest import WebRequest
from Configs import defaultApp
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from scrapy.selector import Selector
from App.common.url.baseUrlHandle import baseUrlHandle
import json, gevent
from App.service.system.classContextService import classContextService
from lxml import etree

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import demjson
import requests
import hashlib
import datetime

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_discount_price(itemid, sellerid):
    url = 'https://detailskip.taobao.com/service/getData/1/p2/item/detail/sib.htm?itemId={}&sellerId={}&modules=dynStock,qrcode,viewer,price,duty,xmpPromotion,delivery,activity,fqg,zjys,amountRestriction,couponActivity,soldQuantity,page,originalPrice,tradeContract&callback=onSibRequestSuccess'.format(
        itemid, sellerid)
    headers = {
        "referer": "https://item.taobao.com/item.htm?ft=t&id={}".format(itemid)}
    resp = requests.get(url, headers=headers)
    discount_price_data = re.search('onSibRequestSuccess\(({[\s\S]*?})\)', resp.text).group(1)
    return discount_price_data

# def get_sku_mapping(HTML):
#     sku_mapping = {}
#     sku_xpath = HTML.xpath("//div[@class='tb-skin']/div[@class='tb-sku']")[0]
#     ns = {"re": "http://exslt.org/regular-expressions"}
#     qqq = sku_xpath.xpath("//dl[re:match(@class,'tb-prop tm-sale-prop tm-clear.*?')]", namespaces=ns)
#     if qqq:
#         propid = []
#         propval = []
#         for qqq_i in qqq:
#             prop_a_id = qqq_i.xpath('./dd//li/@data-value')
#             prop_a_k = qqq_i.xpath('./dt/text()')
#             prop_a_v = qqq_i.xpath('./dd//li/a/span/text()')
#             propid.append(prop_a_id)
#             propval.append(list(itertools.product(prop_a_k, prop_a_v)))
#
#         fn = lambda x, code=';': reduce(lambda x, y: [str(i) + code + str(j) for i in x for j in y], x)  # 多列表组合
#         tt = fn(propid)
#         tt1 = fn(propval)
#         mapping_data = tuple(zip(tt, tt1))
#         for i in mapping_data:
#             sku_mapping.update({i[0]: i[1]})
#         print(json.dumps(sku_mapping))
#     return sku_mapping

def get_sku_img_mapping(Html):
    sku_img_mapping = {}
    img_a_k = Html.xpath('//ul[@class="tm-clear J_TSaleProp tb-img     "]/li/@data-value')
    img_a_v = Html.xpath('//ul[@class="tm-clear J_TSaleProp tb-img     "]/li/a/@style')
    img = tuple(zip(img_a_k, img_a_v))

    for i in img:
        k = str(i[0])
        v = 'https:' + i[1].replace('background:url(', '').replace(')', '').replace(' center no-repeat;', '')
        sku_img_mapping.update({k: v})

    return sku_img_mapping


def filliter(infolist):
    infolist = [x.strip() for x in infolist if x.strip() != '']
    return infolist


def get_desc(itemid):
    url = 'https://mdetail.tmall.com/templates/pages/desc?id={}'.format(itemid)
    resp = requests.get(url, timeout=5)
    descUrldata = re.search('Desc.init\((.*?)\);', resp.text).group(1)
    try:
        descUrl = json.loads(descUrldata)['TDetail']['product_tasks']['descUrl']
    except KeyError:
        descUrl = json.loads(descUrldata)['TDetail']['api']['descUrl']
    imginfo_data = requests.get("https:" + descUrl, timeout=5)
    return imginfo_data


class ccTmallCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Tmall'

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
     # 保存文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月16日 10:11:43
    """

    def saveHtmlResult(self, url):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()
        # itemid = re.search("http.*?id=(\d+)", url).group(1)  # 淘宝的id
        itemid = re.search("detail.tmall.*?id=(\d+).*?", url)  # 天猫的id
        if itemid:
            itemid = itemid.group(1)
        else:
            itemid = re.search("item/(\d+).*?", url).group(1)
        md5str = str(itemid)
        itemid_validity = commonRedisClass.zscoreValByKey('tmall_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.taobao_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/tmall_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='tmall_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data= data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
        headers = {
            'Cache-Control': 'no-cache',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'Content-type:text/html;charset=gbk'
        }
        header = {
            "Accept": "*/*",
             "accept-language": "zh-CN,zh;q=0.9",
             "Connection": "keep-alive",
             "Accept-Encoding": "gzip, deflate, br",
             "Content-Type": 'Content-type:text/html;charset="gbk"',
            'referer': url,
            "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "cache-control": "max-age=0",
            "cookie":'lid=tb076241109; _uab_collina=163299421907049226797254; cna=3PuUGdKY8BoCAQ4Su3ut40eh; hng=CN%7Czh-CN%7CCNY%7C156; enc=ZNFbsA91tUYmFq7a5Pghd4YcxEDSHOf4hnJYPjPBV6fiqt3KGYEoY9sKY0cOKpEFN5NCdvBh1tG19xG4kNCjbQ%3D%3D; sgcookie=E100g%2BCMfG6%2Bz8vBnS8CxtlPJYz8UwLuFDLs2DAgQBQvN5CcErQmK0aZHByUhUJFge8wO%2BAWsfUUpWzU53a96SuWQ5dasTcCSer2L66RTZV36gc%3D; uc3=nk2=F5RFh6jNB14tcWw%3D&vt3=F8dCujaOWgLG7AmNuJI%3D&id2=UNk1%2Br2BfHAWow%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D; t=86f42b4215d41a90ed598665aea1f281; tracknick=tb076241109; uc4=id4=0%40Ug4%2FEBPRLzVMHptqkHXrMTyfHkXT&nk4=0%40FY4O7oHcpA52ZeBDzVoDiyLpBf1oAg%3D%3D; lgc=tb076241109; _tb_token_=efa4053eeebb3; cookie2=14d3aca12e2dbf4ea5d28c87baf5cb54; pnm_cku822=098%23E1hva9vUvbpvjQCkvvvvvjiWPsFwgjYUPsShQjnEPmPZ6jiRPsFW6jlRn2FpzjGvvpvVvvpvvhCvmvhvLCoGa9vjOezva70Adch%2BafmBDXTAVA1lMn2Ie3O0747B9Wma%2BoHoDO2hT2eAnhjEKOmxdB9aUEVYFa70%2Bkt4fXxr18TKfvDr1jc6hfRUvpvVmvvC9jDnuvhvmvvv92q9UYlxKvhv8vvvvWivpv2hvvvmQ6Cv2jpvvUnvphvpgvvv96CvpCCvvvvmA6Cv2nZRvpvhMMGvv29Cvvpvvvvvi9hvCvvv9UU%3D; xlly_s=1; cq=ccp%3D1; l=eBIrxzrlgibD_JQ9BOfZhurza77TGIRRguPzaNbMiOCP9vf65-FGW6UAVuLBCnGVnsdB-37c4VqbBuYZ_yUQCCqPK2Bn9MptndLh.; tfstk=cyjVBQj81oE2Yt-_JntafWPofsvAZlXcI0JBoZ0mN-jIsH8ci-l9EQEpUdMrsEf..; isg=BEJCPC_sl239bosUP2AIvZD_k0ikE0YtNgIiH4xbBLVg3-ZZdqAOPSSVj9ujj77F'
            # "cookie":'cookie2=13f7e5447cb233ac2d003d7182963feb; t=b331b20d250742b9d7ac417f18039d57; dnk=tb3626600441; tracknick=tb3626600441; lid=tb3626600441; lgc=tb3626600441; uc3=lg2=Vq8l%2BKCLz3%2F65A%3D%3D&vt3=F8dCuw%2B4P%2BCToDBmJqw%3D&id2=UUpgR1rYxL2AbnwTRA%3D%3D&nk2=F5RGMOX%2Bfz58eGA%2F; uc4=id4=0%40U2gqyOcIU%2FDbq%2FA3bAFpula4TqMXzWaV&nk4=0%40FY4NBf2jAL6VqKG%2BFjGqzF8Ewg1jbRM%3D; sgcookie=E100u0hoSp%2Fe7R6zowADSLPNgv9smvnQWc8MUzDoXq6YuT7MWWnyPmSFN2%2F3UsgFY6Qygv1UA0TF8O%2F7XiEeYJSNlA%3D%3D; csg=5edac6c5; cq=ccp%3D1; miid=1893390951611830938; OZ_SI_2061=sTime=1623202995&sIndex=2; OZ_1U_2061=vid=v0c01cb4e97791.0&ctime=1623203327&ltime=1623202995; tk_trace=oTRxOWSBNwn9dPyorMJE%2FoPdY8zMG1aAN%2F0TkjYGZjkj6rrK3kv4LgxGhtlxvv2n251iRZBLi5%2BxLVnyk1ChK8mK8ScbDSNcQjoBw4CuKe4IDNRXt8LcPvqEu99OadCWFwfRJefa4s24U%2F77HCnAuEDYu8i0tsQUBHcT%2FWZWey3jB3lNcWANzXgP%2Bf4H7W8fUkkVYIRO7NcqAaF8Qaz82KbsMQZfwba8JgJZeBAVwwBGb7I5LiRiQi9ef%2BqX4Fw9J%2Bqw4Hu8OMhwksC2eqolNv%2BNxMCs7b4kwohvIxSg%2Bd4Qg5VVjUpJ1hlk1oiNsUydhSGvOHMYJNuXx5Y6Wk3LPdfpVpGF32Nyg%2Fbm%2BcGc5nVvLaXPsFTKT3%2BvvCvbteFu%2BR%2B9hKmcbMdNqwjOS0a9wdB04Jz4ZtT7k6gqxm6R6CkkDDpqeM8n6zYdhSdQA63nAKzBWN1VkLHk6XBu1hlu6N2BCszBUPPlS8yNO25Nz8zdQoGpxmJYE65VeBh0geDr%2Fl73uT6OyHe4scslPLb7N2Rn8Ldx0MFYUsZAzGH%2BtJQAepj%2F4DvGJVLu%2FMStw82qmZWy4JdWt5veH%2B19xzI%2FKweT0Zf2Gf49kEJ6fqvOQhwcLwnIvZCpCFuA1%2Fn%2Fg5oPwQ2%2FUPChoYIPsL7awUQjUm4deb%2F9nC8e9AtX7wUjwa3LPncd6KDlIF8gX%2Fcqhebs7Q%3D%3D; uc1=cookie21=U%2BGCWk%2F7oPIg&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&existShop=false&pas=0&cookie14=Uoe2ySRDICOg8A%3D%3D; enc=gIexrHr9S3HCRF1CZk742DhQ3ZADJz4c%2BSgA7PoMlXR7y4N%2BBtFgLn9hN9qMFxWG%2FdSgt7c2cIuvQlz9vYrw9mVIYQoECENZTEgy75plZ8g%3D; _gcl_au=1.1.1701018880.1624859459; _tb_token_=0e8ae57d8353; cna=dXVhGdHcdVgCAQ4Su3v3yv3j; _uab_collina=163158857615630202651977;xlly_s=1; pnm_cku822=098%23E1hvnQvUvbpvUvCkvvvvvjiWPsz90jDCnLqy0j1VPmPpAjYnPsSWtjnHR2dv6j1bRvhvCvvvvvvRvpvhvv2MMQ9CvhQh62pvCsN%2BFOcn%2B3Cgp%2Bex6aZtn0vHfJBlYEkJNZmxfaClHdBYVVzyaNQwV5avTn2OsCy7nDeDyO2v5fh3Zi7vtR9t%2BFBCAfevD404kvhvC99vvOCtou9Cvv9vvUmY%2Bkee5d9Cvm9vvv2HphvvRvvvvsEvpvFNvvm2phCvhRvvvUnvphvppvvvvsivpvAYvvhvC9vhvvCvp8OCvvpvvUmm; tfstk=chtlB0DfSU7SHCbD50sWUJnDQwhOZUrFsH-X0HFShyLf3OtVi5447dzin_Akvy1..; l=eBSxFQlrj3ri820LBOfZFurza779QIRVguPzaNbMiOCPO2f65WS5W6F-wnYBCnGVnsMWR3kQee-kB-YuFyUQhegpqXBn9Mpt3ddC.; isg=BBYWuP2Da6WcBV79izfpX3nmZ8wYt1rxzLJTgYB_EfmUQ7Td6EKGAc-x39-va1IJ',
        }
        for useType in '0123':
            header['USETYPE'] = useType
            header['user-agent'] =  userAgent().getPc()
            header['TARGETURL'] = url
            # print(url)
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)
                html = result.text(self=WebRequest)
                print(len(html))
                if len(html)<5000:
                    requests.packages.urllib3.disable_warnings()
                    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
                    try:
                        requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
                    except AttributeError:
                        # no pyopenssl support used / needed / available
                        pass
                    response = requests.get(url,
                                            headers={
                                                "Accept": "*/*",
                                                "accept-language": "zh-CN,zh;q=0.9",
                                                "Cookie": "_tb_token_=75b36f1368339; cookie2=18bb0897b7b3f75d648c900e1dd3773f; t=18a38971630645bfbcef435698d850d1",
                                                "Connection": "keep-alive",
                                                "Accept-Encoding": "gzip, deflate, br",
                                                "Content-Type": 'Content-type:text/html;charset="gbk"',
                                                # "authority": "detail.tmall.com",
                                                "cache-control": "max-age=0",
                                                "referer": url,
                                                "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
                                                "sec-ch-ua-mobile": "?0",
                                                "sec-fetch-dest": "document",
                                                "sec-fetch-mode": "navigate",
                                                "sec-fetch-site": "same-origin",
                                                "sec-fetch-user": "?1",
                                                "upgrade-insecure-requests": "1",
                                                "user-agent": userAgent().getPc()#"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
                                            },
                                            cookies={
                                                "OZ_1U_2061": "vid=v0c01cb4e97791.0&ctime=1623203327&ltime=1623202995",
                                                "OZ_SI_2061": "sTime=1623202995&sIndex=2",
                                                "_gcl_au": "1.1.1701018880.1624859459",
                                                "_tb_token_": "0e8ae57d8353",
                                                "_uab_collina": "163158857615630202651977",
                                                "cna": "dXVhGdHcdVgCAQ4Su3v3yv3j",
                                                "cookie2": "13f7e5447cb233ac2d003d7182963feb",
                                                "cq": "ccp%3D1",
                                                "csg": "5edac6c5",
                                                "dnk": "tb3626600441",
                                                "enc": "gIexrHr9S3HCRF1CZk742DhQ3ZADJz4c%2BSgA7PoMlXR7y4N%2BBtFgLn9hN9qMFxWG%2FdSgt7c2cIuvQlz9vYrw9mVIYQoECENZTEgy75plZ8g%3D",
                                                # "isg": "BAIC_-1V158z3sq5R1OF0-1aUwhk0wbtYKAdn0wbLnUin6IZNGNW_YhdT5vjz36F",
                                                # "l": "eBSxFQlrj3ri8A9kKOfwourza77OSIRAguPzaNbMiOCP_uf656kfW6FVCYLBC3GVh6qDR3SW3fIbBeYBqo2pBkyca6Fy_Ckmn",
                                                "lgc": "tb3626600441",
                                                "lid": "tb3626600441",
                                                "miid": "1893390951611830938",
                                                "pnm_cku822": "098%23E1hvkpvUvbpvUvCkvvvvvjiWPszwzjiPR2Fh0jthPmPZ1jDER2dpAjlRR2SyQjnmi9hvCvvvpZpgvpvhvvCvpvvCvvOv9hCvvvvUvpCWvCUxHBz1VEoaWLEc340a%2BfmtEpcpTEvsKFwFxT7Yn1pTHkGVqw0qr2u18vmYib01%2BbyDCw2IRfUTKFEw9E7reuTx46JDYEkOjCrQcb9Cvm9vvhv0vvvvMvvvpFvvvvjqvvCj1Qvvv3QvvhNjvvvmmvvvBFUvvUVzuvhvmvvvpLuziV7skvhvC9hvpyPyAvgCvvpvvPMM",
                                                "sgcookie": "E100u0hoSp%2Fe7R6zowADSLPNgv9smvnQWc8MUzDoXq6YuT7MWWnyPmSFN2%2F3UsgFY6Qygv1UA0TF8O%2F7XiEeYJSNlA%3D%3D",
                                                "t": "b331b20d250742b9d7ac417f18039d57",
                                                # "tfstk": "cnrGB3XIrPusp003PGi_QB2ZVTBdZttqZorQYoprxTls-VrFiQYez88lKfVgDE1..",
                                                "tk_trace": "oTRxOWSBNwn9dPyorMJE%2FoPdY8zMG1aAN%2F0TkjYGZjkj6rrK3kv4LgxGhtlxvv2n251iRZBLi5%2BxLVnyk1ChK8mK8ScbDSNcQjoBw4CuKe4IDNRXt8LcPvqEu99OadCWFwfRJefa4s24U%2F77HCnAuEDYu8i0tsQUBHcT%2FWZWey3jB3lNcWANzXgP%2Bf4H7W8fUkkVYIRO7NcqAaF8Qaz82KbsMQZfwba8JgJZeBAVwwBGb7I5LiRiQi9ef%2BqX4Fw9J%2Bqw4Hu8OMhwksC2eqolNv%2BNxMCs7b4kwohvIxSg%2Bd4Qg5VVjUpJ1hlk1oiNsUydhSGvOHMYJNuXx5Y6Wk3LPdfpVpGF32Nyg%2Fbm%2BcGc5nVvLaXPsFTKT3%2BvvCvbteFu%2BR%2B9hKmcbMdNqwjOS0a9wdB04Jz4ZtT7k6gqxm6R6CkkDDpqeM8n6zYdhSdQA63nAKzBWN1VkLHk6XBu1hlu6N2BCszBUPPlS8yNO25Nz8zdQoGpxmJYE65VeBh0geDr%2Fl73uT6OyHe4scslPLb7N2Rn8Ldx0MFYUsZAzGH%2BtJQAepj%2F4DvGJVLu%2FMStw82qmZWy4JdWt5veH%2B19xzI%2FKweT0Zf2Gf49kEJ6fqvOQhwcLwnIvZCpCFuA1%2Fn%2Fg5oPwQ2%2FUPChoYIPsL7awUQjUm4deb%2F9nC8e9AtX7wUjwa3LPncd6KDlIF8gX%2Fcqhebs7Q%3D%3D",
                                                "tracknick": "tb3626600441",
                                                "uc1": "cookie21=U%2BGCWk%2F7oPIg&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&existShop=false&pas=0&cookie14=Uoe2ySRDICOg8A%3D%3D",
                                                "uc3": "lg2=Vq8l%2BKCLz3%2F65A%3D%3D&vt3=F8dCuw%2B4P%2BCToDBmJqw%3D&id2=UUpgR1rYxL2AbnwTRA%3D%3D&nk2=F5RGMOX%2Bfz58eGA%2F",
                                                "uc4": "id4=0%40U2gqyOcIU%2FDbq%2FA3bAFpula4TqMXzWaV&nk4=0%40FY4NBf2jAL6VqKG%2BFjGqzF8Ewg1jbRM%3D",
                                                "xlly_s": "1"
                                            },
                                            auth=(),
                                            )
                    html = response.text
                    print(3333,len(html))
                if len(html) < 5000:
                    continue
                data = self.setResult(html, url)  # 洗完的结构
                print(666, json.dumps(data))
                if data:
                    self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                    commonElasticSearchClass.insertDataByIndexKey(index='tmall_info', id=md5str, data=data)
                    commonRedisClass.insertDataByIndexKey(redisKeyName='tmall_info', redisStr=md5str)
                    self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                else:
                    continue

                return
            except Exception as e:
                print(e)

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
                "size": '',  # 尺寸
                "describe": "",  # 描述评分
                "service": "",  # 服务评分
                "logistics": ""  # 物流评分
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

        all_data_re = re.search("TShop\.Setup\(([\s\S]*?)\);", sourceHtml)
        if all_data_re == None:
            print('获取数据1失败')
            return
        all_data = all_data_re.group(1)

        all_data_dict = json.loads(all_data)

        itemid = str(all_data_dict['rateConfig']['itemId'])
        if itemid:
            data['base']['productId'] = itemid

        title = all_data_dict['itemDO']['title']
        if title:
            data['base']['title'] = title

        mall_id = str(all_data_dict['rstShopId'])
        if mall_id:
            data['base']['mall_id'] = mall_id

        mallLink = ''

        mall_name = ''

        # sellerNick = all_data_dict['itemDO']['sellerNickName']

        sellerid = str(all_data_dict['rateConfig']['sellerId'])

        HTML = etree.HTML(sourceHtml)
        # 品牌
        if '"brand":' in sourceHtml:
            brand = re.findall('"brand":"(.*?)",', sourceHtml)
            data['base']['brand'] = [brand[0] if brand else ''][0]
        # 商家名称
        shop_name = HTML.xpath('//input[@name="seller_nickname"]/@value')
        data['base']['mall_name'] = [shop_name[0] if shop_name else ''][0]
        # 描述评分
        describe = HTML.xpath('//div[@class="main-info"]/div[1]//span[@class="shopdsr-score-con"]/text()')

        data['base']['describe'] = [describe[0] if describe else ''][0]
        # 服务评分
        service = HTML.xpath('//div[@class="main-info"]/div[2]//span[@class="shopdsr-score-con"]/text()')
        data['base']['service'] = [service[0] if service else ''][0]

        #  物流评分
        logistics = HTML.xpath('//div[@class="main-info"]/div[3]//span[@class="shopdsr-score-con"]/text()')
        data['base']['logistics'] = [logistics[0] if logistics else ''][0]

        # 商家年限business_years
        business_years = HTML.xpath('//span[@class="tm-shop-age-num"]/text()')
        data['base']['business_years'] = [business_years[0] if business_years else ''][0]
        # 尺寸
        size_unit = ['m', 'dm', 'cm', 'mm', 'M', 'DM', 'CM', 'MM', '米', '分米', '厘米', '毫米', 'X', '*']

        info2 = []
        descriptionText = ''
        descriptionTextlist = []
        try:

            catPropList = all_data_dict['detail']['bundleItemList'][0]['catPropList']
            for attr_data in catPropList:
                key = attr_data['text']
                value = attr_data['values'][0]['text']
                data_i = {
                    "productId": str(itemid),
                    "pkey": key,
                    "pval": value,
                    "unit": ""
                }
                info2.append(data_i)
                if key == '尺寸' or '规格' in key or '体积' in key:
                    for item in size_unit:
                        if item in value and 'L' not in value:
                            data['base']['size'] = value
                if key == '重量(g)' or key == '重量(kg)' or key == '毛重' or '重量' in key:
                    data['base']['weight_value'] = value
                    if 'kg' in value or 'KG' in value or '千克' in value:
                        data['base']['weight_unit'] = 'kg'
                    elif 'g' in value or 'G' in value or '克' in value:
                        data['base']['weight_unit'] = 'g'
                    elif '公斤' in value:
                        data['base']['weight_unit'] = '公斤'
                infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=key, value=value)
                descriptionTextlist.append(infostr)
                descriptionText =''.join(descriptionTextlist)
        except KeyError:
            propsCut_data_xpath = HTML.xpath('//div[@id="attributes"]')
            if propsCut_data_xpath:
                propsCut_data_name_xpath = propsCut_data_xpath[0].xpath('.//ul[@id="J_AttrUL"]//li/text()')
                info = [i.replace('\xa0', '') for i in propsCut_data_name_xpath]
                for attr_data in info:
                    attr_data = attr_data.replace('：',':')
                    attr_data_i = attr_data.split(':')
                    key = attr_data_i[0]
                    value = attr_data_i[1]
                    data_i = {
                        "productId": str(itemid),
                        "pkey": key,
                        "pval": value,
                        "unit": ""
                    }
                    info2.append(data_i)
                    if key == '尺寸' or '规格' in key or '体积' in key:
                        for item in size_unit:
                            if item in value and 'L' not in value:
                                data['base']['size'] = value
                    if key == '重量(g)' or key == '重量(kg)' or key == '毛重' or '重量' in key:
                        data['base']['weight_value'] = value
                        if 'kg' in value or 'KG' in value or '千克' in value:
                            data['base']['weight_unit'] = 'kg'
                        elif 'g' in value or 'G' in value or '克' in value:
                            data['base']['weight_unit'] = 'g'
                        elif '公斤' in value:
                            data['base']['weight_unit'] = '公斤'
                    infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=key, value=value)
                    descriptionTextlist.append(infostr)
                    descriptionText = ''.join(descriptionTextlist)
                # descriptionText = etree.tostring(propsCut_data_xpath[0]).decode()
        data['extension']['descriptionText'] = descriptionText
        data['attributes'] = info2


        imglist2 = []
        img_xpath = HTML.xpath('//ul[@id="J_UlThumb"]/li/a/img/@src')
        index_img = HTML.xpath('//img[@id="J_ImgBooth"]/@src')
        if index_img:
            index_img = re.findall('_\d+x\d+q\d+.jpg', index_img[0])
            index_img = [index_img[0] if index_img else ''][0]
        else:
            index_img = ''
        if img_xpath:
            images = ['https:' + i for i in img_xpath]
            for i,img in enumerate(images):
                img = re.sub('_\d+x\d+q90.jpg',index_img,img)
                if i == 0:
                    img_i = {
                        "type": "0",
                        "imgUrl":img,
                    }
                else:
                    img_i = {
                        "type": "2",
                        "imgUrl": img,
                    }
                imglist2.append(img_i)
        desc = get_desc(itemid)  # 描述图
        if desc:
            data['extension']['description'] = descriptionText + str(desc.text).replace("var desc='",'')
        #     desc_HTML = etree.HTML(desc.text)
        #     detillimg = desc_HTML.xpath('/html/body//img/@src')
        #     if detillimg:
        #         for i in detillimg:
        #             img_i = {
        #                 "type": "1",
        #                 "imgUrl": i,
        #             }
        #             imglist2.append(img_i)
        data['images'] = imglist2

        discount_price_data = get_discount_price(itemid, sellerid)  # 获取价个库存 bag
        if discount_price_data:
            discount_price_data_dict = json.loads(discount_price_data)
        else:
            print('获取sku价格失败')
            return
        total_stock = discount_price_data_dict['data']['dynStock']['stock']
        data['base']['quantity'] = str(int(total_stock))
        try:
            yuanjia = discount_price_data_dict['data']['promotion']['promoData']['def'][0]['price'].split("-")[0]
            discount_price_data_dict_sku_price = discount_price_data_dict['data']['promotion']['promoData']
        except KeyError:
            yuanjia = discount_price_data_dict['data']['price'].split("-")[0]
            discount_price_data_dict_sku_price = discount_price_data_dict['data']['originalPrice']
            data['base']['priceRange'] = str(discount_price_data_dict['data']['price']).replace('-','~')
        data['base']['price'] = str(float(yuanjia))
        discount_price_data_dict_sku_stock = discount_price_data_dict['data']['dynStock'].get('sku')

        variableList2 = []
        sku_img_mapping = get_sku_img_mapping(HTML)
        #print('sku_img_mapping:',json.dumps(sku_img_mapping))
        skuList = [all_data_dict['valItemInfo'].get('skuList') if all_data_dict.get('valItemInfo') else ''][0]

        #print(44444,json.dumps(skuList))

        prop_mapping = {
            '20509': '尺码',
            '20518': '尺码',
            '20549': '鞋码',
            '1627207': '颜色',
            '-1': '套餐商品',
        }
        if '//div[@class="tb-sku"]/dl':
            pname = HTML.xpath('//div[@class="tb-sku"]/dl/dt/text()')
            pnmb = HTML.xpath('//div[@class="tb-sku"]/dl/dd/ul/li[1]/@data-value')
            for i in tuple(zip(pname, pnmb)):
                v = i[0]
                k = i[1].split(':')[0]
                prop_mapping.update({k: v})
        print(prop_mapping)
        # xpath 获取子标题
        title_li = HTML.xpath('//ul[@class="tm-clear J_TSaleProp tb-img     "]/li')
        title_li_dict = {}

        for titles in title_li:
            title = titles.xpath('./@title')
            title_value = titles.xpath('./@data-value')
            if title and title_value:
                title_li_dict[title_value[0]] = title[0]
        # 获取尺码，构建字典
        dl = HTML.xpath('//dl[@class="tb-prop tm-sale-prop tm-clear "]//li')
        size_dict = {}
        for data_value in dl:
            li_value = data_value.xpath('./@data-value')[0]
            li_name = data_value.xpath('./a/span/text()')[0]
            size_dict[li_value] = li_name

        for sku_i in skuList:
            try:
                price_data = discount_price_data_dict_sku_price[';' + sku_i['pvs'] + ';']
                if type(price_data) == list:
                    price = price_data[0]['price']
                elif type(price_data) == dict:
                    price = price_data['price']
                else:
                    price = ""
            except KeyError:
                price = ""

            try:
                pstock_data = discount_price_data_dict_sku_stock[';' + sku_i['pvs'] + ';']
                if type(pstock_data) == list:
                    pstock = pstock_data[0]['stock']
                elif type(pstock_data) == dict:
                    pstock = pstock_data['stock']
                else:
                    pstock = ""
            except KeyError:
                pstock = ""

            base_i = {
                "productId": sku_i['skuId'],
                "title": sku_i['names'],
                "currency": "CNY",
                "price": price,
                "priceRange": '',
                "stock": str(pstock),
                "sales": 0
            }
            # 优先使用xpath 获取的标题，
            if title_li_dict:
                for value in sku_i['pvs'].split(';'):
                    if value in title_li_dict:
                        base_i['title'] = title_li_dict[value]

            attributes_i = []
            sku_imglist = []
            pvs = sku_i['pvs'].split(';')
            pname = sku_i['names'][:-1].split(' ')

            if pvs[-1] in str(title_li_dict):
                if pname[-1] not in title_li_dict[pvs[-1]]:
                    pname_str = str(pname).replace(pname[-1], title_li_dict[pvs[-1]])
                    pname = eval(pname_str)
                else:
                    pass
            for ii in tuple(zip(pvs, pname)):
                try:
                    img = re.sub('_\d+x\d+q90.jpg','',sku_img_mapping[ii[0]])
                    img_data = {
                        "type": "3",
                        "imgUrl":  img
                    }
                    sku_imglist.append(img_data)
                except:
                    pass
                if ii[0] in str(size_dict):
                    pval = size_dict[ii[0]]

                elif ii[0] in str(title_li_dict):
                    pval = title_li_dict[ii[0]]
                else:
                    pval = ii[1]
                attr_i = {
                    "pkey": prop_mapping[ii[0].split(':')[0]],
                    "productId": str(itemid),
                    "pval": pval,
                    #"pval": ii[1],
                    "unit": ""
                }
                #print('attr_i:',attr_i)
                attributes_i.append(attr_i)
            skudata = {
                "base": base_i,
                "attributes": attributes_i,
                "images": sku_imglist
            }
            variableList2.append(skudata)

        data['variableList'] = variableList2
        print(data)
        return data
        # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
        # result = self.parse_description(desc_req, product_data)
        # result_json = json.dumps(result)
        # sentinelServMaster.lpush(self.item_key, result_json)

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

    pass
