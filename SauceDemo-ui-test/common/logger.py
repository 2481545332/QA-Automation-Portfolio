from loguru import logger
import os
import sys

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 解决 Windows 控制台乱码问题
def console_sink(message):
    stream = sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    stream.write(message.encode(encoding, errors="replace").decode(encoding))
    stream.flush()

logger.remove()
# 控制台输出
logger.add(console_sink, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
# 文件输出
logger.add(os.path.join(log_dir, "ui_test.log"), rotation="10 MB", level="INFO", encoding="utf-8")