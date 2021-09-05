# autopass-chaoxing-video
本程序不会下载视频,通过请求API实现

## 使用方法

#### Windows

可以下载 [releases](https://github.com/yuban10703/autopass-chaoxing-video/releases) 中打包好的exe 

在main.exe目录下,按住shift + 鼠标右键空白区域(比如图中的绿框区域), 然后打开powershell

![image-20210905162419642](https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/20210905162419.png)

输入
```
.\main.exe
```
回车启动程序

![image-20210905162653506](https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/20210905162653.png)

#### Linux

> 推荐使用Ubuntu20.04 或更高版本
>
> **python版本需 >= 3.8**

clone项目

```
 git clone https://github.com/yuban10703/autopass-chaoxing-video --depth=1
```

进入项目目录

 ```
cd autopass-chaoxing-video
 ```

安装要用到的包

```
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

启动

```
python3 main.py
```

> 断开SSH后保持运行请自己使用screen之类的工具
