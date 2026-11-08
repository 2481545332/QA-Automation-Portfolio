import requests
from common.read_config import read_config
from common.logger import logger

class RequestUtil:
    def __init__(self):
        """初始化，拿到基础地址，初始化session、基础请求头"""
        # 从配置文件读取后端基础url，不用硬编码
        self.base_url = read_config.get_base_url()
        # requests.Session()：会话对象，自动维持cookie，复用连接池，提升请求效率
        self.session = requests.Session()
        # 基础header：默认json格式，Jeecg大部分接口是json入参
        self.headers = {
            "Content-Type": "application/json"
        }

    def set_token(self, token: str):
        """
        外部调用这个方法，往header里面加入token
        :param token: 登录接口返回的token字符串
        """
        # JeecgBoot 鉴权头固定是 X-Access-Token
        self.headers["X-Access-Token"] = token
        logger.info(f"token已设置：{token[:20]}******")

    def clear_token(self):
        """清除token，登出、用例结束时调用"""
        if "X-Access-Token" in self.headers:
            self.headers.pop("X-Access-Token")
            logger.info("token已清除")

    def send(self, path, method="GET", json=None, params=None, data=None, return_raw=False,timeout=20):
        """
        统一发送请求的核心方法，get/post/put/delete都走这一个
        :param path: 接口路径，比如 /sys/login
        :param method: 请求方式，默认GET
        :param json: json格式请求体
        :param params: url查询参数（?xxx=xxx）
        :param data: form表单参数
        :param return_raw: False 默认解析返回json；True 返回原始response对象（验证码图片/文件下载接口使用）
        """
        # 拼接完整url：基础地址 + 接口路径
        url = self.base_url + path
        logger.info(f"=====发起请求=====")
        logger.info(f"请求地址：{url}")
        logger.info(f"请求方式：{method.upper()}")
        logger.info(f"请求头：{self.headers}")
        logger.info(f"json入参：{json}")
        logger.info(f"params参数：{params}")

        try:
            # session发起请求
            resp = self.session.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                json=json,
                params=params,
                data=data,
                timeout=timeout # 超时时间10秒，防止接口卡死一直等待
            )
            logger.info(f"响应状态码：{resp.status_code}")
            logger.info(f"响应原文：{resp.text}")

            # ==========新增分支==========
            if return_raw:
                # 返回原始response，给图片、文件流接口使用，不解析json
                return resp
            else:
                # 原有逻辑：统一返回json，Jeecg后端大部分接口统一返回json格式
                return resp.json()

        except requests.exceptions.Timeout:
            logger.error("请求超时！后端响应过慢")
            raise
        except Exception as e:
            logger.error(f"请求发生异常：{str(e)}")
            raise