# common/read_yaml.py
import os
import yaml
from common.logger import logger

class ReadYaml:
    def __init__(self, file_name):
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(__file__))
        # 拼接出 YAML 文件的绝对路径（存放在 data 目录下）
        self.file_path = os.path.join(project_root, "data", file_name)

    def get_data(self):
        """读取 YAML 数据，返回列表嵌套字典的格式"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                # safe_load 是最安全的加载方式
                data = yaml.safe_load(f)
                logger.info(f"读取 YAML 文件成功: {self.file_path}，共 {len(data)} 条用例")
                return data
        except Exception as e:
            logger.error(f"读取 YAML 文件失败，请检查路径或语法: {e}")
            raise e