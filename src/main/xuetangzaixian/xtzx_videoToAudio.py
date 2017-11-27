#-*- coding:utf-8 -*-
'''
Created on 2017年6月5日
comments:面试之后需要先弄一个音频和对应字幕的小例子
@author: Gaolijun
'''
import re
import requests
import os
#os.chdir(r'C:\Users\Administrator\Desktop') #切换到桌面
#print(__import__('os').getcwd())

# videoURL = ['http://ws.cdn.xuetangx.com/071457014c79ae1c-20.mp4?utm_xuetangx=P5Dgn3rg06F3sS3E',
# 'http://bd.cdn.xuetangx.com/1d8fbcc6035b2b52-20.mp4?utm_xuetangx=P5Dgn3rg06F3sS3E',
# 'http://ws.cdn.xuetangx.com/c0dfbe0b322bf038-20.mp4?utm_xuetangx=P5Dgn3rg06F3sS3E',
# 'http://bd.cdn.xuetangx.com/4da77bcf3e7933f7-20.mp4?utm_xuetangx=P5Dgn3rg06F3sS3E',
# 'http://ws.cdn.xuetangx.com/d35636dd1f09c1fb-20.mp4?utm_xuetangx=P5Dgn3rg06F3sS3E']

#根据视频URL抓取视频
def crawlVideo(folderName,videoUrl):
    from contextlib import closing 
    videoName = re.search(r'.*/(.*?\.mp4).*?',videoUrl).group(1)
    # 新建一个文件夹
    try:
        if not os.path.exists(folderName):
            rootpath = os.path.join(r'C:\Users\THINK\Downloads\video2audio', folderName)
            os.mkdir(rootpath)
    except:
        pass
#     cnt = requests.get(videoUrl).content
    videopath = os.path.join(rootpath,videoName)
    # vdopathlst.append(videopath)
    os.chdir(rootpath)
#     with open(videoName, 'wb') as f:
#         f.write(cnt)
    with closing(requests.get(videoUrl,stream=True)) as resp:  #分块读取
        chunkSize = 1024
        # contentSize = int(resp.headers['content-length'])
        # print(contentSize)
        with open(videoName,'wb') as f:
            for data in resp.iter_content(chunk_size=chunkSize):
                f.write(data)
    # yield  videopath   #返回视频所在路径


def main():
    pass
    # for vu in videoURL:
    #     vp = crawlVideo(vu)
    #     gainAudio(vp)
    # print(vdopathlst)

if __name__ == '__main__':
    videoFile = r'C:\Users\THINK\Downloads\video2audio\vedioURL1.txt'
    with open(videoFile,'r') as f:
        lines = set(f.readlines())  #使用集合去重
        for line in lines:
            videoUrl = line.split(' ',1)[0]
            courseName = line.split(' ',1)[1].encode('utf-8')+'.mp4'
            crawlVideo(u'资治通鉴',videoUrl)  #下载视频
            print(line)

# wavPath1 = ['071457014c79ae1c-20.mp3',
#            '1d8fbcc6035b2b52-20.mp3',
#            'c0dfbe0b322bf038-20.mp3',
#            '4da77bcf3e7933f7-20.mp3',
#            'd35636dd1f09c1fb-20.mp3']
# wavPath = [os.path.join(rootpath,i) for i in wavPath1]
# combineAudio(wavPath)
#     f1 = AudioSegment.from_file(os.path.join(rootpath,u'all1.mp3'),format='mp3') #01=all1,23=all2,234=all3,01234=all
#     f2 = AudioSegment.from_file(os.path.join(rootpath,u'all3.mp3'),format='mp3')
#     fout = f1 + f2
#     fout.export(os.path.join(rootpath,u'all.mp3'),format='mp3')
# 转换为mp3，文件小了许多啊
#     wavPath1 = ['071457014c79ae1c-20.mp4',
#                '1d8fbcc6035b2b52-20.mp4',
#                'c0dfbe0b322bf038-20.mp4',
#                '4da77bcf3e7933f7-20.mp4',
#                'd35636dd1f09c1fb-20.mp4']
#     for videoPath in [os.path.join(rootpath,i) for i in wavPath1]:
#         os.system('ffmpeg -i '+videoPath+' -vn -ar 44100 -ac 2 -ab 192 -f mp3 '+videoPath.split('\\')[-1].split('.')[0]+'.mp3')
#
#
#     合并这一条语句搞定啊
#     os.system('ffmpeg -i '+wavPath[0]+' -i '+wavPath[1]+' -i '+wavPath[2]+' -i '+wavPath[3]+' -i '+wavPath[4]+' all.wav') #无用
    
    