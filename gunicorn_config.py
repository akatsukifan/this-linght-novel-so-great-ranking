import multiprocessing

import multiprocessing

# 绑定的地址和端口
bind = "0.0.0.0:8000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作线程数
threads = 2

# 工作进程类型
worker_class = "sync"

# 访问日志格式
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 错误日志格式
errorlog = "-"
loglevel = "info"

# 超时时间
timeout = 30

# 最大并发数
keepalive = 2