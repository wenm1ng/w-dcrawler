# coding: utf-8
import sys, os
import xlwt

o_path = os.getcwd()
sys.path.append(o_path)


from App import app
from App.crontab.indexCrontab import indexCrontab
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch



def write_excel_xlsx(path, sheet_name, value):
    index = len(value)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '页'+str(sheet_name)
    for i in range(0, index):
        for j in range(0, len(value[i])):
            print(str(value[i][j]))
            sheet.cell(row=i+1, column=j+1, value=str(value[i][j]))
    workbook.save(path)
    print("xlsx格式表格写入数据成功！")




if __name__ == '__main__':
    commonElasticSearchClass = commonElasticSearch()

    kqlData = {
        "query": {
            "bool": {
            }
        },
        "sort": [{
            "base.productId": {
                "order": "asc"
            }
        }],
        # "_source": [],
        "size": 0,
        "from": 0
    }

    for index in range(100):
        index = index +1
        kqlData['size'] = 10000
        kqlData['from'] = (int(index) - 1) * int(kqlData['size'])

        print(kqlData)
        es_data = commonElasticSearchClass.getByEsSearch(index='coupang', KQLdata=kqlData, elasticsearchType=1)

        hits = es_data['hits']['hits']
        value3 = []
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("你好")
        if not hits:
            exit()
        if hits:
            for es_data_i in hits:
                if '_source' not in es_data_i:
                    break
                esDataSource = es_data_i['_source']
                src_url = esDataSource['base']['sourceUrl']
                ee = {
                    "产品ID":esDataSource['base']['productId'],
                    "邮箱":esDataSource['base']['sellerDetailInfo']['repEmail'],
                    "电话":esDataSource['base']['sellerDetailInfo']['repPhoneNum'],
                    "店铺名":esDataSource['base']['sellerDetailInfo']['vendorName'],
                    "卖家名称":esDataSource['base']['sellerDetailInfo']['repPersonName'],
                    "来源链接":esDataSource['base']['sourceUrl']
                }
                value3.append(ee)

        # 先写表头  0行 0列
        sheet.write(0, 0, "产品ID")
        sheet.write(0, 1, "邮箱")
        sheet.write(0, 2, "电话")
        sheet.write(0, 3, "店铺名")
        sheet.write(0, 4, "卖家名称")
        sheet.write(0, 5, "来源链接")

        lst = value3
        # 获取行号
        for i in range(len(lst)):
            # 获取列表的第i个
            dic = lst[i]
            # 把值拿出来转换成列表
            value_lst = list(dic.values())
            # 这就是第几列
            for j in range(len(value_lst)):
                # 三个参数行 列 值
                sheet.write(i + 1, j, value_lst[j])

        workbook.save('coupang卖家信息表'+str(kqlData['from'])+"-"+str(kqlData['size'] * index)+".xls")
        # write_excel_xlsx('coupang卖家信息表'+str(kqlData['from']), kqlData['from'], value3)