# -*- coding: utf-8 -*-
"""
QQ空间相册下载器
支持 Windows/Linux/macOS 多平台运行
自动检测 Chrome 浏览器路径和版本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gui import Win, Simpledialog, SimpleMessagebox
import time
import os
import platform
from queue import Queue
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
import json, json5
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import pyautogui
from bs4 import BeautifulSoup
import lxml
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import piexif
from datetime import datetime


def is_wsl():
    """检测当前是否运行在 WSL (Windows Subsystem for Linux) 环境中"""
    return 'microsoft' in platform.uname().release.lower() or 'WSL' in platform.uname().release


def get_chrome_version(browser_path):
    """
    获取 Chrome/Chromium 浏览器版本号
    
    Args:
        browser_path: 浏览器可执行文件路径
        
    Returns:
        str: 版本号字符串 (如 "146.0.7680.80") 或 None
    """
    if not browser_path or not os.path.exists(browser_path):
        return None
    try:
        result = os.popen(f'"{browser_path}" --version 2>/dev/null').read().strip()
        import re
        match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', result)
        if match:
            return match.group(0)
        match = re.search(r'(\d+)', result)
        if match:
            return match.group(1)
    except:
        pass
    return None


def get_chrome_paths():
    """
    根据操作系统自动检测 Chrome/Chromium 浏览器路径
    
    Returns:
        tuple: (browser_path, driver_path) 浏览器路径和驱动路径
    """
    system = platform.system()
    browser_path = None
    driver_path = None
    
    if system == 'Windows':
        windows_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
            r'Chrome/BitBrowser.exe',
            r'Chrome/chrome.exe',
        ]
        for path in windows_paths:
            if os.path.exists(path):
                browser_path = path
                break
        driver_path = r'Chrome/chromedriver.exe'
        if not os.path.exists(driver_path):
            driver_path = None
            
    elif system == 'Linux':
        if is_wsl():
            wsl_chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
            ]
        else:
            wsl_chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
            ]
        for path in wsl_chrome_paths:
            if os.path.exists(path):
                browser_path = path
                break
        driver_path = None
        
    elif system == 'Darwin':
        mac_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
        ]
        for path in mac_paths:
            if os.path.exists(path):
                browser_path = path
                break
        driver_path = None
    
    return browser_path, driver_path


def write_exif_to_image(image_path, photo_data):
    """
    将 QQ 空间照片的 EXIF 信息写入图片文件
    
    Args:
        image_path: 图片文件路径
        photo_data: QQ 空间返回的照片数据字典
    """
    try:
        if photo_data.get('is_video', False):
            return

        exif_data = photo_data.get('exif', {})
        if not exif_data:
            return

        zeroth_ifd = {}
        exif_ifd = {}

        make = exif_data.get('make', '')
        if make:
            zeroth_ifd[piexif.ImageIFD.Make] = make

        model = exif_data.get('model', '')
        if model:
            zeroth_ifd[piexif.ImageIFD.Model] = model

        original_time = exif_data.get('originalTime', '')
        if original_time:
            exif_ifd[piexif.ExifIFD.DateTimeOriginal] = original_time
            exif_ifd[piexif.ExifIFD.DateTimeDigitized] = original_time

        exposure_time = exif_data.get('exposureTime', '')
        if exposure_time:
            try:
                if '/' in exposure_time:
                    num, den = exposure_time.split('/')
                    exif_ifd[piexif.ExifIFD.ExposureTime] = (int(num), int(den))
            except:
                pass

        iso = exif_data.get('iso', '')
        if iso:
            try:
                exif_ifd[piexif.ExifIFD.ISOSpeedRatings] = int(iso)
            except:
                pass

        focal_length = exif_data.get('focalLength', '')
        if focal_length:
            try:
                if '/' in focal_length:
                    num, den = focal_length.split('/')
                    exif_ifd[piexif.ExifIFD.FocalLength] = (int(num), int(den))
            except:
                pass

        flash = exif_data.get('flash', '')
        if flash:
            try:
                exif_ifd[piexif.ExifIFD.Flash] = int(flash)
            except:
                pass

        if zeroth_ifd or exif_ifd:
            exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd}
            try:
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, image_path)
            except Exception as e:
                queue_print(f">> EXIF 写入失败: {e}")

    except Exception as e:
        queue_print(f">> 处理 EXIF 出错: {e}")


global_queue = Queue()


def queue_print(string):
    global global_queue
    global_queue.put(string)
    print(string)


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
        self.browser_path, self.driver_path = get_chrome_paths()
        if self.browser_path:
            queue_print(f'>> 检测到浏览器路径: {self.browser_path}')
        else:
            queue_print('>> 警告: 未检测到 Chrome 浏览器，将尝试自动下载')

    def get_browser_options(self):
        options = Options()
        # self.options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-full-form-autofill-ios")
        options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features")
        options.add_argument("--incognito")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-javascript")
        options.add_argument("--lang=en_US")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--no-first-run")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--autoplay-policy=user-gesture-required")
        options.add_argument("--disable-features=ScriptStreaming")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.page_load_strategy = 'eager'
        return options

    def driver(self):
        """
        初始化并返回 Chrome WebDriver 实例
        自动检测浏览器版本并下载匹配的 ChromeDriver
        """
        chrome_options = self.get_browser_options()
        if self.browser_path and os.path.exists(self.browser_path):
            chrome_options.binary_location = self.browser_path
        
        if self.driver_path and os.path.exists(self.driver_path) and self.browser_path and os.path.exists(self.browser_path):
            driver = uc.Chrome(driver_executable_path=self.driver_path,
                            suppress_welcome=False,
                            options=chrome_options)
        else:
            queue_print('>> 正在初始化浏览器...')
            chrome_version = get_chrome_version(self.browser_path)
            if chrome_version:
                queue_print(f'>> 检测到 Chrome 版本: {chrome_version}')
            try:
                version_main = int(chrome_version.split('.')[0]) if chrome_version else None
                driver = uc.Chrome(options=chrome_options, version_main=version_main)
            except Exception as e:
                queue_print(f'>> undetected_chromedriver 失败: {e}')
                queue_print('>> 尝试使用标准 selenium...')
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                if chrome_version:
                    service = Service(ChromeDriverManager(driver_version=chrome_version).install())
                else:
                    service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(self.url_login)

        if self.username and self.password:
            queue_print('>> 提供了账号或密码，进入自动登录模式(不大建议)')
            queue_print('>> 切换到登录表单')
            driver.switch_to.frame('login_frame')
            # 切换到账号密码登录
            log_method = driver.find_element(by=By.ID, value='switcher_plogin')
            log_method.click()
            # 输入账号密码，登录
            queue_print('>> 输入账号中...')
            username = driver.find_element(by=By.ID, value='u')
            username.clear()
            username.send_keys(self.username)
            queue_print('>> 输入密码中...')
            password = driver.find_element(by=By.ID, value='p')
            password.clear()
            password.send_keys(self.password)
            login_button = driver.find_element(by=By.ID, value='login_button')
            login_button.click()
            queue_print('**此处若有滑块验证，请在10s内手动完成！！！**')
            queue_print('**若未成功登录，请手动完成登录！！！**')
            time.sleep(10)
        else:
            queue_print('>> 未提供账号或密码，进入手动登录模式')
        while True:
            try:
                # WebDriverWait(driver, 2, 0.5).until(
                # EC.presence_of_element_located((By.ID, r'aIcenter')))
                _ = BeautifulSoup(driver.page_source, 'lxml').find_all('a', id='aIcenter')[0]
                print('>> 登陆成功!')
                break
            except Exception as e:
                # SimpleMessagebox.create(
                    # title='自动登陆失败', message='请手动完成登录!', msg_type='warning')
                pyautogui.alert(title='自动登陆失败', text='请手动完成登录后，等待几秒，点击确认!\n若重复出现，请刷新页面。', button='确认')
                queue_print('>> 等待手动完成登录中, 可能较久，稍等一会儿...'+str(e))
                time.sleep(5)
        driver.switch_to.default_content()

        if self.other_username:
          print('>> 进入好友空间...')
          driver.get(r'https://user.qzone.qq.com/' + self.other_username)
          time.sleep(2)
        self.cookies = driver.get_cookies()
        return driver

    def back_session(self):
        # 创建一个session对象
        my_session = requests.session()
        headers = copy.deepcopy(self.headers)
        headers['host'] = 'h5.qzone.qq.com'
        # 将字典转为cookiejar, 这样就可以将cookie赋给session
        c = requests.utils.cookiejar_from_dict(
            self.cookies, cookiejar=None, overwrite=True)
        my_session.headers = headers
        # 将cookie赋给session
        my_session.cookies.update(c)
        return my_session

    def get_g_tk(self, driver):
        hashes = 5381
        for letter in driver.get_cookie('p_skey')['value']:
            hashes += (hashes << 5) + ord(letter)
        self.g_tk = hashes & 0x7fffffff
        return self.g_tk

    def login(self):
        queue_print('>> 开始登陆')
        driver = self.driver()
        queue_print('>> 获取g_tk')
        self.get_g_tk(driver)
        queue_print('>> 登录完成')
        try:
            driver.close()
            driver.quit()
        except:
            pass
        return self.cookies, self.g_tk, self.username


class QQZonePictures:
    def __init__(self, cookies=None, gtk=None, uin=None, host_uin=None, save_path="./QQZone/", threads_num=4):
        self.cookies = cookies
        self.gtk = gtk
        self.uin = uin
        self.hostUin = host_uin
        self.threads_num = threads_num
        self.root = self.Mkdir_path(save_path)
        self.url_list = 'https://user.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/fcg_list_album_v3'
        self.url_photo = 'https://h5.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/cgi_list_photo?'
        self.header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
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
        response = string.strip()
        json_str = response[10:-2] if len(response) > 12 else response
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            queue_print(f'>> JSON 解析错误: {e}')
            queue_print('>> 尝试使用 json5 解析...')
            try:
                data = json5.loads(json_str)
            except Exception as e2:
                queue_print(f'>> json5 解析失败: {e2}')
                queue_print(f'>> 数据位置 {e.pos if hasattr(e, "pos") else "未知"}')
                if hasattr(e, 'pos') and e.pos:
                    start = max(0, e.pos - 50)
                    end = min(len(json_str), e.pos + 50)
                    queue_print(f'>> 错误位置附近数据: ...{json_str[start:end]}...')
                raise
        return data

    def Mkdir_path(self, path):
        # if not os.path.exists(path):
        #     os.mkdir(path)
        os.makedirs(path, exist_ok=True)
        return path

    def Get_photo_lists(self, gtk=None, hostUin=None, uin=None):
        param = {
            'g_tk': gtk or self.gtk,
            'hostUin': hostUin or (self.hostUin if self.hostUin else self.uin),
            'uin': uin or self.uin,
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
        queue_print(f">> 相册{file_name}开始下载...")
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
            queue_print(f">> 当前URL: {url}")
            read = requests.get(url)
            with open(path, 'wb+') as file:
                file.write(read.content)
            queue_print(f">> {pic_name} 下载成功")
        queue_print(f">> 相册{file_name}下载完成...")

    def Downloads(self, data):
        file_name = data["data"]["topic"]['name']
        root = self.Mkdir_path(os.path.join(self.root, file_name))
        contents = []
        temp_pic_names = []
        for photo in data["data"]["photoList"]:
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

            contents.append((pic_name, url, photo))

        with open('./url.txt', 'w+') as f:
            for pic_name, url, photo in contents:
                f.write(pic_name + " " + url + '\n')
        queue_print(">> 图片信息写入url.txt完成")

        queue_print(">> 正式开始下载...")

        def thread_find(id):
            total_length = len(contents)
            gap = math.ceil(total_length / self.threads_num)
            start = gap * id
            end = gap * (id + 1)
            end = end if end <= total_length else total_length
            queue_print('>> [{}]当前线程分配区域: [{}~{})'.format(id, start, end))
            datas = SimpleQueueFetch(contents[start:end].copy())
            while True:
                item = datas.get()
                if not item:
                    queue_print('>> [{}]没有更多内容，当前线程完成'.format(id))
                    break
                pic_name, url, photo = item
                path = os.path.join(root, pic_name)
                queue_print('>> [{}]当前下载：{} - {}'.format(id, path, url))
                cnt_retry = 0
                max_retry = 5
                while cnt_retry < max_retry:
                    try:
                        read = requests.get(url, timeout=5)
                        with open(path, 'wb+') as file:
                            file.write(read.content)
                        queue_print(f">> [{id}] {pic_name} 下载成功")
                        write_exif_to_image(path, photo)
                        break
                    except:
                        cnt_retry += 1
                        queue_print(
                            '>> [{}] 下载超时，即将重试{}/{}'.format(id, cnt_retry, max_retry))
                time.sleep(0.1)

        # with ThreadPoolExecutor(self.threads_num) as executor:  # 创建 ThreadPoolExecutor
        #     future_list = [executor.submit(thread_find, id) for id in range(self.threads_num)]
        # results = []
        # for future in as_completed(future_list):
        #     results.append(future.result())  # 获取任务结果

        pool = []
        for id in range(self.threads_num):
            pool.append(threading.Thread(
                target=thread_find, args=(id, ), daemon=True))
        for t in pool:
            t.start()
        for t in pool:
            t.join()

        queue_print(f">> 相册 {file_name} 下载完成...")

    def main(self):
        photos_lists = self.Get_photo_lists()
        queue_print(photos_lists)
        if photos_lists['code'] != 0:
            queue_print('>> 相册获取失败')
            return
        index = 1
        queue_print(">> 你共有以下相册，请输入需要下载相册的序号 \r\n")
        temp_msg = '>> 你共有以下相册，请输入需要下载相册的序号 \r\n'
        try:
            album_lists = photos_lists["data"]['albumListModeSort']
        except:
            album_lists = []
            for item in photos_lists["data"]['albumListModeClass']:
                album_lists += (item['albumList'] or [])
            # photos_lists = photos_lists["data"]['albumListModeClass'][0]['albumList']
        for photos_list in album_lists:
            name = photos_list['name']
            num = photos_list['total']
            allowAccess = '加密' if photos_list['allowAccess'] == 0 else '开放'
            msg = "[{}] ({}) {} - {}".format(index, allowAccess, name, num)
            queue_print(msg)
            temp_msg += msg + '\n'
            index += 1

        # which_album = int(input("输入数字(如:1) ").strip()) - 1
        temp_msg += '\n- 输入对应数字(如: 1). \n- 支持多个(如: 1,3,5). \n- 支持全部(如: 0)'
        try:
            album_index = pyautogui.prompt(text=temp_msg, title='选择待下载相册', default='1').strip()
            if album_index == '': 
                pyautogui.alert(title='温馨提示', text='请检查输入', button='明白')
                return
            album_index = album_index.replace('，', ',').replace(' ', '')
            if album_index == '0': album_index = list(range(len(album_lists)))
            else: album_index = [int(i)-1 for i in album_index.split(',')]
        except Exception as e:
            print(e)
            pyautogui.alert(title='温馨提示', text='请检查输入', button='明白')
            return

        for which_album in album_index:
            list_id = album_lists[which_album]['id']
            num = album_lists[which_album]['total']
            queue_print('>> 获取照片中...')
            start = 0
            Photos_datas = None
            current_num = 0
            page_size = 100
            while current_num < num:
                try:
                    Photos_data = self.Get_photos(list_id, page_size, start=start)
                    if not Photos_data.get("data") or not Photos_data["data"].get("photoList"):
                        queue_print('>> 无更多项')
                        break
                    photo_list = Photos_data["data"]["photoList"]
                    current_num += len(photo_list)
                    start = current_num
                    queue_print('>> 本次获取到{}项，共{}项'.format(len(photo_list), num))
                    if not Photos_datas:
                        Photos_datas = Photos_data
                    elif photo_list:
                        Photos_datas["data"]["photoList"].extend(photo_list)
                except Exception as e:
                    queue_print(f'>> 获取照片出错: {e}')
                    queue_print('>> 尝试减少每页数量重试...')
                    page_size = max(20, page_size // 2)
                    if page_size < 20:
                        queue_print('>> 重试失败，跳过此批次')
                        start += 100
                        current_num = start
            queue_print('>> 下载照片中...')
            if Photos_datas:
                self.Downloads(Photos_datas)
            else:
                queue_print('>> 未获取到照片数据')

from tkinter import END
class MyWin(Win):
    def __init__(self):
        super().__init__()
        self.button_start_enable_flag = True
        self.download_album_start_evt = False
        
        if os.path.exists('config.json'):
            with open('config.json', 'r+', encoding='utf8') as f:
                config_f = json5.loads(f.read())
            self.tk_input_username.delete('0', END)
            self.tk_input_password.delete('0', END)
            self.tk_input_other_username.delete('0', END)
            self.tk_input_save_path.delete('0', END)
            self.tk_input_threads_num.delete('0', END)
            self.tk_input_username.insert('0', config_f['username'])
            self.tk_input_password.insert('0', config_f['password'])
            self.tk_input_other_username.insert('0', config_f['other_username'])
            self.tk_input_save_path.insert('0', config_f['save_path'])
            self.tk_input_threads_num.insert('0', config_f['threads_num'])
        
        threading.Thread(target=self.simple_daemon_thread, daemon=True).start()
        threading.Thread(target=self.mainloop_thread, daemon=True).start()
    
    def simple_daemon_thread(self):
        while True:
            if not global_queue.empty():
                m = global_queue.get()
                self.append_debug(m)
            self.enable_button_start() if self.button_start_enable_flag else self.disable_button_start()
            time.sleep(0.01)
    
    
    def start_process(self):
        self.update_debug('')
        if self.tk_input_username.get().strip() == '':
            pyautogui.alert(
                title='缺少必填项', text='你的QQ号是必须要填的，其他可选', button='明白')
            return

        self.button_start_enable_flag = False
        
        username = self.tk_input_username.get().strip()
        password = self.tk_input_password.get().strip()
        save_path = self.tk_input_save_path.get().strip()
        other_username = self.tk_input_other_username.get().strip()
        other_username = other_username if other_username != '' else username
        threads_num = self.tk_input_threads_num.get().strip()
        threads_num = int(threads_num) if threads_num else 4
        
        contents = ''
        if os.path.exists('config.json'):
            with open('config.json', 'r+', encoding='utf8') as f:
                contents = f.read()
        config_f = json5.loads(contents) if contents else {}  
        with open('config.json', 'w+', encoding='utf8') as f:
            config_f["username"] = username
            config_f["password"] = password
            config_f["other_username"] = other_username
            config_f["threads_num"] = threads_num
            config_f["save_path"] = save_path
            f.write(json.dumps(config_f))
        
        queue_print('*'*60+'\r\n\t\t    即将开始!')
        queue_print('*'*60)
        time.sleep(2)

        def start_album_download():
            with open('config.json', 'r+', encoding='utf8') as f:
                config_f = json.loads(f.read())
                final_ck = config_f.get('final_ck')
                gtk = config_f.get('gtk')
                uin = config_f.get('uin')
            
            if final_ck and gtk and uin:
                print('Cookie已存在, 检查有效性')
                print()
            if self.check_cookie(final_ck, uin, gtk):
                print('Cookie有效')
            else:
                queue_print('>> 1.先模拟登陆获取cookie')
                Login = QQZone(username=username, password=password,
                            other_username=other_username)
                try:
                    cookies, gtk, uin = Login.login()
                except Exception as e:
                    queue_print('\n\n遇到错误了：\n' + str(e))
                    pyautogui.alert(title='遇到错误了', text=str(e), button='了解')
                    self.button_start_enable_flag = True
                    return
                final_ck = ''
                for ck in cookies:
                    final_ck += '{}={};'.format(ck['name'], ck['value'])
            queue_print(f'>> gtk: {gtk}')
            queue_print(f'>> uin: {uin}')
            queue_print(f'>> final_ck: {final_ck}')

            with open('config.json', 'w+', encoding='utf8') as f:
                config_f['gtk'] = gtk
                config_f['uin'] = uin
                config_f['final_ck'] = final_ck
                f.write(json.dumps(config_f))
            
            queue_print('>> 2.再开始下载相册')
            spider = QQZonePictures(
                cookies=final_ck,
                gtk=gtk,
                uin=uin,
                host_uin=other_username,
                save_path=save_path,
                threads_num=threads_num
            )
            try:
                spider.main()
                pyautogui.alert(title='温馨提示', text='本次下载完成了~\n重新点击>>启动<<可以再次下载', button='明白')
            except Exception as e:
                queue_print('\n\n遇到错误了：\n' + str(e))
                pyautogui.alert(title='遇到错误了', text=str(e), button='了解')
            self.button_start_enable_flag = True
        start_album_download()
    
      
    def mainloop_thread(self):
        while True:
            if self.download_album_start_evt:
                self.start_process()
                self.download_album_start_evt = False
            time.sleep(1)
                
    def check_cookie(self, cookies, uin, gtk):
        res = QQZonePictures(cookies=cookies, uin=uin, gtk=gtk).Get_photo_lists()
        queue_print(res)
        return res['code'] != -3000

    def start(self, evt):
        self.download_album_start_evt = True


if __name__ == "__main__":
    win = MyWin()
    win.mainloop()
