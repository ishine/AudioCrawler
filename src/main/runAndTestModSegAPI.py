# '''
# Created on 2017/6/20 10:52
# 
# @author: Gaolijun
# '''
import sys
from segment import *
import multiprocessing
from queue import Queue
from threading import Thread
from baselib import  getFile
from news.qq_news import QQNews,gen_date


#由于每个音频文件都不一样，所以需要测试一下如何选择分割的阈值。
#同时这里建立独立的函数用于转换，分割，转换及分割，百度API也放在这里吧，不想新建一个文件了
files_q = Queue(50)
exit_flg = object()
#在path目录中得到所有以fileType结尾的文件，转为modify打造
def getFilem(path,*fileType):
    for f in os.listdir(path):
        if f.endswith(fileType):
            files_q.put(os.path.join(path, f))
            time.sleep(5)
        else:
            continue
    files_q.put(exit_flg)

#转换音频
def modify():
    # def _get_wave_file_sec(wavfile):   #获取wav文件的秒数，主要适用于判断转换有无成功，因为会出现没有转换完成的文件时间都是37:16:57即 134217秒
    #     _wavfile = wave.open(wavfile,'rb')
    #     params = _wavfile.getparams()
    #     sec = params[3] // params[2]
    #     return sec
    while True:
        # file_q = Queue()  #用于保存转换后的wav文件，用于_get_wave_file_sec验证
        file = files_q.get()
        if file is not exit_flg:
            modif = ModifyWav(file)
            modif.modifyTo16kSingle()
        else:
            break

def run_modify(sourcefilepath,filetype):
        th1 = Thread(target=getFilem,args=(sourcefilepath,filetype))
        th2 = Thread(target=modify)
        th1.start()
        th2.start()
        th1.join()
        th2.join()

#可以输入参数，便于调整
def run_segment(wavfile,outwavprofix,conThres=0.5,gt=-0.08,lt=0.08):
    seg = Segment(wavfile)   #新建一个Segment对象，传入的是标准wav文件
    seg.segmentAudio(outwavprofix,conThres,gt,lt)

#调用API识别语音
def run_baiduAPI(sourcefilepath):
    try:
        p = multiprocessing.Process(target=wav2title,args=(sourcefilepath,))
        p.start()
        p.join()
    except Exception as e:
        print(e)
        time.sleep(5*60)

#调用腾讯新闻
def run_qqnews(y,m,d):
    qqnews = QQNews()
    firstfolder = r'F:\news'
    for i in gen_date(y,m,d):
        qqnews.main_download(firstfolder,i)
        print('%s is ok\n' % i)

if __name__ == '__main__':
    # 根据命令行运行参数判断，0就是modify，1就是segment，2就是BaiduAPI
    # modify需要三个参数，segment需要六个参数，BaiduAPI需要2个，加上一个判断参数，所以至少是四个
    if len(sys.argv) == 3 and sys.argv[1]== '2':  #api
        sourcefilepath = sys.argv[2]
        run_baiduAPI(sourcefilepath)

    elif sys.argv[1] == '0':  #modify
        sourcefilepath = sys.argv[2]
        filetype = sys.argv[3]
        run_modify(sourcefilepath,filetype)
    elif sys.argv[1] == '1':  #单个segment
        wavfile = sys.argv[2]
        outwavprofix = sys.argv[3]
        conThres = float(sys.argv[4])
        gt = float(sys.argv[5])
        lt = float(sys.argv[6])
        run_segment(wavfile,outwavprofix,conThres,gt,lt)
    elif sys.argv[1] == '3':    # 根据路径名批量分割
        # i = 0  #i主要是为每个音频文件分段的命名
        filelst = getFile(sys.argv[2], 'wav')
        outwavprofix = sys.argv[3]
        conThres = float(sys.argv[4])
        gt = float(sys.argv[5])
        lt = float(sys.argv[6])
        filelst = list(filelst)
        flstlen =  len(filelst)
        for i in range(flstlen):
            print('i=%d -> %d ' % (i+1,flstlen), end=' ')  #%.2f %%,(i+1) * 100 / flstlen
            run_segment(filelst[i], '%s%s' % (outwavprofix,i),conThres,gt,lt)
    elif sys.argv[1]== '4':
        y = sys.argv[2]
        m = sys.argv[3]
        d = sys.argv[4]
        run_qqnews(int(y),int(m),int(d))
    else:
        print('usage:\n sys.argv[1]==0:python {0} 0 sourcefilepath filetype\n '
              'sys.argv[1]==1:python {0} 1 wavefile outwavprofix conthres gt lt'.format('module.py'))

    print('done on %s' % time.ctime())
