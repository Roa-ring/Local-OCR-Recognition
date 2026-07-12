# Local-OCR-Recognition
OCR（光学字符识别）模型为轻量化视觉识别模型，融合文字检测与字符识别双模块，可自动定位图像中文字区域，识别印刷体、常规手写体等各类文本，本地部署后可 实现无网络高速文字提取，适配图片文档、截图等多场景文字识别需求。

## 安装方式
建议使用python 3.12.10版本，建议创建虚拟环境管理，
请依照以下指令安装
克隆仓库
```
git clone https://github.com/Roa-ring/Local-OCR-Recognition.git
cd Local-OCR-Recognition
```
创建虚拟环境（如果需要）
```
py -3.12 -m venv LOR
LOR\Scripts\Activate.ps1
```
如果运行脚本出现报错请自行修改powershell安全策略
```
pip install -r requirements.txt
```

## 使用
运行app.py,在浏览器访问http://127.0.0.1:5000，应当出现以下界面
<div align="center">
<img src="https://github.com/Roa-ring/Local-OCR-Recognition/blob/main/_tmp/readme4.png" width="800"/>
</div>
支持点击、拖拽文件夹、或 Ctrl+V 粘贴截图上传
支持批量处理
采用金字塔缩放加速大图/高分辨率图像识别
可能降低识别准确率，在追求极致准确率时可关闭
右键已上传图片可裁剪识别区域
<div align="center">
<img src="https://github.com/Roa-ring/Local-OCR-Recognition/blob/main/_tmp/readme3.png" width="800"/>
</div>

右上角点击**历史搜索**进入历史记录界面
支持按时间或按关键字模糊搜索以及时间区间搜索
如：20260710 / 2026-07-10 / 2026年7月
区间搜索请用"~"连接起始时间和终止时间
搜索时请补全月和日，如7月应当补全为07
<div align="center">
<img src="https://github.com/Roa-ring/Local-OCR-Recognition/blob/main/_tmp/readme1.png" width="800"/>
</div>

