# -*- coding:utf-8 -*-
import os
import wave
import matplotlib.pyplot as plt
from pydub import AudioSegment
import numpy as np
from segment import getFile  #导入获取文件列表的函数
import subprocess as sp

# wavefile = wave.open('out.wav','rb')
# params = wavefile.getparams()
# nchannels,sampwidth,framerate,nframes = params[:4]
# print(params[:4],'time=',nframes*1.0/framerate)

#文件格式转换函数，将framerate统一转换为16KHZ,channel是声道
#将多声道文件转换为单声道，并强制转为wav格式
def modifyTo16kSingle(sourceWavefile,fr,channel,outfile):
    #1、 这是一种调用系统命名的方法，使用os模块
    # try:
    #     command = 'ffmpeg -i '+sourceWavefile+' -ar '+str(fr)+' -ac '+str(channel)+' -f wav '+outfile
    #     print(command)
    #     __import__('os').system(command)
    # except Exception as e:
    #     print(e.message)

    #2、第二种调用系统命名的方法，使用subprocess
    command = 'ffmpeg -i ' + sourceWavefile + ' -ar ' + str(fr) + ' -ac ' + str(channel) + ' -f wav ' + outfile

    sp.Popen(command,shell=True,stdout=sp.PIPE,stderr=sp.PIPE)
    # print(p.stdout.read().decode('gbk'))   #打印输出，但如果只是处理没有输出也无影响。
    print('%s modify is done' % (outfile))

#文件首尾都需要0.5s的静音，故生成之，时间自定义
def genSilence(sec,outfile):
    import re
    p = re.compile(r'^[-+]?[0-9]+\.?[0-9]*$')  #使用正则检测输入是否合法，这里只能是整数或者浮点数
    res = p.match(str(sec))
    if res:
        secSilence = AudioSegment.silent(duration=1000 * sec)
        secSilence.export('temp.wav',format='wav')
        modifyFrameRateTo16K('temp.wav',16000,outfile)  #转换为16K采样率的音频
        __import__('os').remove('temp.wav')    #临时文件删掉
    else:
        print('参数错误，必须为数字')

#之前用phantomJS老是出错，所以专门测试一下
def testPhantomJS():
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.common.proxy import Proxy
    from selenium.webdriver.common.proxy import ProxyType
    #设置userAgent
    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 ' \
                                             '(KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
    #设置代理IP
    proxy = Proxy({
        'proxyType':ProxyType.MANUAL,
        'httpProxy':'218.108.107.70:909'
    })
    desired_cap = DesiredCapabilities.PHANTOMJS.copy()
    proxy.add_to_capabilities(desired_cap)
    #现在问题是要么是指useragent信息，要么设置代理IP，如何设置两者呢，探索中。
    # 可是学堂在线时而无法访问，看来抓取视频不太现实啊
    driver = webdriver.PhantomJS(desired_capabilities=desired_cap)
    driver.get('http://www.baidu.com')
    #
    data = driver.title
    from pprint import pprint
    print(data)
    pprint(driver.get_cookies())

#为了便于对比，这里获取wav文件的信息，如声道数，采样频率等。并画个图看看震幅
def getWavInfo(wavfile):
    import matplotlib.pyplot as plt
    wavf = wave.open(wavfile,'rb')
    params = wavf.getparams()
    #获取声道数、位深、采样频率和帧数
    nchannels,sampwidth,framerate,nframes = params[:4]
    # print('文件名：{0}，声道数：{1}，位深：{2}，采样频率：{3}，帧数：{4}'.format(wavfile,nchannels,sampwidth,framerate,nframes))
    hours = (nframes *1.0 / framerate) * 3600   #转换为小时
    return hours

    # #画图需要
    # time = np.arange(nframes) * 1.0 / framerate
    # datastr= wavf.readframes(nframes)
    # data = np.fromstring(datastr,np.short)
    # data.shape = -1,nchannels
    # data = data.T
    # data = data[0]
    # plt.plot(time,data)
    # plt.show()

if __name__ == '__main__':
    pass



    # testPhantomJS()
    # from HomeAudioDeal.baiduyuyintest import *  #调用自己写的这个包中方法
    # exampleWav = r'C:\Users\THINK\Desktop\A11_0.WAV'  #这个可以正常识别
    # testWav = r'D:\work\workspace\testSegAudio\test0.wav'  #这个识别有误
    # testWav1 = r'D:\work\workspace\A11_0.wav'  # 这个识别ok
    # getWavInfo(testWav1)
    # token = getToken()  # 获取token
    # print(useAPI(token, exampleWav))
    # print(useAPI(token, testWav))
    # print(useAPI(token, testWav1))

    # getWavInfo(exampleWav)
    # getWavInfo(testWav)
    # getWavInfo(testWav1)

    # modifyTo16kSingle(testWav,16000,1,'test00.wav')

