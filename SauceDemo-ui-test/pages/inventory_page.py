from selenium.webdriver.common.by import By
from base.base_page import BasePage
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.logger import logger


class InventoryPage(BasePage):
    # 购物车定位元素声明
    page_title = (By.CLASS_NAME, "title")
    sort_dropdown = (By.CSS_SELECTOR, "select.product_sort_container")
    add_backpack_btn = (By.ID, "add-to-cart-sauce-labs-backpack")
    add_bike_light_btn = (By.ID, "add-to-cart-sauce-labs-bike-light")
    cart_badge = (By.CLASS_NAME, "shopping_cart_badge")
    cart_link = (By.CLASS_NAME, "shopping_cart_link")
    remove_backpack_btn = (By.ID, "remove-sauce-labs-backpack")
    remove_bike_light_btn = (By.ID, "remove-sauce-labs-bike-light")

    # 获取页面标题
    def get_title(self):
        return self.get_text(self.page_title)

    # 在商品列表页的下拉框中，选择 “Price (low to high)”，实现按价格升序排列。
    def sort_by_price_low_to_high(self):
        logger.info("正在等待排序下拉框加载...")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self.sort_dropdown)
        )
        Select(self.find(self.sort_dropdown)).select_by_value("lohi")
        logger.info("排序操作执行完毕")

    # 抓取页面上所有商品的价格，并返回一个包含浮点数的列表（如 [29.99, 9.99, 15.99, ...]）。
    def get_product_prices(self):
        price_elements = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        prices = [float(el.text.replace("$", "")) for el in price_elements]
        return prices
    # 防状态污染：检查购物车里有没有背包和自行车灯，如果有，就点击“Remove”按钮把它们删掉
    def clear_cart(self):
        try:
            removes = self.driver.find_elements(*self.remove_backpack_btn)
            if removes:
                removes[0].click()
            removes_light = self.driver.find_elements(*self.remove_bike_light_btn)
            if removes_light:
                removes_light[0].click()
        except Exception:
            pass
    # 加入背包
    def add_backpack(self):
        self.clear_cart()
        self.click(self.add_backpack_btn)
    # 加入自行车灯
    def add_bike_light(self):
        self.clear_cart()
        self.click(self.add_bike_light_btn)
    # 获取右上角购物车图标上的数字角标
    def get_cart_count(self):
        return self.get_text(self.cart_badge)
    # 点击右上角的购物车图标，跳转到购物车详情页。
    def go_to_cart(self):
        self.click(self.cart_link)