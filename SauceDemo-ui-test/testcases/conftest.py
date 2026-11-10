import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from base.base_page import BasePage
from config.read_config import config
from pages.login_page import LoginPage

# 全局浏览器驱动
@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

# 登录驱动
@pytest.fixture(scope="session")
def logged_in_driver(driver):
    """Session级登录前置，只登录一次，提升执行效率"""
    driver.get(config.get("base_url"))
    LoginPage(driver).login(config.get("standard_user"), config.get("password"))
    return driver

# 失败自动截图钩子
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            BasePage(driver).take_screenshot(f"screenshots/FAIL_{item.name}.png")