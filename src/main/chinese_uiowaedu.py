# '''
# Created on 2017/7/5 10:08
# 
# @author: Gaolijun
# '''
#来自中文阅读天地，抓取文字和音频。只一次全部搞下来了.

import requests
from bs4 import BeautifulSoup as BS
import re
import random
import time
from myconfig import ualst
from baselib import *



p = re.compile(r'[\s\r\n\t?？:：\\、]*')   #去掉特殊字符，空格等
p1 = re.compile(r'一一|[?？@#$%^&"\'“”‘’，,。*！!.]+')   #替换为空格


class UiowaEdu(object):
    def __init__(self):
        self.url = r'http://collections.uiowa.edu/chinese/{topic}'
        self.topic = ['topic_beginning.html','topic_intermediate.html','topic_advanced.html'] #three topic,each topic has many units
        self.headers = random.choice(ualst)
    def _get_unitUrl_name(self,topic):
        topicUrl = self.url.format(topic=topic)  #
        resp = requests.get(topicUrl,headers=self.headers)
        html = resp.content #.decode('gb2312')  #如此才不会乱码啊。
        soup = BS(html,"lxml")  #使用bs解析
        tbdy =  soup.find('table',attrs={'width':"749"})  #第一个topic731  后两个749，这个网站一点儿都不标准
        albs = tbdy.find_all('a')
        # print(albs[0]['href'],re.sub(p,'',albs[0].text),len(albs))
        return ([a['href'],re.sub(p,'',a.text)] for a in albs if not a.has_attr('onclick') ) #unit_url_name,生成器，每单元的url和标题

    def _get_lessonUrl_name(self,unitUrl):
        '''
        根据单元url获取课程url（即为音频文字所在的url和课程）
        :return: 一个unit所有的课程url和标题
        '''
        # unitUrl_name = self._get_unitUrl_name()
        # for unitUrl,unitName in unitUrl_name:
        unit = self.url.format(topic=unitUrl)  #这是单元的完整url
        resp = requests.get(unit,headers=self.headers)
        html = resp.content #.decode('gb2312')
        soup = BS(html,'lxml')
        tbl = soup.find('table',attrs={'width':'758','border':'1'})
        tb = tbl.find_all('tr',limit=2)[1].table  #这里要重写
        trs = tb.find_all('tr')
        for i in range(1, len(trs)):
            tds = trs[i].find_all('td')
            if len(tds) == 7:
                try:
                    lessonName = re.sub(p,'',tds[0].text + tds[1].text)
                    lessonUrl = tds[6].a['href'][3:]
                    yield (lessonUrl,lessonName)
                    time.sleep(0.3)
                except Exception as e:
                    print('lessonurl error %s'%e)
                    continue

    def _get_lessonText(self,lessonUrl):
        lesson = self.url.format(topic=lessonUrl)  #完整的lessonUrl
        rsp = requests.get(lesson,headers=self.headers)
        html = rsp.content #.decode('gb2312')  #原网页是gb2312啊
        soup = BS(html,'lxml')
        try:
            ps = soup.find_all('p')
            ptext = [p.text for p in ps]
            text = re.sub(p1,' ','\n '.join(ptext))
            return text
        except Exception as e:
            print('get text error %s' %e)

    def downloadMov(self,firstfolder):  #mov的url即把lessonUrl改为mov即可
        #获取所有单元的url和名称（用于创建文件夹，一个单元一个文件夹）
        def _savemov(lessonUrl,movpath):
            movurl = self.url.format(topic=lessonUrl.split('.')[0] + '.mov')
            resp = requests.get(movurl)
            with open(movpath, 'wb') as f:
                f.write(resp.content)

        unitUrl_name = self._get_unitUrl_name(self.topic[2])  #这里得一个个topic手动更换，就没有通用法则吗?
        for unitUrl,unitName in unitUrl_name:
            unitpath = mkDir(firstfolder,unitName)   #单元文件夹
            #获取该单元下所有课程的url和课程名（音频与文件的名字）
            lessonUrl_name = self._get_lessonUrl_name(unitUrl)
            for lessonUrl,lessonName in lessonUrl_name:
                filename = os.path.join(unitpath,re.sub(p1,'',lessonName))  #没有后缀的文件名，用于保存TXT和mov
                if os.path.exists(filename+'.txt') and os.path.exists(filename+'.mov'):
                    print('已存在无需下载 %s' % filename)
                    continue
                else:
                    try:
                        lessonText = lessonName+'\t'+self._get_lessonText(lessonUrl)
                        #保存文本
                        with open(filename+'.txt','w',encoding='utf8') as f:
                            f.write(lessonText)
                        #保存音频mov
                        if not os.path.exists(filename + '.mov'):_savemov(lessonUrl,filename+'.mov')
                        print('%s lesson finished'%lessonName)
                        time.sleep(1)
                    except Exception as e:
                        print(e)
                        if not os.path.exists(filename+'.mov'):_savemov(lessonUrl, filename + '.mov')
                        if os.path.exists(filename + '.txt'):os.remove(filename+'.txt')
                        continue
            print('%s Unit finished on %s'%(unitName,time.ctime()))


if __name__ == '__main__':
    firstfolder = r'F:\audio\uioedu'
    uiedu = UiowaEdu()
    uiedu.downloadMov(firstfolder)

    # url = r'http://collections.uiowa.edu/chinese/0_intermediate/intermediate_unit17.html'
    # resp = requests.get(url)
    # html = resp.content#.decode('utf8')
    # soup = BS(html, 'lxml')
    # tbl = soup.find('table', attrs={'width': '758', 'border': '1'})
    # tb = tbl.find_all('tr', limit=2)[1].table  # 这里要重写
    # print(tb.text)

    #测试
    # uniturl = r'http://collections.uiowa.edu/chinese/0_intermediate/intermediate_unit12.html'
    # resp = requests.get(uniturl)
    # html = resp.content.decode('gb2312')
    # soup = BS(html,'lxml')
    # tbl = soup.find('table',attrs={'width':'758','border':'1'})
    # print(tbl.find_all('tr',limit=2)[1].table.find_all('tr'))
    # uiedu._get_unitUrl_name()
    # uniturl = r'beginning/beginning_unit01.html'  #测试用
    # uiedu._get_lessonUrl_name(uniturl)
    # lessonurl = 'readings/beginning/b_audio/b_audio_u01/b_audio_u01_02.htm' #测试用
    # print(uiedu._get_lessonText(lessonurl))
    # path =r'C:\Users\THINK\Downloads'
    # uiedu._downloadMov(lessonurl,path+r'\1.mov')
