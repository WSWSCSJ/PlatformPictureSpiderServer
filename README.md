# PlatformPictureSpiderServer

```python
"""
@Author: WSWSCSJ
JD|TM|TB 商品图片 主图|详情图|颜色图 的爬取和打包zip下载
仅供学习与参考,擅自修改和使用造成的责任概不负责
"""
```
### Project
+ Spider
    + proxy 封装的全局单例代理池对象
    + spider 抽象三个平台的抓取流程
    + ziptool 根据zipfile源码重写压缩方法,实现在内存中打包

### Requirement
```
“”“
其他版本会造成SSL unknown protocol error
requests == 2.20.0
python3 == 3.7.8
”“”
```
