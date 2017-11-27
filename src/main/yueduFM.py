# '''
# Created on 2017/7/6 10:26
# 
# @author: Gaolijun
# '''
import requests
import os
import re
import time
import random
from myconfig import ualst
from threading import Thread
from queue import Queue
from baselib import mkDir

class YueDuFM:
    def __init__(self):
        self.url = r'http://yuedu.fm/channel/{cnl}/{pg}/'
        self.channeldct = {'1':'悦读','2':'情感','3':'连播','4':'校园','5':'音乐','6':'Labs'}
        self.headers = random.choice(ualst)
        self.articleLst_url_name_q = Queue(30)  #将某一频道的文章列表放入队列，每次30个就好了
        self.quitflag = object()

    def __get_max_page(self,channel):
        channelUrl = self.url.format(cnl=channel, pg=1)  # 频道完整的url
        resp = requests.get(channelUrl, headers=self.headers)
        page_p = re.compile(r'<div class="pg">.*>(\d)</a>.*?下一页</a>',re.S)
        html = resp.text
        page = re.search(page_p,html).group(1)
        return page

    def _get_articleLst_url_name(self,channel,page=1):
        '''
        获取某一频道下指定页文章的url和标题
        :param channel:字典类型，键用于构造频道url，值是频道名称，建立文件夹
        :param page:当前所在页
        :return:
        '''
        channelUrl = self.url.format(cnl=channel,pg=page)  #频道完整的url
        resp = requests.get(channelUrl,headers=self.headers)
        html = resp.text
        url_name_p = re.compile(r'<div class="channel-title">.*?href="(.*?)">(.*?)</a>',re.S)  #文章标题和url
        url_name = re.findall(url_name_p,html)
        # yield  url_name
        for uname in url_name:
            yield  uname  #uname是元祖，第一个为article链接，第二个为article名称

    def get_all_page_article(self,channel):
        '''
        获取当前频道所有文章链接和标题
        :param channel:
        :return:
        '''
        max_page = self.__get_max_page(channel)
        for pg in range(1,int(max_page)+1):
            urlnames = self._get_articleLst_url_name(channel,pg)
            for uname in urlnames:
                self.articleLst_url_name_q.put(uname)
        self.articleLst_url_name_q.put(self.quitflag)

    def downloadAudio_saveArti(self,channelfilepath):
        artiurl_prefix = r'http://yuedu.fm{0}'

        def _download_audio(artihtml,filename):
            if os.path.exists(filename):
                print('已存在无需下载%s'%filename)
            else:
                audiourl_p = re.compile(r'mp3:"(.*?)"',re.S)
                audiourl = artiurl_prefix.format(re.search(audiourl_p,artihtml).group(1))
                res = requests.get(audiourl,headers=self.headers)
                with open(filename,'wb') as f:
                    f.write(res.content)
                print('%s audio is downloaded' %filename)
        def _save_arti(artihtml,filename):
            if os.path.exists(filename):
                print('已存在无需下载%s'%filename)
            else:
                ignore_p = re.compile(r'[="\-\&/><brnspadiquvcltemoh;]')
                article_p = re.compile(r'<div class="item-intro row">(.*?)</div>', re.S)
                article = re.sub(ignore_p, '', re.search(article_p, artihtml).group(1))
                with open(filename,'w',encoding='utf8') as f:
                    f.write(article)
                print('%s article is saved' % filename)

        while True:
            artiUrl_name = self.articleLst_url_name_q.get()  # acticle url and name
            if artiUrl_name is not  self.quitflag:
                artiurl = artiurl_prefix.format(artiUrl_name[0])
                artiname  = artiUrl_name[1]
                filename = os.path.join(channelfilepath,artiname)  #文件名，没有后缀
                artiHtml = requests.get(artiurl,headers=self.headers).text
                th1 = Thread(target=_download_audio, args=(artiHtml,filename+'.mp3'))
                th2 = Thread(target=_save_arti,args=(artiHtml,filename+'.txt'))
                th1.start()
                th2.start()
                th1.join()
                th2.join()
            else:
                break

    def threadStart(self,firstfolder):
        for chnl,title in self.channeldct.items():
            channelfilepath = mkDir(firstfolder,title)  #每个频道创建一个文件夹
            th1 = Thread(target=self.get_all_page_article,args=(chnl,))
            th2 = Thread(target=self.downloadAudio_saveArti,args=(channelfilepath,))
            th1.start()
            th2.start()
            th1.join()
            th2.join()
            print('channel %s is done\n\n' % title)

        print('all done on %s!' % time.ctime())

if __name__ == '__main__':
    firstfolder = r'F:\audio\yueduFM'
    yuedu  =  YueDuFM()
    yuedu.threadStart(firstfolder)