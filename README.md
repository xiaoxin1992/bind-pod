# Bind-pod
[![Python3](https://img.shields.io/badge/Python-3.6.12-blue.svg?style=popout&)](https://www.python.org/)
[![Django2](https://img.shields.io/badge/Django-2.1.5-brightgreen.svg?style=popout)](https://www.djangoproject.com/)
[![Bind](https://img.shields.io/badge/Bind-9.11.4-orange.svg?style=popout)](http://www.isc.org/)
[![DnsPython](https://img.shields.io/badge/DnsPython-2.0.0-9cf.svg?style=popout)](http://www.dnspython.org/)
[![DjangoRestFramework](https://img.shields.io/badge/DjangoRestFramework-3.11.0-yellow.svg?style=popout)](https://www.django-rest-framework.org/)
[![GitHub](https://img.shields.io/github/license/xiaoxin1992/bind-pod)](https://github.com/xiaoxin1992/bind-pod/edit/main/LICENSE)

Bind9 web管理平台并提供API接口调用

 使用方法
 
 安装NPM、Python3、Nginx
 ```shell script
yum -y install epel-release
yum -y install python3-devel python3 python3-pip python3-setuptools python3-libs npm nginx
```

获取源码
```shell script
git clone https://github.com/xiaoxin1992/bind-pod.git
cd bind-pod
```



安装Python依赖
```shell script
pip3 install -i http://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
```

手动启动
```shell script
python3 manage.py runserver 0.0.0.0:8080
```

uwsgi 配置
```ini
[uwsgi]
chdir=/srv/BindPod          #  根据自己的项目路径填写
home = /usr
pythonpath=/srv/BindPod     #  根据自己的项目路径填写
http=0.0.0.0:8080
master=true
processes=4
threads=2
uid=root
gid=root
thunder-lock=true
enable-threads=true
module=bind-pod.wsgi
socket=bind-pod.sock
pidfile=bind-pod.pid
chmod-socket = 666
vacuum = true
die-on-term = true
```

uwsgi 启动
```shell script
uwsgi  --ini uwsgi.ini
```


前端页面编译

修改web页面访问地址
```shell script
sed -i 's/192.168.117.128:8000/10.10.20.30:8080/g' web/bindpod/src/main.js
把10.10.20.30:8080 改成你自己要监听的IP地址和端口
```

手动编译前端文件
```shell script
cd web/bindpod
npm install --registry https://registry.npm.taobao.org 
npm run build
cp -a web/bindpod/dist /usr/share/nginx/html
```
启动Nginx服务器


api接口文档地址: http://ipaddress:port/docs/#api


访问api需要先通过:http://ipaddress:port/login/接口获取Token
登陆接口返回参数如下
```json
{
"display_name": "xiaoxin",
"username": "root",
"Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjAzMzQ0MzE2LCJqdGkiOiI1Zjg1MzI3Y2M4MjY0MjhkYmUyMGYxNWFhZDlkNDdjNSIsInVzZXJfaWQiOjF9.bE4ub_f-Nb1RGLzqsT-XqtgOD4oRXmeYwDpdqNbcbnk",
"UserType": "admin",
"active": "admin",
"is_staff": true
}
display_name        表示用户中文名称
username            登陆用户名
Token               登陆Token
UserType            用户类型（admin表示管理员，user表示普通用户）
active              表示用户是否允许登陆
is_staff        表示用户是否是超级管理员
```

拿到Token后在请求头添加Token
```json
{
"Authorization": "Token eyJ0eXAiOiJKV1QiLCJh"
}
```


Bind9 配置

首先配置rndc
```shell script
rndc-confgen  #  生成rndc配置
```
rndc 配置文件内容如下 "/etc/rndc.key"
```text
key "rndc-key" {
	algorithm hmac-md5;
	secret "8XhahdtLNWhIfpDQjdhvOQ==";
};
```
rndc 配置文件的key配置放入到named.conf文件中
```text
    key "rndc-key" {
        algorithm hmac-md5;
        secret "8XhahdtLNWhIfpDQjdhvOQ==";
    };
```

配置域名管理key
```shell script
cd /var/named/
dnssec-keygen -a HMAC-MD5 -b 128 -n USER bindpod
chown named.named Kbindpod.*
cat  Kbindpod.+157+52547.key
bindpod. IN KEY 0 3 157 HykrxxHfxz2SuFHC7wfSFg==
```


配置 /etc/named.conf, 添加域名管理配置Key
```shell script
key "bindpod" {
	algorithm hmac-md5;
	secret "HykrxxHfxz2SuFHC7wfSFg==";
};
```

/etc/named.conf 配置域名
````shell script
zone "test.com" IN {
    type master;
    file "test.com.zone";
    allow-update { key bindpod; };   # key 必须等于域名管理的key名称
};
````
修改服务配置文件
```shell script
cd  BindPod/BindPod
vim settings.py
DNS_BASE_CONFIG = {
    "server": "127.0.0.1",                服务地址，默认即可
    "port": 53,                           服务端口，默认即可
    "key": "bindpod",                      key
    "secret": "HykrxxHfxz2SuFHC7wfSFg=="  验证密钥
}
```
完成后重启BindPod服务
 
创建好域名后，在平台中添加域名后可以使用

### 默认密码
登陆账号需要使用Django重的manage.py脚本创建一个超级用户即可登陆

```shell
python3 ./manage.py  createsuperuser
```



