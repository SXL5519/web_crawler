"""
爬取福彩官网双色球历史开奖数据到csv文件
"""
import ast

import configHttp


a=configHttp.ConfigHttp()
a.set_url("/cwl_admin/kjxx/findDrawNotice")
# a.convert_set_params({'name':'ssq','dayStart':'2017-10-24','dayEnd':'2019-02-11','pageNo':n})
a.convert_set_headers({'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
                           'Referer':'http://www.cwl.gov.cn/kjxx/ssq/kjgg/'})
# print(a.get().url)
# q=a.get().text
# print(q)
name = ['期数','red_1', 'red_2', 'red_3', 'red_4', 'red_5', 'red_6', 'blue']  ###列名
re_n='"code":"(.*?)".*?"red":"(.*?)","blue":"(.*?)"'
# a.re_data(re_n, q)
# a.write_csv(a.re_data(re_n, q),name,'union_lotto')
for n in range(1,10000):
    a.convert_set_params({'name': 'ssq', 'dayStart': '2005-02-11', 'dayEnd': '2019-02-11', 'pageNo': n})
    q = a.get().text
    # print(q)
    if ast.literal_eval(q).get('state')==1:
        break
    a.write_csv(a.re_data(re_n, q), name, 'union_lotto',n)






