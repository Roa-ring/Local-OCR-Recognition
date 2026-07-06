# Local-OCR-Recognition
OCR（光学字符识别）模型为轻量化视觉识别模型，融合文字检测与字符识别双模 块，可自动定位图像中文字区域，识别印刷体、常规手写体等各类文本，本地部署后可 实现无网络高速文字提取，适配图片文档、截图等多场景文字识别需求。

python版本为3.12.10，未安装对应版本请自行安装
https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
请按照以下步骤进行部署：
git init
git clone https://github.com/Roa-ring/Local-OCR-Recognition.git
pip install -r requirements.txt
LOR\Scripts\activate.bat

请在修改时创建新的分支
请不要随意修改main分支
请务必在虚拟环境下运行项目文件，做出修改
请注意，由于gitignore会默认添加依赖，请在修改项目依赖后添加适当说明并修改requirements文件