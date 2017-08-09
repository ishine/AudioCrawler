# '''
# Created on 2017/6/22 11:33
# 
# @author: Gaolijun
#还没有开始爬就被封了，晕.......又可以啦，时而报错，无语啦
# '''
import os
import requests
import json
import re
import time
import random
from myconfig import mkDir,ualst

#有两步，首先得到音频文件的列表，然后得到音频文件的url并下载
class QingTingFM:
    def __init__(self,albumURL,firstfolder):
        self.albumURL = albumURL  #专辑URL
        self.album_name = ''  #专辑名称
        self.path = ''
        self.firstfolder = firstfolder

    def _get_datalst(self):
        '''
        :param albumURL: 专辑url
        :return:
        '''
        dataheader = {
            'User-Agent': random.choice(ualst)['User-Agent'],
            'Host': 'i.qingting.fm',
            'Origin': 'http://www.qingting.fm'}
        albumid = re.search(r'\d+',self.albumURL).group()  #获取id
        #获得总数
        resp = requests.get(self.albumURL)
        html = resp.text
        total_p = re.compile(
            r'<span class="_1QL0".*?<!-- /react-text --><!-- react-text: .*? -->(.*?)<!-- /react-text -->.*?</span>',
            re.S)  # 总条数的匹配模式
        total = re.search(total_p, html).group(1)
        album_name_p = re.compile(r'<h1 class="_3h7q".*?>(.*?)</h1>')
        self.album_name = re.search(album_name_p, html).group(1)  #专辑名称
        page = (lambda x: int(x)// 100 if not int(x)%100 else int(x)//100 + 1)(total) #页数
        print('已获取专辑：{0}，总数{1}，总页数{2}'.format(self.album_name,total,page))
        self.path = mkDir(self.firstfolder, self.album_name)
        print(self.path)
        for p in range(1,page+1):
            dataurl = 'http://i.qingting.fm/wapi/channels/{0}/programs/page/{1}/pagesize/100'.format(albumid,p)  #albumid,page通过前面获得，默认一页100条
            print(dataurl)
            resp = requests.get(dataurl,headers=dataheader)
            try:
                datajsn = json.loads(resp.text)['data']  #datajsn每页包括100条数据
                yield datajsn
            except Exception as e:
                print(e)
                continue


    #获取文件路径和音频名称
    def _get_filepath(self):
        datajsn = self._get_datalst()
        if datajsn:
            for dt in datajsn:
                for data in dt:
                    file_path = 'http://od.qingting.fm/%s' % data['file_path']
                    name = data['name']
                    yield (name,file_path)

    #下载
    def download_ma4(self):
        name_file = self._get_filepath()
        audioheader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
            'Host': 'od.qingting.fm',
            'Connection': 'keep-alive'}
        p = re.compile(r'[\s\r\n\t]*')
        for name,file_path in name_file:
            try:
                filename = os.path.join(self.path, re.sub(p,'',name)+'.'+file_path.split(r'/')[-1].split('.')[-1])
                if os.path.exists(filename):  #如果文件存在就不需要再下载了
                    print('已存在无需下载%s' % filename)
                    continue
                else:
                    audio = requests.get(file_path,headers=audioheader)
                    with open(filename, 'wb') as f:
                        f.write(audio.content)
                    print(u'已保存', filename)
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue
            time.sleep(5)

if __name__ == '__main__':
    firstfolder = r'D:\work\workspace\qingtingFM'
    url = 'http://www.qingting.fm/channels/211520'
    qingting = QingTingFM(url,firstfolder)
    qingting.download_ma4()

