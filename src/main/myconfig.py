# '''
# Created on 2017/6/22 10:05
# 
# @author: Gaolijun
# '''
"""单独的配置模块，用于设置headers等全局配置信息"""
#设置头文件，随机选取
import os
ualst = [{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'},
             {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
             {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
             {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
             {'User-Agent':'ozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
             {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}]


if __name__ == '__main__':
   #去掉任意位置的空格测试
   import re
   p = re.compile(r'[\s\r\n\t]*')
   a = re.sub(p, '', 'aiodw  23  2ir')
   print(a)