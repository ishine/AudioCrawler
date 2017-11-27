#-*- coding:utf-8 -*-
'''抓取喜马拉雅FM的音频，先进行分割，然后塞入语音识别API转换为文字
1、该模块实现抓取，抓下来之后慢慢处理'''
import requests
import os
import re
import random  #引入主要是为了随机休息一定时间
import time
from baselib import mkDir

#使用一个类将喜马拉雅所有符合的音频全部下载下来吧，只传入专辑url就好了
class XiMaLaYaCrawler(object):
    def __init__(self,albumurl):
        self.albumUrl = albumurl   #听书专辑url
        self.soundIDLst = []    #音频文件的ID，下载所需
        self.albumName = ''     #专辑名称，据此建立文件夹保存所有音频
        self.playPath = ''      #音频播放地址，即音频的存放地址，可直接下载
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}

    # 根据专辑url获得sound ID列表和专辑名称
    def get_sound_ids(self):
        '''返回soundID，许多组成的列表'''
        try:
            html = requests.get(self.albumUrl, headers=self.header)
            psoundid = re.compile(r'<div class="personal_body" sound_ids="(.*)">')  #获取soundID的匹配模式
            pname = re.compile(r'<div class="detailContent_title">.*?<h1>(.*)</h1>')  #获取专辑名称
            resurl = re.search(psoundid, html.text).group(1)
            resname = re.search(pname,html.text).group(1)
            resurl = resurl
            self.soundIDLst = resurl.split(',')
            self.albumName = resname
            print('成功获取soundID和album name %s' % self.albumName)
            time.sleep(random.choice(list(range(1,5)))/10)  #随机休息0点几秒
        except Exception as e:
            print('获取专辑URL和name出错了',e)

    # 根据soundID获得音频的播放地址
    def get_audio_path(self,soundId):
        import json
        rootUrl = 'http://www.ximalaya.com/tracks'   #每个专辑的音频URL都有这个，其后是soundID
        audioUrl = '{0}/{1}.json'.format(rootUrl, soundId)
        try:
            resp = requests.get(audioUrl, headers=self.header)

            respJsn = json.loads(resp.text)
            self.playPath = respJsn['play_path']
            print('playPath %s 已获得' % self.playPath)
            time.sleep(random.choice(list(range(2,6))))
        except requests.exceptions.ConnectTimeout as e:
            self.get_audio_path(soundId)

    # 根据播放地址下载音频文件
    def downloadM4a(self,firstfolder):
        '''
        :param firstfolder: 第一级目录，一个专辑一个文件夹，很多专辑有很多文件夹，全部放在firstfolder中，如ximalaya
        :return:
        '''
        self.get_sound_ids()
        path = mkDir(firstfolder, self.albumName)
        for soundid in self.soundIDLst:
            try:
                self.get_audio_path(soundid)
            except:
                continue
            try:
                filename = os.path.join(path, self.playPath.split(r'/')[-1])
                if os.path.exists(filename):  #如果文件存在就不需要再下载了
                    print('已存在无需下载%s' % filename)
                    continue
                else:
                    audio = requests.get(self.playPath,headers=self.header)
                    with open(filename, 'wb') as f:
                        f.write(audio.content)
                    print(u'已保存', filename)
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue

        time.sleep(random.choice(list(range(1, 5))))

if __name__ == '__main__':
    firstfolder = r'F:\audio\ximalayaAudio'
    albumUrlLst = []  # 先存在一个列表中吧

    # for p in range(5,9):
    album = 'http://www.ximalaya.com/13498076/album/276074'
    ximalayacrawler = XiMaLaYaCrawler(album)
    ximalayacrawler.downloadM4a(firstfolder)
    time.sleep(2)

    ## 下载中途出错，故单独下载这些soundID
    # #网络不行，卡在这里了，晕@#@!
    # sd = [7255528,7256741,7257761,7306528,7306529,7306530,7319836,7319837,7366363,7366364,7366365,7375224,7414212,
    #             7414283,7414450,7433723,7433724,7433725,7446700,7470079,7470124,7488995,7510623,7510648,7542784,7587595,
    #             7587596,7617301,7642398,7677074,7696022,7733155,7733194,7771065,7771066,7806988,7806989,7862917,7862963,
    #             7863021,7884214,7884377,7897110,7897131,7915730,7931064,7942142,7957833,7965628,7980736,7995108,8020325,
    #             8058411,8071693,8106177,8107215,8107731,8107794,8150408,8166173,8187965,8187966,8214712,8214713,8229254,
    #             8235905,8251541,8251542,8269399,8284068,8294602,8294603,8318581,8318642,8337223,8359754,8366450,8392850,
    #             8408737,8436527,8458200,8484567,8493498,8512782]
    # soundids = sd[78:]
    #
    # firstfolder = r'D:\work\workspace\ximalayaAudio'
    # header = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
    # def get_audio_path(soundId):
    #     import json
    #     rootUrl = 'http://www.ximalaya.com/tracks'   #每个专辑的音频URL都有这个，其后是soundID
    #     audioUrl = '{0}/{1}.json'.format(rootUrl, soundId)
    #     try:
    #         resp = requests.get(audioUrl, headers=header)
    #         respJsn = json.loads(resp.text)
    #         playPath = respJsn['play_path']
    #         print('playPath %s 已获得' % playPath)
    #         time.sleep(random.choice(list(range(0,3))))
    #         return playPath
    #     except requests.exceptions.ConnectTimeout as e:
    #         get_audio_path(soundId)
    # def downloadM4a(firstfolder):
    #     '''
    #     :param firstfolder: 第一级目录，一个专辑一个文件夹，很多专辑有很多文件夹，全部放在firstfolder中，如ximalaya
    #     :return:
    #     '''
    #     path = mkDir(firstfolder, '刘心武揭秘红楼梦')
    #     for soundid in soundids:
    #         playPath = get_audio_path(soundid)
    #         try:
    #             filename = os.path.join(path, playPath.split(r'/')[-1])
    #             if os.path.exists(filename):  #如果文件存在就不需要再下载了
    #                 print('已存在无需下载%s' % filename)
    #                 continue
    #             else:
    #                 audio = requests.get(playPath,headers=header)
    #                 with open(filename, 'wb') as f:
    #                     f.write(audio.content)
    #                 print(u'已保存', filename)
    #         except requests.exceptions.ConnectionError as e:
    #             print(e)
    #             continue
    #     time.sleep(random.choice(list(range(1, 5))))
    # downloadM4a(firstfolder)
