from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.logger import logger
import allure


class BasePage:
    # 定义一个接收方法
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    # 元素定位
    def find(self, locator):
        logger.info(f"定位元素: {locator}")
        # 只要元素存在于 DOM 树中即可，不强制要求立刻可见（解决下拉框超时）
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    # 点击
    def click(self, locator):
        logger.info(f"点击元素: {locator}")
        self.find(locator).click()

    # 输入文本
    def input_text(self, locator, text):
        logger.info(f"输入文本: {text}")
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    # 获取返回文本
    def get_text(self, locator):
        return self.find(locator).text

    # 截图方法
    def take_screenshot(self, file_name):
        self.driver.save_screenshot(file_name)
        with open(file_name, "rb") as f:
            allure.attach(f.read(), name=file_name, attachment_type=allure.attachment_type.PNG)