'''
@author: wangjunjie
@contact: wang.junjie@trs.com.cn
@file: duowantuku.py
@time: 2018/9/17 15:20
@desc: 爬取多玩图库图片：https://blog.csdn.net/tinyguyyy/article/details/79404026

'''
import json
import os
import re
import time
import requests
import pymysql


def strip(path):
    path = re.sub(r'[?\\*|"<>:/]', '', str(path))
    return path


# 爬虫类
class Spider:
    # 初始化函数
    def __init__(self):
        self.session = requests.session()

    # 下载图片
    def download(self, url):
        try:
            return self.session.get(url)
        except Exception as e:
            print(e)

    # 从start_url开始获取全部的套图入口，并逐个获取套图信息，最终保存图片
    def run(self, start_url):
        # 获取全部的套图入口id
        img_ids = self.get_img_ids(start_url)
        # print(img_ids)
        # 并逐个获取套图信息，最终保存图片
        for img_id in img_ids:
            # 获取套图json信息
            img_item_info = self.get_img_item_info(img_id)
            print(img_item_info)
            self.save_img(img_item_info)
            # exit()#仅循环一次

    # 下载html代码，并从中筛选出套图入口id，返回套图id列表
    def get_img_ids(self, start_url):
        response = self.download(start_url)
        if response:
            html = response.text
            # print(html)
            # 正则仍然有待学习
            ids = re.findall(r'http://tu.duowan.com/gallery/(\d+).html', html)
            return ids

    # 为了拿到json数据，我们观察文件中存在两个数字，一个是套图入口id我们已知，另一个是时间戳，可以仿制
    def get_img_item_info(self, img_id):
        # http://tu.duowan.com/index.php?r=show/getByGallery/&gid=125658&_=1519643852451
        img_item_url = "http://tu.duowan.com/index.php?r=show/getByGallery/&gid={}&_={}".format(img_id,
                                                                                                int(time.time() * 1000))
        # 下载后解析得到可用的json数据
        response = self.download(img_item_url)
        if response:
            return json.loads(response.text)

    # 套图信息持久化
    def save_img(self, img_item_info):
        # 以套图标题创建文件夹保存套图
        dir_name = img_item_info['gallery_title']
        # 字符串剪切去掉无法做文件夹的字符串
        strip(dir_name)
        print(dir_name)
        # 创建文件夹
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        # 获取图片名，图片url，图片后缀，保存图片路径等
        for img_info in img_item_info['picInfo']:
            img_name = img_info['title']
            strip(img_name)
            img_url = img_info['url']
            pix = (img_url.split('/')[-1]).split('.')[-1]
            img_path = os.path.join(dir_name, "{}.{}".format(img_name, pix))  # 此处路径拼接避免出现字符串问题
            print(dir_name, img_name, img_path)
            # 保存图片至本地
            if not os.path.exists(img_path):
                response = self.download(img_url)
                if response:
                    print(img_url)
                    img_data = response.content
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
        ''' # 在本地数据库中插入记录
         db = pymysql.connect("localhost", "root", "123456", "python", use_unicode=True,
                              charset="utf8");  # 此处会出现编码问题
         cursor = db.cursor()
         try:
             sql = "INSERT INTO img (dir_name,img_title,img_path) VALUE (%s,%s,%s);"  # 此处写法可以避免转义问题
             cursor.execute(sql, (dir_name, img_name, img_path))
             db.commit()
         except Exception as e:
             print(e)
             db.rollback()
         db.close()'''


if __name__ == '__main__':
    spider = Spider()
    spider.run('http://tu.duowan.com/tag/5037.html')
    # spider.download('http://tu.duowan.com/gallery')
