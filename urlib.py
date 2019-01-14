import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#
# # respone = urllib.request.urlopen('https://yqltest.godteam.net/#/')
# respone = urllib.request.urlopen('https://www.baidu.com/')
# print('源码：\n'+respone.read().decode('utf-8'))
# print('状态码：'+str(respone.status))
# print('请求头：\n'+str(respone.getheaders()))

from urllib.robotparser import RobotFileParser
from urllib.request import urlopen

rp = RobotFileParser()
rp.parse(urlopen('http://www.jianshu.com/robots.txt').read().decode('utf-8').split('\n'))
print(rp.can_fetch('*', 'http://www.jianshu.com/p/b67554025d7d'))
print(rp.can_fetch('*', "http://www.jianshu.com/search?q=python&page=1&type=collections"))


# from urllib.robotparser import RobotFileParser
#
# rp = RobotFileParser()
# rp.set_url('http://www.jianshu.com/robots.txt')
# rp.read()
# print(rp.can_fetch('*', 'http://www.jianshu.com/p/b67554025d7d'))
# print(rp.can_fetch('*', "http://www.jianshu.com/search?q=python&page=1&type=collections"))