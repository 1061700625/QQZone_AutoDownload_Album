# coding:utf-8
from bs4 import BeautifulSoup
import requests
import os
import re
import time
import threading
from selenium import webdriver
import urllib.request
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from io import BytesIO

global driver  # 在使用前初次声明
global oth_user

class Fetch:
    def __init__(self, arr):
        self.arr = arr
        self.index = 0

    def circleFetch(self, num):
        length = len(self.arr)
        if self.index <= length:
            if num <= (length - self.index):
                res = self.arr[self.index:self.index + num]
                self.index += num
                return res
            else:
                res = self.arr[self.index:]
                self.index = 0
                remain = num - len(res)
                return res + self.circleFetch(remain)

    def fetch(self, num):
        length = len(self.arr)
        if self.index >= length:
            print('>> 已取完！ <<')
            return None

        if num <= (length - self.index):
            res = self.arr[self.index:self.index + num]
            self.index += num
        else:
            res = self.arr[self.index:]
            self.index = length
        print('** 获取{}个，剩余{}个'.format(num, length-self.index))
        return res


    def add(self, msg):
        self.arr.append(msg)
        self.index += 1


def webpTojpg(path):
    f = Image.open(path)
    f.save(path.rsplit('.')[0]+'.jpg', 'JPEG')
    os.remove(path)
    print("* jpg转换完成 *")


def scroll2bottom():
    global driver  # 再次声明，表示在这里使用的是全局变量
    # 将滚动条移动到页面的底部
    driver.switch_to.default_content()
    js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(4)
    driver.switch_to.frame('tphoto')


import imghdr
def getPicurl():
    global driver  # 再次声明，表示在这里使用的是全局变量
    file_path = os.path.join(os.getcwd(), 'url.txt') 
    album_title = driver.find_element_by_css_selector(
        '.j-pl-quickedit-normal-content.j-pl-albuminfo-title').get_attribute('title')
    Soup = BeautifulSoup(driver.page_source, 'lxml')
    img = Soup.find_all('img', class_='j-pl-photoitem-img')
    imgNames = Soup.find_all('div', class_='item-tit')
    img_url = []
    for item in img:  # 链接的格式转换
        try:
            img_ori = item['src']
        except:
            img_ori = item['data-src']
            pass
        imgurl_rename = img_ori.replace(r'/m/', r'/b/').replace(r'psbe?', r'psb?').replace(r'/mnull', r'/b').replace(r'/m&', r'/b&').replace(r'rf=photolist', r'rf=viewer_4')  # 很重要
        img_url.append(imgurl_rename)
    with open(file_path, 'a+') as f:
        for i in range(len(img)):
            f.write(imgNames[i].getText().strip() + " " + img_url[i] + '\n')
        print("当前页图片链接添加完成")
    # print('img:  ', img, '\r\n', '*' * 60)
    return album_title, file_path


import threading
fetch_lock = threading.Lock()
imgCnt_lock = threading.Lock()
global img_current, total_img

def multiThreadDownload(num, contents):
    global img_current
    fetch = Fetch(contents)
    img_current = 0
    thread_pool = []
    id = 1
    for _ in range(num):
        t = threading.Thread(target=threadDownloadPics, args=(id, fetch))
        id += 1
        t.start()
        thread_pool.append(t)
    # 等待所有线程完成
    for t in thread_pool:
        t.join()
    print ("退出主线程")


def threadDownloadPics(id, fetch):
    while True:
        fetch_lock.acquire()
        items = fetch.fetch(10)
        fetch_lock.release()
        if items:
            doDownload(id, items)
        else:
            break

def doDownload(id, pics_arr):
    global img_current
    for item in pics_arr:
        item = item.strip()
        img_rel = item.split(' ')[-1]
        fileName =item.split(' ')[0]
        imgCnt_lock.acquire()
        img_current = img_current + 1
        imgCnt_lock.release()
        print(str(id) + ">> [{}/{}] 当前图片: {}.jpg".format(img_current, total_img, fileName))
        if os.path.exists(fileName+'.jpg'):
            print(str(id) + ">> 已存在")
            continue
        print(str(id) + ">> Img_URL: {}".format(img_rel))
        img_html = requests.get(img_rel, timeout=60)
        f = open(str(fileName) + '.jpg', 'wb')  # 写入多媒体文件必须要 b 这个参数！
        f.write(img_html.content)  # 多媒体文件是用conctent！
        f.close()
        if imghdr.what(str(fileName) + '.jpg') == 'webp':
            print(str(id) + ">> * webp格式图片 *")
            os.rename(str(fileName)+'.jpg', str(fileName)+'.webp')
            webpTojpg(str(fileName)+'.webp')
        time.sleep(0.1)

def picdownload(album_title, file_path):
    global total_img
    img_current = 0
    Content = []
    with open(file_path, "r") as f:
        for item in f:
            Content.append(item.strip())
        print("读取完成")
    total_img = len(Content)

    path = os.getcwd()  # 获取路径
    path_dir = os.path.join(path, album_title)  # 拼接路径
    print(path_dir)
    try:
        print('创建文件夹 --> {}'.format(album_title))
        os.mkdir(path_dir)  # 创建目录
    except:
        print('此文件夹已存在!')
        pass
    os.chdir(path_dir)  # 切换路径

    print('*' * 60, '\r\n开始下载图片')
    multiThreadDownload(10, Content)
    print('下载完成!')
    os.chdir(path)


def main_enter():
    global driver, oth_user  # 再次声明，表示在这里使用的是全局变量
    user = input('输入账号: \r\n  ').strip()
    word = input('输入密码: \r\n  ').strip()
    oth_user = input('输入对方账号(空表示下载自己): \r\n  ').strip()
    print('*'*60, '\r\n\t\t    即将开始!')
    print('*'*60)
    # while True:
    geturl = r'https://qzone.qq.com/'
    geturl_other = r'https://user.qzone.qq.com/' + oth_user
    profile = webdriver.FirefoxProfile(os.path.join(os.getcwd(), 'selenium_firefox'))
    driver = webdriver.Firefox(profile)   # 读入浏览器配置，以屏蔽浏览器通知
    # driver = webdriver.PhantomJS()
    driver.maximize_window()
    driver.implicitly_wait(30)  # 隐性等待
    driver.get(geturl)

    print('切换到登录表单')
    driver.switch_to.frame('login_frame')  # 登录表单在页面的框架中，所以要切换到该框架
    switcher_plogin = driver.find_element_by_id('switcher_plogin')
    switcher_plogin.click()
    time.sleep(1)

    username = driver.find_element_by_id('u')  # 查找账号
    password = driver.find_element_by_id('p')  # 查找密码
    login_button = driver.find_element_by_id('login_button')  # 查找登陆按键

    print('输入账号中...')
    username.clear()
    # time.sleep(1)
    username.send_keys(user)  # 输入账号
    print('输入密码中...')
    password.clear()
    # time.sleep(1)
    password.send_keys(word)  # 输入密码
    print('登陆中...')
    time.sleep(1)
    login_button.click()
    print('**此处若有滑块验证，请在10s内手动完成！！！**')
    time.sleep(10)
    while True:
        try:
            driver.find_element_by_id('switcher_plogin')
            print('登陆失败,将重试!')
            login_button.click()
            print('**此处若有滑块验证，请在10s内手动完成！！！**')
            time.sleep(10)
            # driver.delete_all_cookies()
            # driver.close()
            continue
        except:
            print('登陆成功!')
            break

    driver.switch_to.default_content()  # 返回

    if oth_user:
        time.sleep(5)
        print('进入', oth_user)
        driver.get(geturl_other)
        print('等待稳定...')
        time.sleep(5)
        if 'btn-fs-sure' in driver.page_source:
            friendship = driver.find_element_by_class_name('btn-fs-sure')
            friendship.click()
            time.sleep(1)
        print("稳定结束")
        # driver.refresh()


def main_album():
    global driver, img_current, total_img, oth_user  # 再次声明，表示在这里使用的是全局变量
    total_img = 0
    img_current = 0
    driver.refresh()
    time.sleep(2)
    driver.find_element_by_class_name('icon-homepage').click()
    # driver.find_element_by_class_name('logo').click()
    time.sleep(2)
    try:
        print("执行js调出'我的主页'界面")
        js = r'document.getElementById("tb_menu_panel").style.display="block"'
        driver.execute_script(js)
        # mainpage = driver.find_element_by_css_selector('.homepage-link.a-link')  # 进入主页
        # ActionChains(driver).move_to_element(mainpage).perform()
        time.sleep(2)
        menu_item = driver.find_elements_by_class_name('menu_item_4')[0]
        menu_item.click()
        # ActionChains(driver).move_by_offset(200, 200)
        # time.sleep(2)
        print("执行js退出'我的主页'界面")
        js = r'document.getElementById("tb_menu_panel").style.display="none"'
        driver.execute_script(js)
        time.sleep(2)
        # try:
        #     menu_item = driver.find_element_by_id('QM_Profile_Photo_A')
        # except:
        #     menu_item = driver.find_elements_by_class_name('menu_item_4')[1]
        # print('进入相册列表中...')
        # menu_item.click()  # 进入相册列表
        # time.sleep(6)

        print('检测广告中...')
        if '.op-icon.icon-close' in driver.page_source:
            guanggao = driver.find_element_by_css_selector('.op-icon.icon-close')
            print('检测到弹窗广告，自动关闭！')
            guanggao.click()
        else:
            print('无广告')
        driver.switch_to.frame('tphoto')
        print('switch to tphoto frame')
        print('**此页面如果有未处理广告，且干扰程序运行，请手动关闭！！！**')
        # 滚动
        driver.switch_to.default_content()
        js = "var q=document.documentElement.scrollTop=400"
        driver.execute_script(js)
        time.sleep(3)
        driver.switch_to.frame('tphoto')
        time.sleep(2)

        length = 0
        album_list = driver.find_elements_by_css_selector('.c-tx2.js-album-desc-a')
        album_list_cnt = 0
        print("你共有以下相册，请输入需要下载相册的序号 \r\n  ")
        for i in album_list:
            album_list_cnt = album_list_cnt + 1
            print("[", album_list_cnt, "] ", i.text)
        which_album = int(input("输入数字(如:1) ").strip()) - 1

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        total_img = int(soup.find_all(class_='pic-num')[which_album].string)
        #total_img = int(driver.find_elements_by_class_name('pic-num')[which_album])  # 'pic-num'  'j-pl-albuminfo-total'

        print("本相册共有[%s]张照片" % total_img)
        while True:
            album_list = driver.find_elements_by_css_selector('.c-tx2.js-album-desc-a')[which_album]
            print('进入相册中...', album_list.get_attribute('title'))
            album_list.click()
            time.sleep(5)

            #driver.find_element_by_class_name('pic-num-wrap')

            if oth_user:
                if '转载' not in driver.page_source:
                    print('进入相册失败,将重试!')
                    # album = driver.find_elements_by_css_selector('.item-wrap.bor-tx')[0]
                    # album.click()
                    # 滚动
                    driver.switch_to.default_content()
                    length = length + 100
                    js = "var q=document.documentElement.scrollTop=" + str(500 + length)
                    driver.execute_script(js)
                    time.sleep(3)
                    driver.switch_to.frame('tphoto')
                    time.sleep(2)
                    continue
                else:
                    print('进入成功!')
                    break
            else:
                if 'pic-num-wrap' in driver.page_source:
                    print('进入相册失败,将重试!')
                    # album = driver.find_elements_by_css_selector('.item-wrap.bor-tx')[0]
                    # album.click()
                    # 滚动
                    driver.switch_to.default_content()
                    length = length + 100
                    js = "var q=document.documentElement.scrollTop="+str(500+length)
                    driver.execute_script(js)
                    time.sleep(3)
                    driver.switch_to.frame('tphoto')
                    time.sleep(2)
                    continue
                else:
                    print('进入成功!')
                    break
    except Exception as e:
        print(e)

    print('扫描图片中...')
    counter = 3
    while counter > 0:
        scroll2bottom()
        counter = counter - 1
        while '加载失败，点击重试' in driver.page_source:
            print('点击重试')
            retry = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[2]/div[1]/div[3]/div[1]/div[1]/p/a')
            retry.click()
            time.sleep(1)
            scroll2bottom()
    print('扫描完成')

    if 'pager_last_1' in driver.page_source:
        page_num = driver.find_element_by_id('pager_last_1').get_attribute('innerHTML')
    elif 'js-pagenormal' in driver.page_source:
        page_num = driver.find_elements_by_css_selector('.js-pagenormal')[-1].get_attribute('title')
    else:
        page_num = 1

    page_current = 1
    print('**第{}/{}页**'.format(page_current, page_num))
    getPicurl()
    while page_current < int(page_num):
        next_page =driver.find_element_by_id('pager_next_1')
        next_page.click()
        page_current = page_current + 1
        print('**第{}/{}页**'.format(page_current,page_num))
        time.sleep(2)
        print('扫描图片中...')
        counter = 3
        while counter > 0:
            scroll2bottom()
            counter = counter - 1
            while '加载失败，点击重试' in driver.page_source:
                print('点击重试')
                retry = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[2]/div[1]/div[3]/div[1]/div[1]/p/a')
                retry.click()
                time.sleep(1)
                scroll2bottom()
        print('扫描完成')
        try:
            getPicurl()
        except Exception as e:
            print(e)




#******************************程序从此处开始******************************#


if __name__ == '__main__':
    # picdownload('无锡二漂', 'url.txt')
    # exit(0)
    global driver  # 再次声明，表示在这里使用的是全局变量
    print("此应用禁止任何形式商业活动，当你使用此应用时，默认同意此协议")
    print('程序运行要求：\r\n  '
          '1、下载火狐浏览器。\r\n  '
          '2、下载火狐驱动 geckodriver.exe\r\n  '
          '3、将驱动放至火狐安装目录。\r\n  '
          '4、将火狐安装目录添加至系统环境变量。\r\n  '
          '5、按提示输入信息，随后自动运行，若出错请多试几次。\r\n  '
          '6、程序有时运行缓慢，请耐心等待！\r\n  '
          '7、进入相册前，请不要在浏览器界面移动鼠标，以免干扰程序判断\r\n\r\n'
          'Github: https://github.com/1061700625/QQZone_AutoDownload_Album\r\n\r\n'
          )

    # ping = os.popen("ping baidu.com -n 1").readlines()
    # if "丢失 = 0" in ping[5]:
    #     print("网络可用")
    # else:
    #     print("网络不可用 - ", ping[5])
    #     input("任意键退出")
    #     os._exit(0)

    main_enter()
    album_title, file_path = main_album()
    picdownload(album_title)
    while(input("是否继续？(Y/N): ").strip().lower() == 'y'):
        print('\r\n\r\n')
        album_title, file_path = main_album()
        picdownload(album_title)
        
    print('感谢使用，下次见!')
    driver.close()


