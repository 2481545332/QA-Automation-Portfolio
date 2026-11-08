import yaml
import os

class ReadConfig:
    def __init__(self):
        # 获取项目根目录
        self.root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.root_path, "config", "config.yaml")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get(self, key):
        return self.data.get(key)

config = ReadConfig()