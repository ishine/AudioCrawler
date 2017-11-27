# '''
# Created on 2017/6/30 19:05
# 
# @author: Gaolijun
# '''
'''该库主要实现一些基础方法，方便调用，要不然我需要一个方法的时候到处找不到，集中在一起吧'''
import sys
import os
import re
import wave

#过滤标题非法字符匹配模式
p_title = re.compile(r'[ \s\n\t\r?？@#$%^&"\/\'\\“”‘’，:,。*！!.~|]+')
#在path目录中得到所有以fileType结尾的文件，返回列表
def getFile(path,fileType):
    '''

    :param path: 文件路径
    :param fileType: 后缀名（限Windows）
    :return: 该文件夹中所有filetype的文件，生成器
    '''
    for f in os.listdir(path):
        if f.endswith(fileType):
            yield os.path.join(path, f)
        else:
            continue

#新建文件夹
def mkDir(path,foldName):
    '''
    在path中建立foldName文件夹
    :param path: 目录
    :param foldName: 文件名
    :return: 新建文件名路径
    '''
    try:
        # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        # print(__file__)
        # print(sys._getframe().f_code.co_name)  #当前函数名
        # print(sys._getframe().f_lineno)    #当前行号
        if not os.path.exists(path):
            os.mkdir(path)
        rootpath = os.path.join(path, foldName)
        if not os.path.exists(rootpath):
            os.mkdir(rootpath)
        return rootpath
    except Exception as e:
        print('%s_%s\t make new file error %s' % (sys._getframe().f_code.co_name,sys._getframe().f_lineno,e))
        pass

#批量重命名文件，主要是去掉文件名的空格和特殊符号
def renamefile(sourcefile):
    try:
        p = re.compile(r'[！（一）? \s\n\t\r]+')
        filepath = '\\'.join(sourcefile.split('\\')[:-1])
        filename = re.sub(p,'',sourcefile.split('\\')[-1])  #将空格和特殊字符替换掉
        # filename = re.sub(r'mp3','.mp3',sourcefile.split('\\')[-1])
        os.rename(sourcefile,os.path.join(filepath, filename))
        print('rename %s is done' % filename)
    except Exception as e:
        print(e)

# 为了便于对比，这里获取wav文件的时长。
def getWavTime(wavfile):
    import matplotlib.pyplot as plt
    wavf = wave.open(wavfile, 'rb')
    params = wavf.getparams()
    # 获取声道数、位深、采样频率和帧数
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print('文件名：{0}，声道数：{1}，位深：{2}，采样频率：{3}，帧数：{4}'.format(wavfile,nchannels,sampwidth,framerate,nframes))
    hours = (nframes * 1.0 / framerate) / 3600  # 转换为小时
    return hours

#为了便于统计究竟搞了多少实际的音频时长，这里统计某一专辑所有已切割音频的时长、个数等
def get_segwav_info(albumPath):
    '''
    
    :param albumPath:
    :return:
    '''
    pathlst = list(os.walk(albumPath))  #获取专辑目录的所有路径
    all_total_hours = 0 #统计专辑所有音频时长
    for i in range(1,len(pathlst)):
        dirpath = pathlst[i][0]   #小段音频所在的文件夹路径
        wavfilelst = list(getFile(dirpath,'wav'))
        hours_total =0  #统计小音频总时长
        for wav in wavfilelst:
            hours = getWavTime(wav)
            hours_total +=hours
            # print('%s时长为\t%s小时' %(wav,hours))
        all_total_hours += hours_total
        print('%s  文件个数:%s，有效时长:%s小时' % (dirpath,len(wavfilelst),hours_total))
    print('%s  总时长为：%s小时'%(albumPath,all_total_hours))

if __name__ == '__main__':
    #获取分段音频大小的信息，可统计识别后的实际时长
    path =r'G:\已拷贝'
    get_segwav_info(path)

    # path = r'F:\audio\yueduFM'


    # path = r'D:\work\workspace\kaolaFM\大唐王朝惹了谁'
    # files = getFile(path,'mp3')
    # print(files)
    # flst = list(files)
    # print(flst,len(flst))

    # a = mkDir(r'C:\Users\THINK\Desktop','test')
    # print(a)