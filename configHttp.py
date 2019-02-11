#-*- coding:utf-8 -*-
"""
配置接口请求方法
"""
import ast
import re
import csv

import os
import requests

import json


class ConfigHttp():

    def __init__(self):
        # localReadConfig = readConfig.ReadConfig()
        global host, port, timeout
        # host = localReadConfig.get_http("baseurl")
        # port = localReadConfig.get_http("port")
        # timeout = float(localReadConfig.get_http("timeout"))
        host='http://www.cwl.gov.cn'
        port=''
        timeout=''
        ###将字符串转化成字典
        # headers = ast.literal_eval(localReadConfig.get_http("headers"))
        self.params = {}
        self.data = {}
        # self.data = json.dumps({})
        self.url = None
        self.files = {}
        self.headers={}

    def set_url(self, url):
        """
        组装URL
        :param url:
        :return:
        """
        self.url = host + url
        # print(self.url)
        # return self.url

    def set_headers(self, header):
        self.headers = ast.literal_eval(header)

    def convert_set_headers(self,headers):
        self.headers=headers

    def set_params(self, param):

        self.params = ast.literal_eval(param)

    def convert_set_params(self, param):
        self.params = param

    def set_data(self, data):
        """
        组装data ，需要改变变量类型
        :param data:
        :return:
        """
        self.data =ast.literal_eval(data)

    def convert_set_data(self, data):
        """
        组装修改后的data ，不需要改变变量类型
        :param data:
        :return:
        """
        self.data =data

    def set_files(self, file):
        """
        上传文件接口，组装file
        :param file:
        :return:
        """
        self.files = ast.literal_eval(file)

    # defined http get method
    def get(self):
        try:
            response = requests.get(self.url, params=self.params,headers=self.headers)
            # response.raise_for_status()
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

    # defined http post method
    def post(self):
        try:
            response = requests.post(self.url,data=self.data,headers=self.headers,timeout=timeout)
            # response.raise_for_status()
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

    def write_csv(self,data,name,filename,n):
        """
        将爬取的数据写入CSV文件
        :param data:写入的数据
        :param name:csv文件列名
        :param filename:csv文件名
        :return:
        """
        list1=[]
        if n==1:
            if os.path.exists('./data_file/'+filename+'.csv'):
                os.remove('./data_file/'+filename+'.csv')
        with open('./data_file/'+filename+'.csv', 'a+',newline='') as f:
            csv_write = csv.writer(f)
            if n==1:
                csv_write.writerow(name)
            for i in data:
                print(i)
                list1.append(str(i[0]))
                for j in i[1].split(','):
                    list1.append(j)
                list1.append(str(i[2]))
                csv_write.writerow(list1)
                list1=[]

    def re_data(self,i,data):
        """

        :param i: 正则表达式
        :param data: 匹配的数据
        :return: 匹配成功的数据
        """
        re_str = re.compile(i)
        re_data=re_str.findall(data)
        # print(re_data)
        return re_data


