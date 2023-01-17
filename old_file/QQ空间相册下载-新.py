import math
from re import U
import threading
import time
from selenium.webdriver import ActionChains, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
import requests
import copy
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from tqdm import tqdm


class SimpleQueueFetch:
    """
    fetch = SimpleQueueFetch(['a','b','c','d','e'])
    fetch.show()
    fetch.get()
    fetch.show()
    fetch.put('h')
    fetch.show()
    """
    def __init__(self, arr):
        self.q = queue.Queue()
        for item in arr:
            self.q.put(item)

    def empty(self):
        return self.q.empty()

    def get(self):
        if self.q.empty():
            return None
        return self.q.get()

    def fetch(self, num=1):
        res = []
        for _ in range(num):
            if not self.empty():
                res.append(self.get())
        return res

    def put(self, msg):
        if msg:
            self.q.put(msg)

    def show(self):
        print(self.q.queue)

    def totalLength(self):
        return self.q.qsize()

    def pick(self):
        val = self.get()
        self.put(val)
        return val

class QQZone:
    def __init__(self, username=None, password=None, other_username=None):
        self.url_login = 'https://i.qq.com/'
        self.username = username
        self.password = password
        self.other_username = other_username
        self.qzonetoken = None
        self.cookies = None
        self.g_tk = None
        self.headers = {
            'host': 'user.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:66.0) Gecko/20100101 Firefox/66.0',
            'connection': 'keep-alive',
            'referer': 'https://qzone.qq.com/',
        }
        # Chrome下载链接：http://xfxuezhang.cn/web/share/软件-电脑/Chrome.zip
        self.browser_path = r'Chrome/BitBrowser.exe'
        self.driver_path = r'Chrome/chromedriver.exe'

    def driver(self):
        # 有头浏览器的写法
        driver = uc.Chrome(driver_executable_path=self.driver_path,
                            browser_executable_path=self.browser_path,
                            suppress_welcome=False)
        driver.get(self.url_login)
        
        if self.username and self.password:
          print('>> 提供了账号或密码，进入自动登录模式(不大建议)')
          print('>> 切换到登录表单')
          driver.switch_to.frame('login_frame')
          # 切换到账号密码登录
          log_method = driver.find_element(by=By.ID, value='switcher_plogin')
          log_method.click()
          # 输入账号密码，登录
          print('>> 输入账号中...')
          username = driver.find_element(by=By.ID, value='u')
          username.clear()
          username.send_keys(self.username)
          print('>> 输入密码中...')
          password = driver.find_element(by=By.ID, value='p')
          password.clear()
          password.send_keys(self.password)
          login_button = driver.find_element(by=By.ID, value='login_button')
          login_button.click()
          print('**此处若有滑块验证，请在10s内手动完成！！！**')
          time.sleep(10)
        else:
          print('>> 未提供账号或密码，进入手动登录模式')
        while True:
          try:
            WebDriverWait(driver, 2, 0.5).until(EC.presence_of_element_located((By.ID, r'aIcenter')))
            print('>> 登陆成功!')
            break
          except:
            print('>> 等待手动完成登录中...')
            time.sleep(10)
        driver.switch_to.default_content()

        # if self.other_username:
        #   print('>> 进入好友空间...')
        #   driver.get(r'https://user.qzone.qq.com/' + self.other_username)
        #   time.sleep(2)
        self.cookies = driver.get_cookies()
        return driver

    def back_session(self):
        # 创建一个session对象
        my_session = requests.session()
        headers = copy.deepcopy(self.headers)
        headers['host'] = 'h5.qzone.qq.com'
        # 将字典转为cookiejar, 这样就可以将cookie赋给session
        c = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
        my_session.headers = headers
        # 将cookie赋给session
        my_session.cookies.update(c)
        return my_session

    # 生成g_tk
    def get_g_tk(self, driver):
        hashes = 5381
        for letter in driver.get_cookie('p_skey')['value']:
            hashes += (hashes << 5) + ord(letter)
        self.g_tk = hashes & 0x7fffffff
        return self.g_tk


    def login(self):
        print('>> 开始登陆')
        driver = self.driver()
        print('>> 获取g_tk')
        self.get_g_tk(driver)
        print('>> 登录完成')
        driver.close()
        return self.cookies, self.g_tk, self.username



 
class QQZonePictures:
    def __init__(self, cookies=None, gtk=None, uin=None, host_uin=None, threads_num=4):
        self.cookies = cookies
        self.gtk = gtk
        self.uin = uin
        self.hostUin = host_uin
        self.threads_num = threads_num
        self.root = self.Mkdir_path(".//QQZone//")
        self.url_list = 'https://user.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/fcg_list_album_v3'
        self.url_photo = 'https://h5.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/cgi_list_photo?'
        self.header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'cookie': self.cookies,
            'pragma': 'no-cache',
            'referer': 'https://user.qzone.qq.com/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
        }

    def Clean_data(self, string):
        response = string.replace(' ', '')
        response = response.replace('\t', '')
        response = response.replace('\n', '')
        response = response.replace('false', '"false"')
        response = response.replace('true', '"true"')
        data = json.loads(response[10:-2])
        return data

    def Mkdir_path(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def Get_photo_lists(self):
        param = {
            'g_tk': self.gtk,
            'hostUin': self.hostUin if self.hostUin else self.uin,
            'uin': self.uin,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'pageNumModeSort': '40',
            'pageNumModeClass': '15'
        }
        res = requests.get(self.url_list, headers=self.header, params=param)
        Photo_lists_data = self.Clean_data(res.text)
        return Photo_lists_data

    def Get_photos(self, list_id, num, start=0):
        param = {
            'g_tk': self.gtk,
            'hostUin': self.hostUin if self.hostUin else self.uin,
            'uin': self.uin,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'topicId': list_id,
            'mode': 0,
            'appid': 4,
            'idcNum': 4,
            'noTopic': 0,
            'singleurl': 1,
            'skipCmtCount': 0,
            'pageStart': start,
            'pageNum': num,
            'source': 'qzone',
            'plat': 'qzone',
            'outstyle': 'json',
            'format': 'jsonp',
            'json_esc': 1,
            'question': '',
            'answer': '',
            'batchId': '',
        }
        # print(param)
        res = requests.get(self.url_photo, headers=self.header, params=param)
        # print(res.text)
        Photos_data = self.Clean_data(res.text)
        return Photos_data


    def Downloads_bk(self, data):
        file_name = data["data"]["topic"]['name']
        root = self.Mkdir_path(self.root + file_name + '//')
        print(f">> 相册{file_name}开始下载...")
        for photo in data["data"]["photoList"]:
            name = photo['name']
            pic_name = f"{name}.jpg"
            path = root + pic_name
            exist_index = 1
            while os.path.exists(path):
              pic_name = f"{name}_{exist_index}.jpg"
              path = root + pic_name
              exist_index += 1
            url = photo['raw'] if photo['raw'] else photo['url']
            print(f">> 当前URL: {url}")
            read = requests.get(url)
            with open(path, 'wb+') as file:
                file.write(read.content)
            print(f">> {pic_name} 下载成功")
        print(f">> 相册{file_name}下载完成...")
  
    def Downloads(self, data):
        file_name = data["data"]["topic"]['name']
        root = self.Mkdir_path(self.root + file_name + '//')
        contents = []
        temp_pic_names = []
        for photo in tqdm(data["data"]["photoList"], desc='照片链接处理中...'):
            name = photo['name'].split('/')[-1].split('.')[-1]
            url = photo['raw'] if photo['raw'] else photo['url']
            is_video = photo['is_video'] == "true"
            suffix = ".mp4" if is_video else ".jpg"
            pic_name = name + suffix

            exist_index = 1
            while temp_pic_names.count(pic_name):
              pic_name = f"{name}_{exist_index}" + suffix
              # print(f">> 文件名称已存在, 尝试新名称: {pic_name}")
              exist_index += 1
            temp_pic_names.append(pic_name)

            contents.append((pic_name, url))
        with open('url.txt', 'w+') as f:
          for pic_name, url in contents:
              f.write(pic_name + " " + url + '\n')
        print(">> 图片信息写入url.txt完成")
        
        print(">> 正式开始下载...")
        def thread_find(id):
          total_length = len(contents)
          gap = math.ceil(total_length / self.threads_num)
          start = gap * id
          end = gap * (id + 1)
          end = end if end <= total_length else total_length
          print('>> [{}]当前线程分配区域: [{}~{})'.format(id, start, end))
          datas = SimpleQueueFetch(contents[start:end].copy())
          while True:
            item = datas.get()
            if not item:
                print('>> [{}]没有更多内容，当前线程完成'.format(id))
                break
            pic_name, url = item
            path = root + pic_name
            print('>> [{}]当前下载：{} - {}'.format(id, path, url))
            read = requests.get(url)
            with open(path, 'wb+') as file:
                file.write(read.content)
            print(f">> [{id}] {pic_name} 下载成功")
            time.sleep(0.1)

        with ThreadPoolExecutor(self.threads_num) as executor:  # 创建 ThreadPoolExecutor
            future_list = [executor.submit(thread_find, id) for id in range(self.threads_num)]
        results = []
        for future in as_completed(future_list):
            results.append(future.result())  # 获取任务结果
        
        # pool = []
        # for id in range(self.threads_num):
        #   pool.append(threading.Thread(target=thread_find, args=(id, )))
        # for t in pool:
        #   t.start()
        #   t.join()

        print(f">> 相册{file_name}下载完成...")
        


    def main(self):
        photos_lists = self.Get_photo_lists()
        print(photos_lists)
        if photos_lists['code'] != 0:
          print('>> 相册获取失败')
          return
        index = 1
        print(">> 你共有以下相册，请输入需要下载相册的序号 \r\n  ")
        for photos_list in photos_lists["data"]["albumListModeSort"]:
            name = photos_list['name']
            num = photos_list['total']
            allowAccess = '加密' if photos_list['allowAccess'] == 0 else '开放'
            print("[{}] ({}){} - {}".format(index, allowAccess, name , num))
            index += 1
        which_album = int(input("输入数字(如:1) ").strip()) - 1
        list_id = photos_lists["data"]["albumListModeSort"][which_album]['id']
        num = photos_lists["data"]["albumListModeSort"][which_album]['total']
        print('>> 获取照片中...')
        start = 0
        Photos_datas = None
        current_num = 0
        while current_num <= num:
            Photos_data = self.Get_photos(list_id, 500, start=start)
            if not Photos_data["data"]["photoList"]:
                print('>> 无更多项')
                break
            current_num += 500
            start = current_num
            print('>> 本次获取到{}项，已获取到{}项，共{}项'.format(len(Photos_data["data"]["photoList"]), current_num, num))
            if not Photos_datas:
                Photos_datas = Photos_data
            elif Photos_data["data"]["photoList"]:
                Photos_datas["data"]["photoList"].extend(Photos_data["data"]["photoList"])
        print('>> 下载照片中...')
        self.Downloads(Photos_datas)
 

if __name__ == '__main__':
    username = input('>> 输入账号(必填): \r\n  ').strip() or '1061700625'
    password = input('>> 输入密码(可以为空, 直接回车): \r\n  ').strip()
    other_username = input('>> 输入对方账号(空表示下载自己): \r\n  ').strip()
    other_username = other_username if other_username else username
    threads_num = input('>> 输入下载线程数(默认4): \r\n  ').strip()
    threads_num = int(threads_num) if threads_num else 4

    print('*'*60, '\r\n\t\t    即将开始!')
    print('*'*60)
    time.sleep(2)

    print('>> 1.先模拟登陆获取cookie')
    Login = QQZone(username=username, password=password, other_username=other_username)
    cookies, gtk, uin = Login.login()
    final_ck = ''
    for ck in cookies:
        final_ck += '{}={};'.format(ck['name'], ck['value'])

    print('>> gtk: ', gtk)
    print('>> uin: ', uin)
    print('>> final_ck: ', final_ck)

    print('>> 2.再开始下载相册')
    Spider = QQZonePictures(cookies=final_ck, gtk=gtk, uin=uin, host_uin=other_username, threads_num=threads_num)
    Spider.main()













