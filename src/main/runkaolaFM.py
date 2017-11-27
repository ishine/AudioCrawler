# '''
# Created on 2017/6/20 9:42
# 
# @author: Gaolijun
# '''
#通过命令行运行，下载音频
import sys
import time
from kaolaFM import KaoLaFM
import multiprocessing

firstfolder = r'D:\work\workspace\kaolaFM'
def run(url):
    kaola = KaoLaFM(url)
    th = multiprocessing.Process(target=kaola.downloadMp3,args = (firstfolder,))
    th.start()
    th.join()
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage:python runkaolaFM.py albumURL')
    else:
        url = sys.argv[1]
        run(url)
    print('done in %s' % time.ctime())