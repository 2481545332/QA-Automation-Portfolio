import allure
import uuid
import pytest
from common.read_excel import ReadExcel
from common.path import EXCEL_PATH
from common.captcha_helper import get_real_captcha,build_captcha
from common.logger import logger

# 实例化读取excel对象,获取全部测试数据
excel = ReadExcel(EXCEL_PATH,"login").get_data()

@allure.feature("登录模块")
@allure.story("账号密码登录-数据驱动")
@pytest.mark.parametrize("case", excel,ids=lambda x:x["case_id"])
def test_login_data_drive(http_util,ocr,case):
    """
    数据驱动登录接口
    :param case_id: 用例编号
    :param case_title: 用例标题
    :param username: 账号
    :param password: 密码
    :param checkKey_flag: right/wrong 验证码key类型标记
    :param captcha_flag: right/wrong/empty 验证码类型标记
    :param expect_success: 预期success布尔值
    :param expect_msg: 预期提示信息
    """
    case_id = case["case_id"]
    case_title = case["case_title"]
    username = case["username"]
    password = case["password"]
    expect_success = case["expect_success"]
    expect_msg = case["expect_msg"]
    captcha_flag = case["captcha_flag"]
    checkKey_flag = case["checkKey_flag"]

    allure.dynamic.title(f"{case_id} - {case_title}")
    # 1.生成checkKey
    check_key = str(uuid.uuid4())
    logger.info(f"【用例{case_id}】checkKey：{check_key}")

    # 2.请求验证码接口
    resp_captcha = get_real_captcha(http_util,check_key,ocr)
    # 根据标记，决定传给接口的验证码是什么
    send_captcha = build_captcha( resp_captcha, captcha_flag)
    logger.info(f"【用例{case_id}】识别验证码：{resp_captcha}实际传入{send_captcha}")
    #模拟过期
    final_check_key = check_key
    if checkKey_flag == "expired":
        # 如果是测试过期，我们把传给登录接口的 key 变成无效的
        final_check_key = "expired_fake_key_123456789"
    # 3.组装登录请求体
    login_json = {
        "username": username,
        "password": password,
        "captcha": send_captcha,
        "checkKey": final_check_key
    }
    resp_login = http_util.send(path="/sys/login", method="POST", json=login_json, timeout=20)
    logger.info(f"【用例{case_id}】登录返回：{resp_login}")

    # 4.断言（修复None报错版本）
    assert resp_login["success"] == expect_success, f"用例{case_id} 业务状态不符"
    assert resp_login["message"] == expect_msg, f"用例{case_id} 提示文案不符"

    if expect_success:
        # 成功：先判断result存在且是字典
        assert "result" in resp_login, "登录成功返回缺少result字段"
        assert isinstance(resp_login["result"], dict), "登录成功result必须是字典"
        assert "token" in resp_login["result"], "登录成功必须返回token"
    else:
        # 失败：只有result存在并且不为None，才校验token
        if "result" in resp_login and resp_login["result"] is not None:
            assert isinstance(resp_login["result"], dict), "返回result类型异常"
            assert "token" not in resp_login["result"], "登录失败不应该返回token"