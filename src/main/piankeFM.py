# '''
# Created on 2017/7/11 17:13
# 
# @author: Gaolijun
# '''
#ajax加载的页面，不过可以通过构造URL搞定。好的就是音频链接和文字全部都在一页中。
import os
import requests
import random
import json
import re
from threading import  Thread
from myconfig import ualst
from baselib import mkDir
p = re.compile(r'[<>|"℃/?*]+')


class PianKeFM(object):
    def __init__(self):
        """请求参数，一是用于伪装，否则请求非法，无返回数据，二是循环迭代得到数据"""
        self.headers = {'User-Agent':random.choice(ualst)['User-Agent'],
                        'Authorization':'OjIwMTcwNzExMTY0MjAw',
                        'Host':'pianke.me'}
        self.styleLst = {'1':'爱情','2':'故事','3':'旅行','4':'音乐','5':'电影','6':'读诗'}
        # self.pageSize = 10   #每页返回的条数，最大为10，写在url中吧
        self.pageNum = 1 #每次递增 1，从1开始

    def get_one_style(self,fisrtfolder,style):
        """获取一个分类下所有mp3 Url和文本文件"""
        url = 'http://pianke.me/version5.0/ting/listByStyle.php' #三个参数后续传入，或者使用params传入

        def _download_audio(mp3url,filename):
            if os.path.exists(filename):
                print('已存在无需下载%s'%filename)
            else:
                res = requests.get(mp3url)
                with open(filename,'wb') as f:
                    f.write(res.content)
                print('%s audio is downloaded' %filename)

        while True:
            params = {'style': style,
                      'pageNum': self.pageNum,
                      'sort':1,
                      'sig':'75A7B75F646CB27319EE2408E5BEBB07',
                      'pageSize':'9'}
            try:
                resp = requests.get(url,params=params,headers = self.headers)
                jsnres = json.loads(resp.text)
                data = jsnres['data']
                if data:
                    self.pageNum += 1
                    for dt in data:
                        title = re.sub(p,'_',dt['title'])
                        musicUrl = dt['musicUrl']
                        text = dt['text']
                        filename = os.path.join(fisrtfolder,title)
                        #下载音频
                        th = Thread(target=_download_audio,args=(musicUrl,filename+'.mp3'))
                        th.start()
                        th.join()
                        #保存文本
                        if os.path.exists(filename+'.txt'):
                            print('已存在无需下载%s' % (filename+'.txt'))
                        else:
                            with open(filename+'.txt','w',encoding='utf-8') as f:
                                f.write(text)
                            print('%s text is saved' % (filename+'.txt'))
                else:
                    print('style %s is done' % style)
                    break
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    #本想在class中搞个循环下载所有style的音频，不过就这里下载了吧，测试之后也不方便停止啊。
    styleLst = {'1': '爱情', '2': '故事', '3': '旅行', '4': '音乐', '5': '电影', '6': '读诗'}
    fisrtfolder = r'F:\audio'
    fisrtfolder = mkDir(fisrtfolder,'piankeFM')
    pianke = PianKeFM()
    for i in range(1,7):
        pianke.get_one_style(fisrtfolder,str(i))