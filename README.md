# Local-OCR-Recognition
OCR（光学字符识别）模型为轻量化视觉识别模型，融合文字检测与字符识别双模 块，可自动定位图像中文字区域，识别印刷体、常规手写体等各类文本，本地部署后可 实现无网络高速文字提取，适配图片文档、截图等多场景文字识别需求。

<<<<<<< HEAD
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
=======
请先安装以下文件：
git:https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.2/Git-2.55.0.2-64-bit.exe
python(3.12.10):https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe(window版本，其他版本请自行查找）

项目结构的构建以VScode为例
请先在插件栏安装python的相关插件
在合适的位置创建空文件夹后(文件夹名请不要带有中文），在python中依次运行以下命令：
git clone https://github.com/Roa-ring/Local-OCR-Recognition.git
py -3.12 -m venv LOR
LOR\Scripts\Activate.ps1
pip install "paddleocr[all]"
pip install paddlepaddle==3.1.1 

运行测试文件：
python test.py
python test2.py

以下为测试文件2应当的输出：
信息: 用提供的模式无法找到文件。
D:\Local-OCR-Recognition\LOR\Lib\site-packages\paddle\utils\cpp_extension\extension_utils.py:717: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)
Model files already exist. Using cached files. To redownload, please delete the directory manually: `C:\Users\never\.paddlex\official_models\PP-OCRv6_medium_rec`.
ReduceMeanCheckIfOneDNNSupport
ReduceMeanCheckIfOneDNNSupport
ReduceMeanCheckIfOneDNNSupport
ReduceMeanCheckIfOneDNNSupport
ReduceMeanCheckIfOneDNNSupport
ReduceMeanCheckIfOneDNNSupport
{'res': {'input_path': 'bdc0fe63-cf15-440f-be9c-07b04a5e63d0.png', 'page_index': None, 'rec_text': '1. 安装必要的库', 'rec_score': 0.9963347315788269}}

以下为项目注意事项：
请在新的分支中修改
请不要随意修改main分支
请务必在虚拟环境下运行项目文件，做出修改
请注意，由于gitignore会默认添加依赖，请在修改项目依赖后添加适当说明并修改requirements文件
>>>>>>> c04bb57c075776607aebfb21d5ca2935668ceba3
