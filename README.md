# QQZone_AutoDownload_Album
Python+selenium 自动下载QQ空间相册

---

> 上传QQ空间相册可以看这个：[https://github.com/1061700625/QQZone_AutoDownload_Album](https://github.com/1061700625/QQZone_Album_Upload)

---

<div style="text-align: center;">
    <img alt="" src="https://user-images.githubusercontent.com/31002981/212890235-ebc75c56-a3a1-4066-8192-31809f3bd45a.png" style="margin: 0 auto;" />
</div>


貌似腾讯的登陆加密做的很复杂。所以用selenium模拟登陆的，这样就可以绕过复杂的登陆验证了，等登陆进去后，就可以随便浪啦，解析网页啥的跟普通差不多。   


功能包括：    
- 下载自己空间的相册
- 下载他人空间的公开相册
- 更改为通用方法，导航栏无需更改为默认设置
- 自动将webp格式转为jpg


# 文件说明：
1、main.py+gui.py是界面版的。    
2、之前的console版放到了`old_file`里，可以运行`old_file/QQ空间相册下载-新.py`。    

# 运行说明：
先下载文件：
- [releases](https://github.com/1061700625/QQZone_AutoDownload_Album/releases)
- 或者直接在上发`Code -> Download ZIP`下载 （**推荐**）

**exe运行方式：**
1. 解压Chrome.zip；
2. 双击`main.exe`；

**GUI源码运行方式：**
1. 首次运行先安装依赖：`pip install -r requirements.txt`；
2. 运行py：`python main.py`。

**Console源码运行方式：**
1. 首次运行先安装依赖：`pip install -r requirements.txt`；
2. 将`old_file/QQ空间相册下载-新.py`复制出来，即放到与`main.py`同目录；
3. 运行py：`QQ空间相册下载-新.py`。

# 其他说明
1、如果是下载自己QQ号的相册，加密的相册就也可以下。因为自己进自己的相册不用密码的。        
2、一般回车程序没了是出错了，可以在桌面按住shift键，然后右击--选择“在此处打开命令窗口”，然后松开shift，把程序拖入窗口后回车，就运行了，按照步骤重新走一遍，这样就算出错了，也会显示错误信息。然后把错误信息截图我看看。       
3、使用前，请先**解压Chrome.zip**。

