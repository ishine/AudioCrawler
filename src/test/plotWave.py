# -*- coding:utf-8 -*-
'''
Created on 2017年6月10日

@author: Gaolijun
根据网上资料学习对wave文件进行绘制波形图，为了判断句子分割
'''
import os
import wave
import numpy as np
import matplotlib.pyplot as plt
import pydub

def waveread(path):
    wavefile = wave.open(path,'rb')
    params = wavefile.getparams()
    nchannels,framerate,nframes = params[0],params[2],params[3]  #得到采样率和总的帧数
    print(params)
    datawav = wavefile.readframes(nframes)   #读取每一帧
    
    wavefile.close()
    datause = np.fromstring(datawav,dtype=np.short)
    datause = datause * 1.0 /(max(abs(datause)))   #归一化，转换为-1至1之间的数，导致内存不够
    datause.shape = -1,nchannels
    datause = datause.T   #转置
#     print(datause.shape,datause.ndim,type(datause))
    time = np.arange(0,nframes) * (1.0/framerate)        #秒数
    return datause,time

def main():
#     path = r'E:\workspace\practice\audioAndsubtitle\video2audio2subtitle\1d8fbcc6035b2b52-20.wav'
    path = os.path.join(os.getcwd(),r'../test.wav')
    wavedata,wavetime = waveread(path)
    data = wavedata[0]
    print(np.mean(data),np.min(data),data[(data>=-100)&(data<=100)].size)
    print('start plot')
    plt.title('wave pic')
    plt.subplot(111)
    plt.plot(wavetime[::100],data[::100],color='g')
    plt.show()

if __name__ == '__main__':
#     path = r'E:\workspace\practice\audioAndsubtitle\video2audio2subtitle\1d8fbcc6035b2b52-20.wav'
#     wavedata,wavetime = waveread(path)
#     data = wavedata[0]
    main()
    