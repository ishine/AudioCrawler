# '''
# Created on 2017/6/16 9:43
# 
# @author: Gaolijun
# '''
import os
import random
import time
import requests
import re
import json
from ximalayaFM import mkDir   #从喜马拉雅模块中引入创建文件夹的函数

#考拉FM类，根据专辑url下载所有音频文件
class KaoLaFM(object):
    def __init__(self,albumurl):
        self.albumUrl = albumurl  #专辑所在URL
        self.id = 0  #获取playURL需要的参数ID
        self.header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
    'Host':'www.tingban.cn'}
        self.albumName = ''  #专辑名称
        self.datadict = {}  #定义一个字典，键是音频名称，值是MP3 URL
        self.pagenum = 1    #保存总的页数
        self.count = 0      #专辑总条数

    # 获取id的值
    def get_id(self):
        try:
            html = requests.get(self.albumUrl, headers=self.header)
            pagesource = html.text
            idpattern = re.compile(r'<input id="albumID" type="hidden" value="(.*)"')  # 获取ID的模式
            albumnamep = re.compile(r'<h1 class="zj_title mb4">(.*)</h1>')   #获取专辑名称的模式
            id = re.search(idpattern, pagesource).group(1)
            albumname = re.search(albumnamep,pagesource).group(1)
            self.id = id
            self.albumName = albumname
            print('id 和专辑名称：%s已获取' % self.albumName)
        except requests.exceptions.BaseHTTPError as e:
            print('获取ID和专辑名称失败',e)
        finally:
            time.sleep(random.choice(list(range(1, 5)))/10)

    #获取mp3playURL
    def getMp3PlayUrl(self,curpage,pagesize=50):
        '''

        :param pagenum: 当前页数
        :param pagesize: 每页显示条数，网站默认20，限制最多50
        :return:
        '''
        dataurl = 'http://www.tingban.cn/webapi/audios/list'  #所有data的url前缀都是这个
        params = {
            'id': self.id,
            'pagesize': pagesize,
            'pagenum': curpage,
            'sorttype': 1
        }
        resp = requests.get(dataurl, params=params, headers=self.header)
        resData = json.loads(resp.text)['result']
        dataLst = resData['dataList']  # 所有章节音频url所在位置，list里面是字典格式
        self.pagenum = resData['sumPage']      #获取总页数
        self.count = resData['count']  #该专辑总的音频数量

        for data in dataLst:
            audioName = data['audioName']  # 音频名称
            mp3PlayUrl = data['mp3PlayUrl']  # MP3播放地址，据此下载音频
            self.datadict[audioName] = mp3PlayUrl  #保存到字典中，提供调用
        # import pprint
        # pprint.pprint(self.datadict)
        time.sleep(random.choice(list(range(1, 3))))

    #下载音频文件
    def downloadMp3(self, firstfolder):
        '''
        :param firstfolder: 第一级目录，一个专辑一个文件夹，很多专辑有很多文件夹，全部放在firstfolder中，如ximalaya
        :return:
        '''
        self.get_id()  #获取id和专辑名称
        path = mkDir(firstfolder, self.albumName)
        print(path)
        self.getMp3PlayUrl(1)  #先抓取第一页的数据，得到总页数再循环处理
        print('该专辑共有%s条音频，%s页' % (self.count, self.pagenum))  # 打印专辑音频总量和页数信息
        if self.pagenum > 1:   #如果多余一页那就循环处理
            for page in range(2, self.pagenum+1):  #第一页已经处理了，从第二页开始
                self.getMp3PlayUrl(page)  #获取音频url信息
        #根据字典保存的内容进行下载音频
        p = re.compile(r'[\s\r\n\t?？]*')
        for mp3name,mp3url in self.datadict.items():
            try:
                filename = os.path.join(path, re.sub(p,'', mp3name)+'.mp3')
                if os.path.exists(filename):  # 如果文件存在就不需要再下载了
                    print('已存在无需下载%s' % filename)
                    continue
                else:
                    audio = requests.get(mp3url)
                    try:
                        with open(filename, 'wb') as f:
                            f.write(audio.content)
                        print(u'已保存', filename)
                    except Exception as e:
                        print(e,filename)
                        continue
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue

        time.sleep(random.choice(list(range(3))))

if __name__ == '__main__':
    import multiprocessing
    firstfolder = r'F:\audio\kaolaFM'
    albumurllst = ['http://www.tingban.cn/zj/fgQOr3HA.html','http://www.tingban.cn/zj/EWl2MVVE.html']
    for albumurl in albumurllst:
        kaola = KaoLaFM(albumurl)
        th = multiprocessing.Process(target=kaola.downloadMp3, args=(firstfolder,))
        th.start()
        th.join()
    print('done on %s' % time.ctime())
