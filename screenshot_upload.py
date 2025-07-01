import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont
import keyboard
import pyperclip
import requests
import os
import json
from datetime import datetime
import pystray

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Imgbb Screenshot Uploader")
        self.root.geometry("450x450")  # 增加高度以容纳新控件
        self.root.resizable(False, False)
        
        # 设置现代主题
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 11))
        style.configure("TEntry", padding=5)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 标题和来源
        ttk.Label(main_frame, text="📷 Imgbb Screenshot Uploader", font=('Helvetica', 14, 'bold')).pack(pady=5)
        ttk.Label(main_frame, text="From: CMC.CM", font=('Helvetica', 10, 'italic')).pack(pady=2)
        
        # API 密钥输入
        ttk.Label(main_frame, text="ImgBB API 密钥:").pack(pady=5)
        self.api_key_entry = ttk.Entry(main_frame, width=40)
        self.api_key_entry.pack(pady=5)
        
        # 快捷键输入
        ttk.Label(main_frame, text="截图快捷键（例: ctrl+alt+w）:").pack(pady=5)
        self.hotkey_entry = ttk.Entry(main_frame, width=40)
        self.hotkey_entry.pack(pady=5)
        
        # 保存目录输入
        ttk.Label(main_frame, text="截图保存目录:").pack(pady=5)
        self.save_dir_entry = ttk.Entry(main_frame, width=40)
        self.save_dir_entry.pack(pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.choose_save_dir).pack(pady=5)
        
        # 水印文本输入
        ttk.Label(main_frame, text="水印文本（留空则无水印）:").pack(pady=5)
        self.watermark_entry = ttk.Entry(main_frame, width=40)
        self.watermark_entry.pack(pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="按快捷键截图")
        self.status_label.pack(pady=10)
        
        # URL 显示
        self.url_label = ttk.Label(main_frame, text="", wraplength=400, font=('Helvetica', 10))
        self.url_label.pack(pady=10)
        
        # 截图画布
        self.canvas = tk.Canvas(main_frame, width=200, height=100, bg="white", highlightthickness=1, relief="flat")
        self.canvas.pack(pady=10)
        self.screenshot_image = None
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="保存设置", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="最小化到托盘", command=self.minimize_to_tray).pack(side="left", padx=5)
        ttk.Button(button_frame, text="退出", command=self.quit).pack(side="left", padx=5)
        
        # 系统托盘
        self.icon = None
        self.setup_system_tray()
        
        # 加载配置
        self.current_hotkey = "ctrl+alt+w"  # 默认快捷键
        self.load_settings()
        
        # 绑定快捷键
        keyboard.add_hotkey(self.current_hotkey, self.start_screenshot)
        
        # 区域选择变量
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.screenshot_window = None
        self.was_minimized = False
        
        # 捕获最小化事件
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        self.root.mainloop()
    
    def setup_system_tray(self):
        # 创建简单托盘图标
        image = Image.new('RGB', (16, 16), color='black')
        draw = ImageDraw.Draw(image)
        draw.text((2, 2), "S", fill='white')
        self.icon = pystray.Icon(
            "Imgbb Screenshot Uploader",
            image,
            "Imgbb Screenshot Uploader",
            menu=pystray.Menu(
                pystray.MenuItem("显示窗口", self.show_window),
                pystray.MenuItem("退出", self.quit)
            )
        )
    
    def minimize_to_tray(self):
        self.root.withdraw()
        if not self.icon:
            self.setup_system_tray()
        self.icon.run_detached()
    
    def show_window(self):
        if self.icon:
            self.icon.stop()
            self.icon = None
        self.root.deiconify()
    
    def quit(self):
        if self.icon:
            self.icon.stop()
        keyboard.unhook_all()
        self.root.quit()
    
    def load_settings(self):
        config_file = "config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
                    self.api_key_entry.insert(0, config.get("api_key", ""))
                    self.hotkey_entry.insert(0, config.get("hotkey", "ctrl+alt+w"))
                    self.save_dir_entry.insert(0, config.get("save_dir", "D:/Screenshot"))
                    self.watermark_entry.insert(0, config.get("watermark_text", ""))
                    self.current_hotkey = config.get("hotkey", "ctrl+alt+w")
        except Exception as e:
            messagebox.showwarning("警告", f"加载设置失败: {str(e)}")
    
    def save_settings(self):
        api_key = self.api_key_entry.get()
        hotkey = self.hotkey_entry.get()
        save_dir = self.save_dir_entry.get()
        watermark_text = self.watermark_entry.get()
        config_file = "config.json"
        try:
            # 保存新设置
            with open(config_file, "w") as f:
                json.dump({
                    "api_key": api_key,
                    "hotkey": hotkey,
                    "save_dir": save_dir,
                    "watermark_text": watermark_text
                }, f)
            # 更新快捷键
            if hotkey and hotkey != self.current_hotkey:
                keyboard.unhook_all()
                self.current_hotkey = hotkey
                keyboard.add_hotkey(self.current_hotkey, self.start_screenshot)
                self.status_label.config(text=f"按 {hotkey} 截图")
            messagebox.showinfo("成功", "设置保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def choose_save_dir(self):
        directory = filedialog.askdirectory(initialdir=self.save_dir_entry.get() or "D:/")
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, directory)
    
    def start_screenshot(self):
        self.was_minimized = self.root.state() == 'iconic'
        if self.was_minimized:
            self.root.deiconify()
            self.root.update()
        
        self.screenshot_window = tk.Toplevel(self.root)
        self.screenshot_window.attributes("-fullscreen", True)
        self.screenshot_window.attributes("-alpha", 0.3)
        self.screenshot_window.configure(bg="gray")
        
        self.canvas_screenshot = tk.Canvas(self.screenshot_window, highlightthickness=0)
        self.canvas_screenshot.pack(fill="both", expand=True)
        
        self.canvas_screenshot.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas_screenshot.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas_screenshot.bind("<ButtonRelease-1>", self.on_button_release)
    
    def on_button_press(self, event):
        self.start_x = self.canvas_screenshot.canvasx(event.x)
        self.start_y = self.canvas_screenshot.canvasy(event.y)
        self.rect = self.canvas_screenshot.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2
        )
    
    def on_mouse_drag(self, event):
        cur_x = self.canvas_screenshot.canvasx(event.x)
        cur_y = self.canvas_screenshot.canvasy(event.y)
        self.canvas_screenshot.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
    
    def on_button_release(self, event):
        end_x = self.canvas_screenshot.canvasx(event.x)
        end_y = self.canvas_screenshot.canvasy(event.y)
        
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        
        self.take_screenshot(x1, y1, x2, y2)
        self.screenshot_window.destroy()
        
        if self.was_minimized:
            self.minimize_to_tray()
    
    def take_screenshot(self, x1, y1, x2, y2):
        try:
            self.screenshot_window.withdraw()
            self.root.update()
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # 添加水印
            watermark_text = self.watermark_entry.get()
            if watermark_text:
                draw = ImageDraw.Draw(screenshot)
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
                position = (screenshot.width - text_width - 10, screenshot.height - text_height - 10)
                draw.text(position, watermark_text, fill=(255, 255, 255, 255), font=font)
            
            # 确保保存目录
            save_dir = self.save_dir_entry.get() or "D:/Screenshot"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 保存截图
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(save_dir, f"img_{timestamp}.png")
            screenshot.save(temp_file)
            
            # 显示缩略图
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((200, 100))
            self.screenshot_image = ImageTk.PhotoImage(thumbnail)
            self.canvas.create_image(100, 50, image=self.screenshot_image)
            
            # 上传到 ImgBB
            self.upload_to_imgbb(temp_file)
        except Exception as e:
            messagebox.showerror("错误", f"截图失败: {str(e)}")
        finally:
            if self.screenshot_window:
                self.screenshot_window.destroy()
    
    def upload_to_imgbb(self, file_path):
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("错误", "请输入 ImgBB API 密钥")
            return
        
        self.status_label.config(text="正在上传...")
        try:
            with open(file_path, "rb") as file:
                response = requests.post(
                    "https://api.imgbb.com/1/upload",
                    params={"key": api_key},
                    files={"image": file}
                )
            data = response.json()
            if data.get("success"):
                url = data["data"]["url"]
                self.url_label.config(text=f"已上传: {url}")
                pyperclip.copy(url)
                self.status_label.config(text="上传成功！URL 已复制到剪贴板。")
            else:
                self.status_label.config(text="上传失败: " + data.get("error", {}).get("message", "未知错误"))
        except Exception as e:
            self.status_label.config(text=f"上传失败: {str(e)}")

if __name__ == "__main__":
    app = ScreenshotApp()
