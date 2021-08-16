# Bind-pod
[![Python3](https://img.shields.io/badge/Python-3.6.12-blue.svg?style=popout&)](https://www.python.org/)
[![Django2](https://img.shields.io/badge/Django-2.1.5-brightgreen.svg?style=popout)](https://www.djangoproject.com/)
[![Bind](https://img.shields.io/badge/Bind-9.11.4-orange.svg?style=popout)](http://www.isc.org/)
[![DnsPython](https://img.shields.io/badge/DnsPython-2.0.0-9cf.svg?style=popout)](http://www.dnspython.org/)
[![DjangoRestFramework](https://img.shields.io/badge/DjangoRestFramework-3.11.0-yellow.svg?style=popout)](https://www.django-rest-framework.org/)
[![GitHub](https://img.shields.io/github/license/xiaoxin1992/bind-pod)](https://github.com/xiaoxin1992/bind-pod/edit/main/LICENSE)

#### Bind9 web管理平台并提供API接口调用

##### 安装使用方法
 
###### 如果要使用sqlite数据则需要安装
```shell script
yum -y install sqlite sqlite-devel
```

###### 安装NPM、Python3、Nginx
 ```shell script
yum -y install epel-release
yum -y install python3-devel python3 python3-pip python3-setuptools python3-libs npm nginx
```

###### 获取源码
```shell script
git clone https://github.com/xiaoxin1992/bind-pod.git
cd bind-pod
```

###### 安装Python依赖
```shell script
pip3 install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
```

###### 配置数据数据库和dns配置   config/bindpod.json
修改服务配置文件
```json5
{
  "dns": {
    "server": "127.0.0.1",    //  dns服务器地址，rndc配置可以通过named控制允许访问的IP地址
    "port": 53,               // dns端口
    "key": "bindpod",         // rndc 的key
    "secret": "HykrxxHfxz2SuFHC7wfSFg=="  // rndc 的密钥
  },
  //  数据库配置
  "database": {
    "sqlite": {
      "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "./db.sqlite3"
      }
    },
    "mysql": {
      "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "mysql_database",
        "USER": "USER",
        "PASSWORD": "PASSWORD",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
          "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
        }
      }
    },
    "select": "sqlite"   // 选择使用的数据库默认sqlite
  }
}
```
完成后重启BindPod服务

###### 执行migrate生成数据库表和基础数据
```shell script
python3 manage.py makemigrations
python3 manage.py migrate
```
###### 创建超级管理员用户(根据命令行提示创建超级管理员)
```shell script
python3 manage.py createsuperuser
```

###### 手动启动
```shell script
python3 manage.py runserver 0.0.0.0:8080
```

###### 使用UWSGI方式启动
```shell script
uwsgi  --ini uwsgi.ini
```

###### 配置文件
```ini
[uwsgi]
chdir=/srv/BindPod          #  根据自己的项目路径填写
home = /usr                 #   Python安装路径 例如: /srv/python3
pythonpath=/srv/BindPod     #  根据自己的项目路径填写
http=0.0.0.0:8080
master=true
processes=4
threads=2
uid=root
gid=root
thunder-lock=true
enable-threads=true
module=BindPod.wsgi
socket=BindPod.sock
pidfile=BindPod.pid
chmod-socket = 666
vacuum = true
die-on-term = true
```

###### 前端
前端页面地址: https://github.com/xiaoxin1992/bindpod-web

###### API接口
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
is_staff            表示用户是否是超级管理员
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

配置完成重启named服务



