from selenium.webdriver.common.by import By
from base.base_page import BasePage

class LoginPage(BasePage):
    # 定位元素声明
    user_input = (By.CSS_SELECTOR, "[data-test='username']")
    pwd_input = (By.CSS_SELECTOR, "[data-test='password']")
    login_btn = (By.CSS_SELECTOR, "[data-test='login-button']")
    error_msg = (By.CSS_SELECTOR, "[data-test='error']")

    # 打开网站
    def open(self, url):
        self.driver.get(url)

    # 登录方法
    def login(self, username, password):
        self.input_text(self.user_input, username)
        self.input_text(self.pwd_input, password)
        self.click(self.login_btn)

    # 获取错误返回文本用于断言
    def get_error_text(self):
        return self.get_text(self.error_msg)