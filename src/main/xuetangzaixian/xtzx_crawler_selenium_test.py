# '''
# Created on 2017/7/13 15:09
# 
# @author: Gaolijun
# '''

#感觉不需要使用selenium了，直接使用requests就可以，设置cookie登录，进入课程详细页面，将各章节课程url抓下来，
# 进入课程页可得到mp4地址和字幕文件地址，如此更简单啊。
# 使用selenium有诸多问题，比如页面加载很慢导致视频文件还没有出来字幕就下载了，文件缺失，定位不准等，总是出现一个浏览器窗口
# 也是很不爽的啊，主要考虑到登录问题所以才使用，现在可以设置cookie为什么还要使用selenium呢，

import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 通过课程主页得到各播放地址，再获取video和字幕

url = 'http://www.xuetangx.com/courses/course-v1:TsinghuaX+00612642X+sp/courseware/820411228c5242c4a91be9c1a58e96ca/'
# browser = webdriver.PhantomJS()
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 15)

try:
    if not os.path.exists('video2audio'):
        rootpath = os.path.join(r'C:\Users\THINK\Downloads',u'video2audio')
        os.mkdir(rootpath)
except:
    pass
videoUrlLst = []
subtitlelst = []
videoPathlst = []

#登录。如果设置了cookie，就不需要每次都登陆了。
def loginOn():
    try:
        #进入主页
        browser.get(url)
        #需要登陆才行
        userNameIPT = wait.until(EC.presence_of_element_located((By.NAME,'username'))) #获取用户名输入框
        pwdIPT = wait.until(EC.presence_of_element_located((By.NAME,'password'))) #密码输入框
        submitBtn = wait.until(EC.element_to_be_clickable((By.ID,'loginSubmit'))) #提交按钮

        userNameIPT.send_keys('zhou.g.52@foxmail.com')
        pwdIPT.send_keys('xuexi123BC')
        submitBtn.click()  #提交
    except TimeoutException:
        return loginOn()
#获取videoURL，传入章节（从0开始）和小节序号（从1开始）（xpath），返回videoURL
isVideo = True
def getVideoURL(chapter,cls):
    #进入到课程主页
    #选择课程小结
    try:
        displayCourse = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="accordion"]/nav/div[%d]'%(chapter+1)))) #点击章节显出小节
        ac = ActionChains(browser)
        ac.click(displayCourse).perform()
        course = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ui-accordion-accordion-panel-{0}"]/li[{1}]'.format(chapter,cls))))
        ac.click(course).perform()
        __import__('time').sleep(3)
        browser.implicitly_wait(20)
        try:
            videoUrl = wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="xt_video_player_wrap"]/video'))).get_attribute('src')
            videoUrlLst.append(videoUrl)
            isVideo = True
            courseName = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="seq_content"]/div/div/div/div/h2'))).text
            os.chdir(rootpath)
            with open('vedioURL.txt', 'a') as f:
                f.write(videoUrl+' {0}\n'.format(courseName))
        except NoSuchElementException:
            isVideo = False
            print(u'视频不存在')
        # print(videoUrl+' {0}\n'.format(courseName))
    except TimeoutException:
        # getVideoURL(chapter,cls)
        pass
#获取字幕，该方法已弃用
def getSubtitle():
    #点击显示字幕并获取
    try:
        displayDiv = wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="xt_video_player_caption_btn xt_video_player_common fr"]/div[@class="xt_video_player_common_value"]')))
        ac = ActionChains(browser)
        ac.move_to_element(displayDiv).perform()
        displayTitle = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'li[data-type="aside"]')))
        ac.click(displayTitle).perform()  #链式操作
        subTitle = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[class="xt_video_player_caption_aside"]'))).text
        subtitlelst.append(subTitle)
        print(len(subTitle))
    except TimeoutException:
        getSubtitle()

#下载字幕文件
def downloadSubtitle():
    try:
        downBtn = wait.until(EC.presence_of_element_located((By.LINK_TEXT,u'下载字幕')))
        downBtn.click()
    except TimeoutException:
        # downloadSubtitle()
        pass
def downloadVideo(videoUrl):
    from contextlib import closing
    courseName = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="seq_content"]/div/div/div/div/h2'))).text
    videoName = courseName+'.mp4' #re.search(r'.*/(.*?\.mp4).*?',videoUrl).group(1)
#     cnt = requests.get(videoUrl).content
    videopath = os.path.join(rootpath,videoName)
    videoPathlst.append(videopath)
    print(courseName)
    # os.chdir(rootpath)
    # with open('videopath.txt', 'w+') as f:
    #     f.write(videopath.decode('utf-8'))

    #先将视频链接下载下来在慢慢下载视频吧
    # os.chdir(rootpath)
    # with closing(requests.get(videoUrl,stream=True)) as resp:  #分块读取
    #     chunkSize = 1024
    #     contentSize = int(resp.headers['content-length'])
    #     with open(videoName,'wb') as f:
    #         for data in resp.iter_content(chunk_size=chunkSize):
    #             f.write(data)

    # return videopath


def main():
    try:
        loginOn()
        for ch in range(0,17):
            __import__('time').sleep(1)
            for i in range(1,5):  #循环小节
                if isVideo:
                    getVideoURL(ch,i)  #测试第一章节
                    __import__('time').sleep(0.5)
                    downloadSubtitle()
                    # downloadVideo(videoUrl)
                    # video2audio(videopath)
                else:
                    continue
        print(videoUrlLst)
    except Exception as e:
        print(e)
        # print(videoUrlLst)
