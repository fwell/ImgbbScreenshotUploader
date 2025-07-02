# ImgbbScreenshotUploader
Quickly take screenshots and upload them to imgBB. You can set simple text watermarks, customize shortcut keys, and set temporary folder support.
快速截取屏幕截图并上传至 imgBB。您可以设置简单的文字水印、自定义快捷键以及设置临时文件夹支持。

# 自行编译
## 安装依赖库
```bash
pip install pillow keyboard requests pyperclip

```
## 安装打包程序
```bash
pip install pyinstaller
```
## 打包程序
```bash
pyinstaller --onefile --windowed --name ImgbbScreenshotUploader screenshot_upload.py
```
## 获取API

1. Users need to apply for an account on imgbb.com.
2. Apply for API
3. Simply fill in the API information into the software
4. The program is completely written with Grok

1. 用户需要到imgbb.com上申请一个账户。
2. 申请API
3. 将API信息填入软件中即可
4. 程序完全是有grok编写的

# 成品使用
## 下载已安装好的程序
### win x64 下载程序：https://github.com/fwell/ImgbbScreenshotUploader/releases
## 编辑配置文件
配置文件在config.json文件中
### 在线教程 https://cmc.cm/post/22.html
![demo](https://github.com/user-attachments/assets/086220cd-7e5f-491e-99f4-18bcb65c57ed)
