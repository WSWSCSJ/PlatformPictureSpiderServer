# PlatformPictureSpiderServer

```python
"""
@Author: WSWSCSJ
JD|TM|TB 商品图片 主图|详情图|颜色图 的爬取和打包zip下载
仅供学习与参考,擅自修改和使用造成的责任概不负责
"""
```

### Project
+ AiohttpVersion
  + 基于 [AsyncSpider](https://github.com/WSWSCSJ/AsyncSpiderFramework) 的并发版本
  + 封装 aiomysql 的异步数据库IO
    
+ RequestVersion
    + proxy 封装的全局单例代理池对象
    + spider 抽象三个平台的抓取流程
    + ziptool 根据zipfile源码重写压缩方法,实现在内存中打包
    + requirement
      + requests == 2.20.0
      + python3 >= 3.7.0

### 2021.02.11 update
```python
"""
使用 https://github.com/WSWSCSJ/AsyncSpiderFramework 框架
重构 https://github.com/WSWSCSJ/PlatformPictureSpiderServer 项目
只重构了JD平台的模块,其他的懒得写了
相比较于旧项目使用request阻塞式的请求方式
使用aiohttp并发得处理请求性能更好效率更高
"""
```