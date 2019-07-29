<h1 align = "center">Bind-DLZ + Django   + Mysql  DNS管理平台 </h1>
系统环境:CentOS 7.6 X64

软件版本: 

      bind-9.11.6.tar.gz  
      mysql-5.6.16.tar.gz
	  Python 3.6 
	  Django 1.11.x

<h2 align = "center">一．源码安装配置Bind: </h2>

    yum -y install make gcc-c++ cmake bison-devel  ncurses-devel python-devel python-ply bind-utils
    ./configure --prefix=/usr/local/bind/ \
    --with-dlz-mysql=/usr/local/mysql \
    --enable-threads=no --enable-largefile \
    --disable-ipv6 --with-openssl=no
    make && make install

1.用户添加授权目录

     mkdir -p /usr/local/bind/var/{logs,zones}
     cd /usr/local/bind/etc/
     /usr/local/bind/sbin/rndc-confgen > rndc.conf
     tail -10 rndc.conf | head -9 | sed s/#\ //g > named.conf
	 useradd  -s  /sbin/nologin  named
	 chown  -R named:named /usr/local/bind/        
2.配置Bind
##### # 配置主服务器 

    vim /usr/local/bind/etc/named.conf # 主
    key "rndc-key" {
       algorithm hmac-md5;
       secret "mvCUyhyDvNNGywhoVHbSaQ==";
    };
    
    # 声明控制通道，用于rndc程序
    controls {
       inet 127.0.0.1 port 953 
                     allow { 127.0.0.1; } keys { "rndc-key"; };
    };
    
    acl trust-lan {
            172.0.0.0/8;
    };
    
    # 通信通道，以访问named统计信息
    statistics-channels {
        inet 127.0.0.1 port 8653 allow { 127.0.0.1; };
    };
    
    options {
        listen-on port 53 {any;};         # 开启侦听53端口，any表示接受任意ip连接
        zone-statistics yes;
        tcp-clients 50000;
        dnssec-enable no;
        dnssec-validation no;
        datasize unlimited;
        stacksize unlimited;
        directory "/usr/local/bind/var";
        pid-file "named.pid";               # named进程的pid
        dump-file "bind_dump.db";     # 服务器在收到rndc dump命令时，转储数据到文件的路径
        statistics-file "/usr/local/bind/var/bind.stats";   
        allow-query{ trust-lan; };        # 允许trust-lan ip查询 
        allow-transfer { 172.20.10.61;   #允许哪些主机从服务器接受传送
                        172.20.10.62; };
        notify yes;                                 # 允许通知同步
        also-notify { 172.20.10.61;        # 允许通知本服务器
                     172.20.10.62; };
        allow-recursion { trust-lan; };      # 允许哪些主机可以通过本服务器进行递归查询
        recursive-clients 35000;
        forwarders{ 114.114.114.114;
                 223.5.5.5;
                 223.6.6.6; 
                 8.8.8.8; };      # 设置转发的公网ip
    };

    # 指定服务器记录哪些日志，和在哪里记录日志消息
    logging {
        channel bind_log {
            file "/usr/local/bind/var/logs/bind.log" versions 3 size 100m;
            severity debug;
            print-time yes;
            print-severity yes;
            print-category yes;
        };

        channel error_log {
            file "/usr/local/bind/var/logs/error.log" versions 10 size 32m;
            severity info;
            print-time yes;
            print-severity yes;
            print-category yes;
        };
    
        channel query_log {
            file "/usr/local/bind/var/logs/query.log" versions 10 size 32m;
            severity info;
            print-time yes;
            print-severity yes;
            print-category yes;
        };
    
        category default { bind_log; };
    
        category queries { query_log; };
    };
    
    dlz "Mysql zone" {
       database "mysql
       {dbname=db_ops port=3306 host=172.28.10.60 user=op_oss pass=JqIrsM1hVvo8 ssl=false}
       {select zone from t_dns_records where zone = '$zone$' and status = 1}
       {select ttl, type, mx_priority, case when lower(type)='txt' then concat('\"', data, '\"')
            when lower(type) = 'soa' then concat_ws(' ', data, resp_person, serial, refresh, retry, expire, minimum)
            else data end from t_dns_records where zone = '$zone$' and host = '$record$' and status = 1}
       {}
       {select ttl, type, host, mx_priority, case when lower(type)='txt' then
            concat('\"', data, '\"') else data end, resp_person, serial, refresh, retry, expire,
            minimum from t_dns_records where zone = '$zone$' and status = 1}
       {select zone from t_dns_xfr_table where zone = '$zone$' and client = '$client$' and status = 1}";
    };
   
##### # 配置从服务器   
    
    vim /usr/local/bind/etc/named.conf # 从
    key "rndc-key" {
       algorithm hmac-md5;
       secret "mvCUyhyDvNNGywhoVHbSaQ==";
    };
    
    controls {
       inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { "rndc-key"; };
    };
    
    acl trust-lan {
            172.0.0.0/8;
    };
    
    options {
        listen-on port 53 {any;};
        zone-statistics yes;
        tcp-clients 50000;
        dnssec-enable no;
        dnssec-validation no;
        datasize unlimited;
            stacksize unlimited;
            directory "/usr/local/bind/var";
            pid-file "/usr/local/bind/var/bind.pid";
            dump-file "/usr/local/bind/var/bind_dump.db";
            statistics-file "/usr/local/bind/var/bind.stats";
        allow-query{ trust-lan; };
        allow-transfer { 172.20.10.61; };
        notify yes;
        also-notify { 172.20.10.61; };
        recursion yes;
        allow-recursion { trust-lan; };
        recursive-clients 35000;
        forwarders { 114.114.114.114;
            8.8.8.8; };
    };
    
    
    logging {
        channel bind_log {
            file "/usr/local/bind/var/logs/bind.log" versions 3 size 100m;
            severity debug;
            print-time yes;
            print-severity yes;
            print-category yes;
        };
    
        channel error_log {
            file "/usr/local/bind/var/logs/error.log" versions 10 size 32m;
            severity info;
            print-time yes;
            print-severity yes;
            print-category yes;
        };
    
        channel query_log {
            file "/usr/local/bind/var/logs/query.log" versions 10 size 32m;
            severity info;
            print-time yes;
            print-severity yes;
            print-category yes;
        };
    
        category default { bind_log; };
    
        category queries { query_log; };
    };
    
    zone "baidu.com" IN {
        type slave;
            file "zones/baidu.com.zone";
            masterfile-format text;
            masters{ 172.20.10.60; };
    };
    
##### # 启动脚本
    vim /etc/systemd/system/named.service
    [Unit]
    Description=Internet domain name server
    After=network.target
    
    [Service]
    ExecStart=/usr/local/bind/sbin/named -f -u named -4
    ExecReload=/usr/local/bind/sbin/rndc reload
    ExecStop=/usr/local/bind/sbin/rndc stop
    
    [Install]
    WantedBy=multi-user.target
    Alias=bind.service
    
##### # 启动命令    
    systemctl daemon-reload
    systemctl start named.service
    
<h2 align = "center">二．配置Bind-Web 管理平台 </h2>

1.获取代码 
  
    git  clone  https://github.com/ymx8383521/Bind-Web.git  #git  克隆下来
    cd Bind-Web
    pip install -r  requirement.txt
 
2.数据库配置
 
        1.)   CREATE DATABASE db_ops CHARACTER SET utf8 COLLATE utf8_general_ci;  #创建数据库
	      grant all privileges on db_ops.* to op_oss@'%' identified by 'JqIrsM1hVvo8'
		
        2.)配置文件devops/settings 里连接数据库
		
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.mysql',
                        'NAME':'db_ops',
                        'USER': 'op_oss',
                        'PASSWORD': 'JqIrsM1hVvo8',
                        'HOST': '127.0.0.1',
                        'PORT':'3306',
                    }
                }
				
        3.)表结构刷到数据库
                python  manage.py makemigrations 
                python  manage.py migrate
                python manage.py  createsuperuser
				 
	    4.)运行项目
                python manage.py  runserver 0.0.0.0:8001
	
        5.)访问WEB 界面 登录账户就是创建的管理用户
                http://ip/8001

<h2 align = "center">三. 针对已有数据库的操作</h2>
##### # 把新生成的models.py放到app目录下

    python manage.py inspectdb > models.py  #需要修改managed = True  
    python manage.py migrate
    
##### # 数据库构   

    create table `t_dns_records` (
      `id` bigint(20) not null auto_increment comment '主健',
      `zone` varchar(255) not null default '' comment '域名',
      `host` varchar(255) not null default '' comment '记录名称',
      `type` varchar(255) not null default '' comment '记录类型',
      `data` varchar(255) not null default '' comment '记录值',
      `ttl` int(11) default null comment 'ttl(存活时间)',
      `mx_priority` int(11) default null comment 'mx优先级',
      `refresh` int(11) default null comment '刷新时间间隔',
      `retry` int(11)  default null comment '重试时间间隔',
      `expire` int(11) default null comment '过期时间',
      `minimum` int(11) default null comment '最小时间',
      `serial` bigint(20) default null comment '序列号,每次更改配置都会在原来的基础上加1',
      `resp_person` varchar(64) default null comment '责任人',
      `primary_ns` varchar(64) default null comment '主域名',
      `status` tinyint(4) default 1 comment '0:该记录无效, 1:该记录有效',
      `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
      primary key (`id`),
      key `ix_zone` (`zone`),
      key `ix_host` (`host`),
      key `ix_data` (`data`),
      key `ix_type` (`type`),
      key `ix_status` (`status`),
      key `ix_created_at` (`created_at`),
      key `ix_updated_at` (`updated_at`)
    ) engine=InnoDB default charset=utf8 comment='DNS解析记录';
    
    create table `t_dns_xfr_table` (
      `id` bigint(20) not null auto_increment comment '主健',
      `zone` varchar(255) not null default '' comment '域名',
      `client` varchar(255) not null default '' comment 'BIND SLAVE 客户端',
      `status` tinyint(4) default 1 comment '0:该记录无效, 1:该记录有效',
      `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
      primary key (`id`),
      key `ix_created_at` (`created_at`),
      key `ix_updated_at` (`updated_at`)
    ) engine=InnoDB default charset=utf8 comment='DNS授权传送信息';

<h2 align = "center">四．Bind-Web使用 </h2>
参考：http://wiki.vknow.com/display/yunwei/bind
1. slave配置zone


    zone "php.com." in {  
        type slave;  
        file "zones/php.com";  
        masterfile-format text;  
        masters{ 172.28.10.60; };  
    };  
    
2. Bind-Web平台上操作，首先要创建SOA记录和NS记录


    select * from t_dns_records limit 3;  
    +----+-----------+------+------+------------- -+-----+-------------+---------+-------+--------+---------+------------+-------------+------------+--------+---------------------+---------------------+
    | id | zone      | host | type | data          | ttl | mx_priority | refresh | retry | expire | minimum | serial     | resp_person | primary_ns | status | created_at          | updated_at          |
    +----+-----------+------+------+---------------+-----+-------------+---------+-------+--------+---------+------------+-------------+------------+--------+---------------------+---------------------+
    |  1 | baidu.com | @    | NS   | ns.baidu.com. |  60 |        NULL |    NULL |  NULL |   NULL |    NULL |       NULL | NULL        | NULL       |      1 | 2019-07-01 11:02:14 | 2019-07-11 19:10:54 |
    |  2 | baidu.com | @    | SOA  | ns            |  60 |        NULL |     300 |  3000 |  86400 |   86400 | 1562898308 | admin       | NULL       |      1 | 2019-07-01 11:02:28 | 2019-07-12 10:25:12 |
    |  3 | baidu.com | xxxx | A    | 172.20.10.72  |  60 |        NULL |    NULL |  NULL |   NULL |    NULL |       NULL | NULL        | NULL       |      1 | 2019-07-01 11:05:44 | 2019-07-11 19:10:54 |
    +----+-------- --+------+------+---------------+-----+-------------+---------+-------+--------+---------+------------+-------------+------------+--------+---------------------+---------------------+
    
    select * from t_dns_xfr_table limit 1;  
    +----+-----------+--------------+--------+---------------------+---------------------+  
    | id | zone      | client       | status | created_at          | updated_at          |  
    +----+-----------+--------------+--------+---------------------+---------------------+  
    |  1 | baidu.com | 172.20.10.61 |      1 | 2019-07-01 11:01:46 | 2019-07-01 11:01:46 |  
    +----+-----------+--------------+--------+---------------------+---------------------+    
