# Local-OCR-Recognition
OCR（光学字符识别）模型为轻量化视觉识别模型，融合文字检测与字符识别双模块，可自动定位图像中文字区域，识别印刷体、常规手写体等各类文本，本地部署后可 实现无网络高速文字提取，适配图片文档、截图等多场景文字识别需求。

## 安装方式
建议使用python 3.12.10版本，使用虚拟环境管理，
请依照以下指令安装
克隆仓库
```
git clone https://github.com/Roa-ring/Local-OCR-Recognition.git
cd Local-OCR-Recognition
```
创建虚拟环境（如果需要）
```
pip install -r requirements
```

## 使用
运行app.py,在浏览器访问http://127.0.0.1:5000，应当出现以下界面
<div align="center">
<img src="https://i0.hdslb.com/bfs/openplatform/f885a27b62b14709fccc4e780654069367f5aa13.png" width="800"/>
</div>
支持点击、拖拽文件夹、或 Ctrl+V 粘贴截图上传
支持批量处理
右键已上传图片可裁剪识别区域
右上角点击**历史搜索**进入历史记录界面
<div align="center">
<img src="https://i0.hdslb.com/bfs/openplatform/26c5016702150c0ccfc241d69fb77c669c68134c.png" width="800"/>
</div>
支持按时间或按关键字搜索

