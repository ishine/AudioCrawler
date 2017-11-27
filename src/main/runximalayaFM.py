# '''
# Created on 2017/6/20 9:28
# 
# @author: Gaolijun
# '''
#主要是用于在cmd中运行下载功能，只要输入专辑url和页数就行啦
import sys
from ximalayaFM import *
firstfolder = r'D:\work\workspace\ximalayaAudio'

def run(url,pagecnt):
    '''
    参数通过命令行获取
    :param url:专辑url
    :param pagecnt: 总的页数
    :return:
    '''
    for p in range(1,int(pagecnt)+1):
        album = '%s?page=%s' % (url,p)
        ximalayacrawler = XiMaLaYaCrawler(album)
        ximalayacrawler.downloadM4a(firstfolder)
        time.sleep(5)
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage:python runximalaya.py albumURL pageCount')
    else:
        url = sys.argv[1]
        pagecnt = sys.argv[2]
        run(url,pagecnt)
    print('done in %s' % time.ctime())