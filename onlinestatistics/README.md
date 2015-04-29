##使用流程

	# 安装最新版docker，方便以后安装docker compose等
	add-apt-repository ppa:docker-maint/testing
	apt-get update
	apt-get install docker.io
	# 切换到目录
	cd **
	# 创建docker镜像
	docker build -t myimage .
	# 创建容器并运行
	-d指代后台运行
	--restart设定重启方式，设置为always当系统重启时该重启将自启动，免去了使用supervisor的麻烦
	-e 添加环境变量到容器
	docker run -d --restart=always -e HOSTIP=$(curl ipinfo.io/ip) myimage
	# 查看正在容器ID
	docker ps
	# 如果没法发生问题则会看到ID，可以查看输出日志
	docker logs <container id>
	# 今天要更新代码，居然一下忘记怎么更新了Orz
	cd ~/Code/Path
	docker ps
	docker stop ContainerId
	docker rm ContainerId
	docker rmi dependencdIMG
	docker bulid -t myimage .
	docker run -d --restart=always -e HOSTIP=$(curl ipinfo.io/ip) myimage
	# 顺便改个名，好用logs查看日志
	docker ps
	docker rename Old New
	
	~~~~~~~其他命令请查看docker man	

####以下是其他感想~~~~
--------
- 如果要配合docker compose这个工具编排docker的话 那么需要**安装1.3以上版本**
- docker发展中改变略大，比如前期是server docker.io restart 后前变成了docker
- 由于在容器当中，所以链接host上的数据库localhost地址变得不可用，postgres需设置/etc/postgresql/9.4/main/pg_hab.conf允许远程访问，同时postgresql.conf中listen_address设置为*
- 设置远程访问后，就需要有服务器外网ip才能连接数据库，不可能每个环境自己去单独设置IP，这里选用了环境变量，使用curl获取公网IP有以下几个地址：
   - ifconfig.me 最知名的，结果速度异常慢，发生404的情况也是有的
   - ifconfig.io 速度非常快，但是返回有可能是IPV6啊摔
   - ip.cn 域名很好记，但是你返回那么多无用信息是干啥，不用说。就是没打算方便别人用的
   - ipinfo.io/ip 虽然长了点，但是最少还能用，就选你了
- 巨坑的是：**千万不用选用python：2.7镜像作为模板**，虽然预装了pip和一些其他的依赖，但是使用apt-get install python-xxx 安装的第三方包是没法使用的，真是呵呵了，而且apt-get build-dep这样的命令没法正常使用，莫名奇妙的问题还有→→→即使成功使用build-dep那么你还需要单独将pip install pyquery成行，放在requirements.txt里面一样是没法成功安装的~~~就在这里我折腾了将近三小时
- 最值得欣慰的是不用supervisor写脚本设置开机自启动,很方便~~

####以下是动机
-----------
- 一个原因是Docker火啊，去年就看过，不过那时太不成熟，就没试试。
- 最根本的原因是代替tmux看日志，以前都用tmux new -s XXX -d然后tmux a进去看日志啊，万一被重启还得搞一趟啊。然后现在只需要docker logs XX就够了~~~~~~~

