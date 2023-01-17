from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
import tkinter
import tkinter.simpledialog


# 自动隐藏滚动条
def scrollbar_autohide(bar,widget):
    def show():
        bar.lift(widget)
    def hide():
        bar.lower(widget)
    hide()
    widget.bind("<Enter>", lambda e: show())
    bar.bind("<Enter>", lambda e: show())
    widget.bind("<Leave>", lambda e: hide())
    bar.bind("<Leave>", lambda e: hide())


class Simpledialog:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def create(title='', prompt='', initialvalue=''):
        root = tkinter.Tk()
        # 隐藏空白主窗口
        root.withdraw()
        result = tkinter.simpledialog.askstring(title=title, prompt=prompt, initialvalue=initialvalue)
        root.destroy()
        return result

class SimpleMessagebox:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def create(title='', message='', msg_type='error'):
        root = tkinter.Tk()
        # 隐藏空白主窗口
        root.withdraw()
        result = ''
        if msg_type=='error':
            result = tkinter.messagebox.showerror(title=title, message=message)
        elif msg_type=='warning':
            result = tkinter.messagebox.showwarning(title=title, message=message)
        root.destroy()
        return result

class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_button_start = self.__tk_button_start()
        self.tk_text_debug = self.__tk_text_debug()
        self.tk_label_username = self.__tk_label_username()
        self.tk_input_username = self.__tk_input_username()
        self.tk_label_password = self.__tk_label_password()
        self.tk_input_password = self.__tk_input_password()
        self.tk_label_other_username = self.__tk_label_other_username()
        self.tk_input_other_username = self.__tk_input_other_username()
        self.tk_label_threads_num = self.__tk_label_threads_num()
        self.tk_input_threads_num = self.__tk_input_threads_num()
        self.tk_label_frame_note = Frame_note(self)
        self.tk_label_save_path = self.__tk_label_save_path()
        self.tk_input_save_path = self.__tk_input_save_path()
        self.tk_button_select_path = self.__tk_button_select_path()

    def __win(self):
        self.title("QQ空间相册批量下载")
        # 设置窗口大小、居中
        width = 568
        height = 487
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

    def __tk_button_start(self):
        btn = Button(self, text="启动")
        btn.place(x=20, y=276, width=532, height=33)
        return btn

    def __tk_text_debug(self):
        text = Text(self)
        text.place(x=20, y=321, width=530, height=157)
        
        vbar = Scrollbar(self)
        text.configure(yscrollcommand=vbar.set)
        vbar.config(command=text.yview)
        vbar.place(x=535, y=321, width=15, height=157)
        scrollbar_autohide(vbar,text)
        return text

    def __tk_label_username(self):
        label = Label(self,text="你的QQ账号",anchor="center")
        label.place(x=20, y=180, width=90, height=24)
        return label

    def __tk_input_username(self):
        ipt = Entry(self)
        ipt.place(x=120, y=180, width=150, height=24)
        return ipt

    def __tk_label_password(self):
        label = Label(self,text="你的QQ密码",anchor="center")
        label.place(x=300, y=180, width=90, height=24)
        return label

    def __tk_input_password(self):
        ipt = Entry(self, show='*')
        ipt.place(x=400, y=180, width=150, height=24)
        return ipt

    def __tk_label_other_username(self):
        label = Label(self,text="对方QQ账号",anchor="center")
        label.place(x=20, y=210, width=90, height=24)
        return label

    def __tk_input_other_username(self):
        ipt = Entry(self)
        ipt.place(x=120, y=210, width=150, height=24)
        return ipt

    def __tk_label_threads_num(self):
        label = Label(self,text="下载线程数",anchor="center")
        label.place(x=300, y=210, width=90, height=24)
        return label

    def __tk_input_threads_num(self):
        ipt = Entry(self)
        ipt.insert(0, '4')
        ipt.place(x=400, y=210, width=150, height=24)
        return ipt

    def __tk_label_save_path(self):
        label = Label(self,text="保存的路径",anchor="center")
        label.place(x=20, y=240, width=90, height=24)
        return label

    def __tk_input_save_path(self):
        ipt = Entry(self)
        ipt.delete('0', END)
        ipt.insert('0', './QQZone')
        ipt.place(x=120, y=240, width=350, height=24)
        return ipt

    def __tk_button_select_path(self):
        btn = Button(self, text="选择路径")
        btn.place(x=480, y=240, width=70, height=25)
        return btn


class Frame_note(LabelFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.__frame()
        self.tk_label_note3 = self.__tk_label_note3()
        self.tk_label_note2 = self.__tk_label_note2()
        self.tk_label_note1 = self.__tk_label_note1()
        self.tk_label_note4 = self.__tk_label_note4()
    def __frame(self):
        self.configure(text="使用说明")
        self.place(x=20, y=10, width=530, height=148)

    def __tk_label_note1(self):
        label = Label(self,text="1、此工具来自“小锋学长生活大爆炸”，仅做学习交流，请勿用于非法用途!",anchor="w")
        label.place(x=20, y=0, width=496, height=24)
        return label
        
    def __tk_label_note2(self):
        label = Label(self,text="2、填写完信息后，点击“启动”按钮即可；",anchor="w")
        label.place(x=20, y=30, width=496, height=24)
        return label

    def __tk_label_note3(self):
        label = Label(self,text="3、若对方Q号为空，则为下载自己；若你的Q密为空，则需手动完成登录；",anchor="w")
        label.place(x=20, y=60, width=497, height=24)
        return label

    def __tk_label_note4(self):
        label = Label(self,text="4、由于登录可能有问题，建议先在电脑上登录QQ，以便使用快捷登录。",anchor="w")
        label.place(x=20, y=90, width=496, height=24)
        return label

class Win(WinGUI):
    def __init__(self):
        super().__init__()
        self.__event_bind()

    def update_debug(self, strings):
        self.tk_text_debug.delete('1.0', END)
        self.tk_text_debug.insert('1.0', strings)
        self.tk_text_debug.update()
        self.tk_text_debug.see(END)

    def append_debug(self, strings, end='\n'):
        self.tk_text_debug.insert(END, str(strings)+end)
        self.tk_text_debug.update()
        self.tk_text_debug.see(END)

    def start(self, evt):
        pass

    def select_path(self,evt):
        path = filedialog.askdirectory(title='请选择一个目录')
        if path:
            self.tk_input_save_path.delete('0', END)
            self.tk_input_save_path.insert('0', path)
        
    def __event_bind(self):
        self.tk_button_start.bind('<Button-1>', self.start)
        self.tk_button_select_path.bind('<Button-1>', self.select_path)
    
    def disable_button_start(self):
        self.tk_button_start.config(state=DISABLED, text="运行中...")
        self.tk_button_start.update()
        self.tk_button_start.unbind("<Button-1>")

    def enable_button_start(self):
        self.tk_button_start.config(state=NORMAL, text="启动")
        self.tk_button_start.update()
        self.tk_button_start.bind('<Button-1>', self.start)


if __name__ == "__main__":
    win = Win()
    win.mainloop()
