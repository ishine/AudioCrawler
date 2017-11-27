# '''
# Created on 2017/7/13 15:40
# 
# @author: Gaolijun
# '''

import os
import re
import requests
import random
from threading import Thread
from contextlib import closing
from myconfig import ualst
from baselib import p_title,mkDir

s = requests.Session()
cookieDct =  {'gr_user_id':'f318d025-4634-4c91-a4c3-b36990d8ff02',
              'UM_distinctid':'15d3a92205cbd0-013de5e8d284ec-474a0521-1fa400-15d3a92205da73',
              'sharesessionid':'cfb14f69094d13883d1054bed8c98833',
              'frontendUserTrack':'88636',
              'gr_session_id_a6b8a3dfa84a2afd':'5c6e659e-33f0-4c4b-82e8-c5fbbacded09',
              'frontendUserTrackPrev':'88636',
              '_log_user_id':'50e388e4191c892860a147598e9276f6'}
headers = random.choice(ualst)

def get_courseUrlName(url):
    cookieDct['frontendUserReferrer'] = url
    s.cookies = requests.utils.cookiejar_from_dict(cookieDct, cookiejar=None, overwrite=True)
    r = s.get(url,headers=headers)
    html = r.text
    chapter_p = re.compile(r'<div class="chapter.*?>(.*?)</div>',re.S)
    chapters = re.findall(chapter_p,html)  #找到所有章节
    # print(chapters)
    courseUrl_p = re.compile(r'<li .*?<a href="(.*?)">.*?<p>(.*?)</p>.*?<p class="subtitle"> </p>.*?</li>',re.S)
    for cha in chapters:
        courseUrl = re.findall(courseUrl_p,cha)  #某章节下的所有课程，格式为[(courseUrl,标题),(courseUrl,标题),...]
        yield courseUrl

#根据传入的课程url找到mp4地址和字幕地址，并下载
def getcourseMp4_subtitle(courseUrl,filename):
    whole_courseUrl = 'http://www.xuetangx.com%s'%courseUrl #完整的课程url
    cookieDct['frontendUserReferrer'] = whole_courseUrl
    s = requests.Session()
    s.cookies = requests.utils.cookiejar_from_dict(cookieDct, cookiejar=None, overwrite=True)
    r = s.get(whole_courseUrl,headers=headers)
    html = r.text
    # print(html)
    def _downloadMp4(videoUrl,mp4filename):
        if os.path.exists(mp4filename):
            print('已存在无需下载:%s'%mp4filename)
        else:
            with closing(requests.get(videoUrl, stream=True)) as resp:  # 分块读取
                chunkSize = 1024
                # contentSize = int(resp.headers['content-length'])
                # print(contentSize)
                with open(mp4filename, 'wb') as f:
                    for data in resp.iter_content(chunk_size=chunkSize):
                        f.write(data)
                    print('%s已下载'%mp4filename)

    #获取视频URL
    videoUrl_p = re.compile(r'data-ccsource=&#39;(.*?)&#39;')
    # videoReq = 'http://www.xuetangx.com/videoid2source/%s'%re.search(videoUrl_p,html).group(1)  #视频url所在的请求地址
    # videoUrl = requests.get(videoReq,headers=headers).json()['sources']['quality10'][0]
    videoUrls = re.findall(videoUrl_p,html)  #同一小节有多个视频，并且要与字幕相对应啊

    #获取字幕文件URL
    # srtUrl_p = re.compile(r'&lt;a href=&#34;(.*?)&#34; .*?(下载中?文?字幕|字幕下载)')  #字幕所在位置有多个条件啊，换了一门课程，字幕匹配不到了，看来只有匹配下载链接了
    srtUrl_p =  re.compile(r'&lt;li class=.*?video-download-button.*?a href=&#34;(.*?)&#34;&gt;下载字幕',re.S)  #re.compile(r'&lt;a href=&#34;(.*?)&#34;&gt;(下载字幕|字幕下载)')
    srturls = re.findall(srtUrl_p,html)
    # print(videoUrls)
    # print(srturls)
    i = 1
    for vurl,surl in zip(videoUrls,srturls):
        # print(vurl,surl[0])
        videoReq = 'http://www.xuetangx.com/videoid2source/%s' % vurl
        videoUrl = requests.get(videoReq,headers=headers).json()['sources']['quality10'][0]
        srtUrl = 'http://www.xuetangx.com%s'%surl
        # _downloadMp4(videoUrl,filename+'{0}.mp4'.format(i))
        th = Thread(target=_downloadMp4,args=(videoUrl,filename+'{0}.mp4'.format(i)))
        th.start()
        # th.join()
        #保存字幕
        rsrt = s.get(srtUrl,headers=headers)
        srtfilename = filename+'{0}.srt'.format(i)
        if not os.path.exists(srtfilename):
            with open(srtfilename,'w',encoding='utf-8') as f:
                f.write(rsrt.text)
                print('%s已保存' % srtfilename)
        else:
            print('已存在无需下载:%s' % srtfilename)
        i+=1
    ## yield videoUrl,srtUrl

def main(url,courseName):
    import time
    firstfolder = mkDir(r'F:\audio\xuetangzaixian',courseName)  #以课程名建立文件夹
    # print(get_courseUrlName(url))
    i = 1
    for courseUrlNames in get_courseUrlName(url):  #每一章
        # print(courseUrlNames)
        chapter =  'chapter%s'%i
        print(chapter)
        for curlName in courseUrlNames:  #该章的每一节，每一节会有多个视频
            courseurl = curlName[0]
            title = chapter+re.sub(p_title,'',curlName[1])  #主要是命名冲突，比如第一章和第二章课程名相同时会自动跳过，坑啊
            print(title,'\t',courseurl)
            filename = os.path.join(firstfolder,title)
            getcourseMp4_subtitle(courseurl,filename)
        # time.sleep(1)
        i += 1
    print('done on %s\n' % time.ctime())


if __name__ == '__main__':
    #单元测试
    # test_courseUrl = r'/courses/course-v1:TsinghuaX+80000901_tv+2015_T1/courseware/2640b90a1bfc484c85e0628fa6cd309c/91dd676764454041ae5d11ace9cf21d3/'
    # # print(list(getcourseMp4_subtitle(test_courseUrl)))
    # getcourseMp4_subtitle(test_courseUrl,'1')

    # 测试视频与字幕，每个视频和字幕必须要一一对应，要不然名字相同但是不对应那就悲剧了。
    # vurl = r'/courses/course-v1:TsinghuaX+80000901X_2+2017_T1/courseware/1532699977ef42d98e5d0f798703c361/c0658d0554624911b503de6c4e7df806/'
    # filename = r'F:\audio\xuetangzaixian\中国建筑史（下）（2017春）\chapter1第一节'
    # getcourseMp4_subtitle(vurl,filename)

    # #正式开始，测试
    url = r'http://www.xuetangx.com/courses/course-v1:TsinghuaX+30240184_2X+sp/courseware/06d6c305fca54193901007d83cd6e74e/'
    coursename = r'数据结构(下)'
    main(url,coursename)
