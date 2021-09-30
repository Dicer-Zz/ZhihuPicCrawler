# 知乎回答图片爬虫

这是一个知乎回答的图片脚本，代码不长，但是：

1. 免登录不用账号密码
2. 高并发加快下载速度
3. 支持同时爬取多个问题

当然，也存在一些亟待解决的问题，header没有池化，因此在长时间运行之后可能会出现403，不过一般下载量在数个G之内问题都不大。如果真出现403，那么更换一下header即可。

欢迎提出issue & PR

# Usage

通过知乎问题链接可以获取qID（问题ID）比如 https://www.zhihu.com/question/488737569 其中 488737569 就是这个问题的唯一ID。

然后执行：

``` shell
python Spider.py -q 488737569
```

其他命令行用法请参考：

```shell
usage: Spider.py [-h] -q QIDS [QIDS ...] [-n The number of pictures Default: 2000)]
                 [--max_size The maximum size(KB) limitation of pictures (Default: 10000)]
                 [--min_size The minimum size(KB) limitation of pictures (Default: 200)]
                 [--num_workers The number of workers (Default: 20]

This is a script that can download images from Zhihu.

optional arguments:
  -h, --help            show this help message and exit
  -q QIDS [QIDS ...], --qIDs QIDS [QIDS ...]
  -n The number of pictures (Default: 2000), --num_pic The number of pictures (Default: 2000)
  --max_size The maximum size(KB) limitation of pictures (Default: 10000)
  --min_size The minimum size(KB) limitation of pictures (Default: 200)
  --num_workers The number of workers (Default: 20)
```
# 已知问题
由于控制下载图片数量的变量没有使用互斥锁，因此图片数量有可能超过限制的数量。
但是考虑到使用互斥锁（猜想）可能会降低爬虫速度，因此暂时不考虑更改。

# Reference
https://github.com/python3xxx/zhihu_spider/blob/master/zhihu_spider.py
