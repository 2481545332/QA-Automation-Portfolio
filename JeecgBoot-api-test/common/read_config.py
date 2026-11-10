# 导入需要的包
import os
import yaml
from common.logger import logger


class ReadConfig:
    """读取yaml配置文件工具类"""
    def __init__(self):
    #     # __file__：当前read_config.py这个文件的绝对路径
    #     current_file_path = __file__
    #     # os.path.dirname()：获取当前文件所在目录 → common文件夹
    #     current_dir = os.path.dirname(current_file_path)
    #     # os.path.dirname()再套一层 → 项目根目录
    #     project_root = os.path.dirname(current_dir)
    #     # 拼接配置文件完整路径：项目根目录 + config + config.yaml
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.config_file_path = os.path.join(project_root, "config", "config.yaml")

        # 加载yaml里面全部内容，存到self.config_data
        self.config_data = self.load_yaml()

    def load_yaml(self):
        """加载并解析yaml文件"""
        try:
            # open：打开文件；r=只读；encoding="utf-8" 防止中文乱码
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                # yaml.safe_load：安全解析yaml，不执行yaml里危险代码，比普通load安全
                data = yaml.safe_load(f)
                logger.info("配置文件读取成功")
                return data
        except Exception as err:
            logger.error(f"读取配置文件失败：{err}")
            # 抛出异常，脚本直接终止，不会带着错误配置继续跑用例
            raise err

    def get_env(self):
        """获取当前激活环境，比如 test"""
        return self.config_data.get("env")

    def get_base_url(self):
        """获取后端接口基础地址"""
        env = self.get_env()
        return self.config_data.get(env).get("base_url")

    def get_user_info(self):
        """返回账号、密码"""
        env = self.get_env()
        user_info = self.config_data.get(env)
        return {
            "username": user_info.get("username"),
            "password": user_info.get("password")
        }

    def get_mysql_info(self):
        """返回mysql连接信息字典"""
        env = self.get_env()
        mysql_info = self.config_data.get(env).get("mysql")
        return mysql_info

    def get_depart_id(self):
        """返回部门角色用例使用的部门id（对应 sys_depart.id）"""
        env = self.get_env()
        return self.config_data.get(env).get("depart_id")


# 实例化一次，全局共用这一个读取对象，其他文件直接导入使用
read_config = ReadConfig()