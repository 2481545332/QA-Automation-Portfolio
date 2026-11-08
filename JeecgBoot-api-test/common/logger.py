from loguru import logger
import os
import sys

# 日志文件夹
log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(log_path):
    os.mkdir(log_path)

# 日志文件名
log_file = os.path.join(log_path, "run.log")


def console_sink(message):
    """
    控制台输出兜底：
    Windows 控制台默认 GBK 编码，日志里带 emoji / 特殊字符时直接 print 会抛
    UnicodeEncodeError，loguru 会报 "Logging error"，并让 pytest 退出码变成 1。
    这里按当前输出流真实编码做一次容错替换，保证「日志打不出来」不会影响用例结果。
    """
    stream = sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    stream.write(message.encode(encoding, errors="replace").decode(encoding))
    stream.flush()


# 移除默认handler，重新添加：控制台 + 文件
logger.remove()
logger.add(
    sink=log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    encoding="utf-8",
    rotation="500 KB",   # 文件超过500k自动切割
    retention="7 days",  # 保留7天日志
    level="INFO"
)
# 控制台输出
logger.add(
    sink=console_sink,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)