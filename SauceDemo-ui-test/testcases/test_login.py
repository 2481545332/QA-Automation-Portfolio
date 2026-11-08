import pytest
import allure
from pages.login_page import LoginPage
from common.read_excel import read_excel
from config.read_config import config
# 读取数据
login_data = read_excel("login")

@allure.feature("登录模块")
class TestLogin:
    @allure.story("数据驱动异常登录")
    @pytest.mark.parametrize("case", login_data, ids=[f"case_{c[0]}" for c in login_data])
    def test_login_fail(self, driver, case):
        allure.dynamic.title(f"登录测试 - {case[3]}")
        login_page = LoginPage(driver)
        login_page.open(config.get("base_url"))

        login_page.login(case[1], case[2])
        with allure.step("断言错误提示"):
            assert case[3] in login_page.get_error_text()