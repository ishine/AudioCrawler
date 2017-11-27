#-*- coding:utf-8 -*-
# '''
# Created on 2017年6月5日
# 
# @author: Gaolijun
# '''

#本文件处理倒数三个步骤，（1）视频中提取音频，（2）将音频根据字幕进行切割，
# （3）读取文件与字幕的对应文件，获取相应文件和字幕,最后一步了
#故不涉及网络爬虫，主要是对爬下来的数据进行处理罢了。
import os
from pydub import AudioSegment
import wave
from functools import reduce

# 获取path下的所有MP4文件

#建立分割之后的音频文件，暂时不用
def mkSegDir(path,foldName):
    try:
        if not os.path.exists(os.path.join(path,foldName)):
            rootpath = os.path.join(path,foldName)
            os.mkdir(rootpath)
            return rootpath
        else:
            return os.path.join(path,foldName)
    except:
        pass

#测试，重命名文件
def renameFile():
    path = 'C:\\Users\\THINK\\Downloads\\video2audio\\资治通鉴'
    wavLst = getFile(path, 'wav')  # 获取所有wav文件
    videoFile = r'C:\Users\THINK\Downloads\video2audio\vedioURL1.txt'
    newWavName = []
    with open(videoFile, 'r', encoding='UTF-8') as f:
        lines = set(f.readlines())  # 使用集合去重
        for line in lines:
            videoUrl = line.split(' ', 1)[0]
            name = videoUrl.split(r'/')[-1].split('.')[0]
            courseName = line.split(' ', 1)[1].strip() + '.wav'
            newWavName.append((name, courseName))
    for i in wavLst:
        for j in newWavName:
            try:
                if i.split('\\')[-1].split('.')[0] == j[0]:
                    newName = j[1]
                    os.rename(i, os.path.join(path, newName))
            except:
                continue

#在path目录中得到所有以fileType结尾的文件，返回列表
def getFile(path,fileType):
    filelst = []
    for f in os.listdir(path):
        if f.endswith(fileType):
            filelst.append(os.path.join(path, f))

    return filelst


#倒数第三，从视频中提取音频
def gainAudio(videoPath):
    __import__('time').sleep(3)
    if os.path.exists(videoPath):
        # videoPath.split('\\')[-1].split('.')[0]
        os.system('ffmpeg -i '+videoPath+' -vn -ar 16000 -ac 1 -ab 192 -f wav '+videoPath.split('.')[0]+'.wav')
        print(videoPath.split('.')[0]+'.wav is ok')
    else:
        pass

#打开本地生成的时长为0.5秒的静音
halfSecSilence = AudioSegment.from_file(r'D:\work\workspace\halfSecSilence.wav',format='wav')

#将字幕文件的00:00:24,816时间格式转换为毫秒，便于音频的分割，返回对应的毫秒数
def time2millisec(timeStr):
    hour,sec,millsec = timeStr.split(':')
    millsec = int(hour)*3600*100+int(sec)*60*1000+int(millsec.replace(r',',''))
    return millsec

#倒数第二，将音频根据字幕进行切割
def segAudioBaseTitle(txtpath,oldwavPrefix,wavfile,srtfile):
    '''
    :param oldwavPrefix: wav文件的前缀，如A00，后面跟音频文件序号
    :param wavfile: 一个音频文件
    :param srtfile: 一个字幕文件
    :return: 无返回值
    '''
    wvfile = AudioSegment.from_file(wavfile, format='wav')  #打开音频文件
    if not os.path.exists(os.path.join(txtpath,srtfile.split('\\')[-1].split('.')[0]+'.txt')):
        with open(os.path.join(txtpath,srtfile.split('\\')[-1].split('.')[0]+'.txt'),'a',encoding='utf8') as f:  #即命名与字幕文件相同
            with open(srtfile,'r',encoding='utf-8') as subF:  #一句对应四行，序号、时间、字幕、空格
                for i,j in enumerate(subF):
                    #起始时间
                    if i % 8 == 2:  #先前的格式为4，这里居然要变化
                        seTime = j.split('-->')
                        linestartTime = seTime[0]  #一句的开始
                        lineendTime = seTime[1].strip()  #一句的结束，对应字幕文件的一行

                        startTime = time2millisec(linestartTime)
                        endTime = time2millisec(lineendTime)

                        wavlen = endTime+1 - startTime  #分段音频的长度，单位毫秒
                        # print(wavlen)

                        segWav = wvfile[startTime:endTime+1]
                        segWav.export('{oldwavPrefix}{name}.wav'.format(oldwavPrefix=oldwavPrefix,name =(i-1)//4 + 1),format='wav')
                        f.write('{oldwavPrefix}{name}\t'.format(oldwavPrefix=oldwavPrefix,name =(i-1)//4 + 1))
                        print('{oldwavPrefix}{name}.wav'.format(oldwavPrefix=oldwavPrefix,name =(i-1)//4 + 1),end='\t')
                    if i % 8 == 4:
                        title = j.strip()
                        f.write(title+'\n')
                        print(title)

# 合并音频，提供调用
def combineAudio(path,wavPathLst,oneWavName):
    '''传入一个根目录和音频文件路径的列表和合并之后的文件名。返回合并之后的文件路径'''
    if len(wavPathLst) == 1:  #若只有一个文件呢
        f = AudioSegment.from_file(wavPathLst[0],format='wav')
        fout = halfSecSilence + f + halfSecSilence
        fout.export(os.path.join(path, '{0}.wav'.format(oneWavName)), format='wav')
        return os.path.join(os.path.join(path, '{0}.wav'.format(oneWavName)))
    else:
        def _combine2wav(w1,w2):
            f1 = AudioSegment.from_file(w1,format='wav')
            f2 = AudioSegment.from_file(w2,format='wav')
            fout = halfSecSilence + f1 + f2
            fout.export(os.path.join(path,r'{0}.wav'.format(oneWavName)),format='wav')
            return os.path.join(os.path.join(path,'{0}.wav'.format(oneWavName)))
        reduce(_combine2wav,wavPathLst)

#以下处理短时间小音频文件问题
#倒数第一，读取文件与字幕的对应文件，获取相应文件和字幕,最后一步了
def genProduct(path,newwavPrefix,oldwavNameTitletxt,newwavNameTitletxt):
    '''path:音频文件和TXT文件所在的路径
    oldwavNameTitletxt:旧的音频名与字幕的对应，小音频不符合要求
    newwavPrefix:新音频文件前缀，如S00，后面是具体的序号名字
    newwavNameTitletxt:新的音频名与字幕的对应，时间符合要求
    注意：音频文件要与TXT文件放在
    '''
    # os.chdir(path)  # 切换到所有文件所在的目录

    wavTime = 0
    title = ''
    wavPath = ''
    cicleTimes = 0  # 循环次数，用于统计循环次数，主要是命名新文件
    productPath = mkSegDir(path,oldwavNameTitletxt.split('.')[0])
    print(productPath)
    if not os.path.exists(os.path.join(productPath,newwavNameTitletxt)):
        nameTitletxt = open(os.path.join(productPath,newwavNameTitletxt),'a',encoding='utf8')  #新建一个文件用于保存文件名和字幕,如'nameAndTitle.txt'
        # print(nameTitletxt)
        with open(os.path.join(path,'temp',oldwavNameTitletxt),'r',encoding='utf8') as ftxt:  #'第七课01_楚汉之争_下__汉王拜将.txt'
            lines  = ftxt.readlines()
            for i in range(len(lines)):
                wavName = lines[i].split('\t')[0].split('\\')[-1]   #获取wav文件名
                title += ' '+ lines[i].split('\t')[1].strip()   #获取对应字幕
                wavPath += ',' +os.path.join(path,'temp', wavName+'.wav')
                wavPathStr = wavPath.split(',')
                wav = wave.open(wavPathStr[-1],'rb')  #保证每次都是取最新一个文件进行处理
                params = wav.getparams()
                _,_,framerate,nframes = params[:4]
                wavTime += nframes / framerate   #音频时长，单位秒

                # print(wavTime)
                if wavTime < 5:
                    cicleTimes += 1
                    # print(cicleTimes)
                    continue
                else:
                    print('{newwavrPrefix}{name}\t{title}\n'.format(newwavrPrefix= newwavPrefix,name=i-cicleTimes,title=title.strip()))
                    # print(wavPathStr)
                    combineAudio(productPath,wavPathStr[1:],'{newwavrPrefix}{name}'.format(newwavrPrefix= newwavPrefix,name=i-cicleTimes)) #前缀从S00开始
                    nameTitletxt.write('{newwavrPrefix}{name}\t{title}\n'.format(newwavrPrefix= newwavPrefix,name=i-cicleTimes,title=title.strip()))
                    #全部变量归零
                    wavTime = 0
                    title = ''
                    wavPath = ''
        nameTitletxt.close()


#由于将所有音频和字幕放在了一个文件中，所以需要先将音频和字幕对应起来
def get_wavsrtLst(path):
    if not os.path.exists(path):
        raise("文件不存在")
    else:
        wavlst = getFile(path,'wav')
        srtlst = getFile(path,'srt')
        for srt in srtlst:
            for wav in wavlst:
                if srt.split('.')[0] == wav.split('.')[0]:
                    yield wav,srt
                else:
                    continue

if __name__ == '__main__':
    # mp4Lst = getFile('C:\\Users\\THINK\\Downloads\\video2audio\\资治通鉴','mp4')
    # for i in mp4Lst:
    #     gainAudio(i)

    # main()
    # time2millisec('00:02:16,275')
    #测试读取字幕文件
    # subtitleFile = u'C:\\Users\\THINK\\Downloads\\吴起的悲剧.srt'
    # with open(subtitleFile,'r') as subF:  #一句对应四行，序号、时间、字幕、空格
    #     for i,j in enumerate(subF):
    #         #起始时间
    #         if i % 4 == 1:
    #             seTime = j.split('-->')
    #             startTime = seTime[0]
    #             endTime = seTime[1].strip()
    #             print(startTime, endTime)
    #         if i % 4 == 2:
    #             title = j.strip()
    #             print(title)

    #使用分割函数，根据字幕将音频文件分割，现在有一个问题就是，音频文件与字幕文件的对应关系不太好确认。
    path = r'F:\audio\xuetangzaixian\数据结构(上)'
    # os.chdir(path)
    # # 得到path中的所有mp4文件，一一提取出音频
    # mp4Lst = getFile(path, 'mp4')
    # for i in mp4Lst:
    #     gainAudio(i)

    # #分割及合并音频
    wavsrt_gen = get_wavsrtLst(path)
    i = 0
    temp = mkSegDir(path,'temp')
    for wav, srt in wavsrt_gen:
        prefix = os.path.join(temp,wav.split('\\')[-1].split(r'.')[0] + '_A' + str(i))
        # try:
        #     segAudioBaseTitle(temp,prefix, wav, srt)  # 根据字幕切割音频
        # except Exception as e:
        #     raise e
        genProduct(path, 'S{}'.format(i), '{0}.txt'.format(wav.split('\\')[-1].split('.')[0]), wav.split('\\')[-1].split('.')[0]+'_nameAndTitle.txt')  #短音频合并
        i += 1

    # i =0
    # txtf = getFile(path+r'\temp','txt')
    # for txt in txtf:
    #     genProduct(path, 'S{}'.format(i), '{0}.txt'.format(txt.split('\\')[-1].split('.')[0]),
    #                txt.split('\\')[-1].split('.')[0] + '_nameAndTitle.txt')  # 短音频合并
    #     i+=1

    # wav = r'C:\users\think\desktop\chapter3第二节2.wav'
    # srt = r'C:\users\think\desktop\chapter3第二节2.srt'
    # prefix = os.path.join(r'C:\users\think\desktop', wav.split('\\')[-1].split(r'.')[0] + '_A' + str(i))
    # segAudioBaseTitle('A1', wav, srt)  # 根据字幕切割音频
    # wavLst = getFile(path, 'wav') #获取所有wav文件
    # srtLst = getFile(path,'srt')  #获取所有字幕文件
    # segAudioBaseTitle('A10',wavLst[0],srtLst[0])  #该文件夹只存在一个，如果是多个还需要一一判断对应一下。
    # genProduct(path,'S10','{0}.txt'.format(srtLst[0].split('.')[0]),'nameAndTitle.txt')

    #处理所有音频文件和字幕都在一个文件夹的情况


    #测试字幕文件
    # srtfile = r'F:\audio\xuetangzaixian\中国建筑史\第一节城市宫殿与佛教建筑1.srt'
    # with open(srtfile, 'r', encoding='utf-8') as subF:  # 一句对应四行，序号、时间、字幕、空格
    #     for i, j in enumerate(subF):
    #         # print(j)
    #         # 起始时间
    #         if i % 8== 2:  #2是字幕时间,4是文字
    #             seTime = j.strip().split('-->')
    #             print(j)
                # linestartTime = seTime[0]  # 一句的开始
                # lineendTime = seTime[1].strip()  # 一句的结束，对应字幕文件的一行
                # print(linestartTime,lineendTime)
                #
                # startTime = time2millisec(linestartTime)
                # endTime = time2millisec(lineendTime)