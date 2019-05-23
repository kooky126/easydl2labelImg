# easydl2labelImg

easydl数据集导出到labelImg工具

数据集导出并没有官方的api，本工具模拟浏览器下载实现，并不能保证一定可用

1 将本代码下载到本地

2 正常登录自己的百度账号，进入物体检测数据集页面

3 使用cookie工具导出当前cookie到cookie.txt文件，格式为 Netscape HTTP Cookie File

4 记下要导出的数据集id备用

代码基于python 3.6，不同版本请自行修改代码调试

参考test.py,一个语句就可以完成数据集的导出（参数为数据集id和labelImg数据目录，labelImg目录需要预先建好）


代码调用方式(参考test.py)

import easydl2labelImg

easydl2labelImg.downloaddateset(20076,r"C:\\Users\\KOOKY\\Desktop\\works")


或者直接命令行方式调用

python main.py -dataset_id 20076 -xmlpath C:\\Users\\KOOKY\\Desktop\\works




————————————————————————————————————————————————————————————————————————————————————————————————————

本地labelImg数据上载到easydl工具参见：

https://github.com/kooky126/labelImg2easydl
