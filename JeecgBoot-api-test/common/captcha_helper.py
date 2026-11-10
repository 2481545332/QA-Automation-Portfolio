import base64
from common.logger import logger
#发送验证码请求
def get_real_captcha(http_util,check_key,ocr,timeout=20):
    """
    请求验证码图片并用 OCR 识别，返回真实验证码文本。

    :param http_util: 你end 方法）
    :param check_key: uuid 生成的 checkKey的请求工具实例（s
    :param ocr:       已实例化的 DdddOcr 对象
    :return: 识别出的验证码字符串
    """
    resp = http_util.send(
        path=f"/sys/randomImage/{check_key}",method="GET",timeout=timeout
    )
    # 接口返回形如 "data:image/png;base64,xxxxxx"，取逗号后面部分
    img_base64 = resp["result"].split(",")[1]
    # 把 base64 文本还原成原始二进制字节
    img_bytes = base64.b64decode(img_base64)
    # ocr.classification(img_bytes)：ddddocr 的核心方法，输入图片字节，输出识别出的文字（如 "3a8f"）；
    return ocr.classification(img_bytes)

# 判断验证码的类型（正确，错误，传空）
def build_captcha(real_captcha,captcha_flag):
    """
    根据 Excel 里的标记，决定真正传给登录接口的验证码。

    :param real_captcha: OCR 识别出的真实验证码
    :param captcha_flag: "right" / "wrong" / "empty" / 其它
    :return: 实际要传给接口的验证码
    """
    if captcha_flag == "wrong":
        return real_captcha + "1"
    if captcha_flag == "empty":
        return ""
    # "right" 以及未知标记都按真实验证码处理
    return real_captcha

# 整合函数方法，直接识别并传入
def get_captcha_by_flag(http_util, ocr, captcha_flag, check_key=None):
    import uuid
    check_key = check_key or str(uuid.uuid4())
    real = get_real_captcha(http_util,check_key,ocr)
    send = build_captcha(real,captcha_flag)
    logger.info(f"checkKey={check_key} 识别={real} 实际传入={send!r}")
    return send, real, check_key