import allure
import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from common.read_excel import read_excel

checkout_data = read_excel("checkout")


@allure.feature("结算模块")
class TestCheckout:

    @allure.story("结算异常信息校验")
    @pytest.mark.parametrize("case", checkout_data, ids=[f"err_{c[0]}" for c in checkout_data])
    def test_01_checkout_errors(self, logged_in_driver, case):
        # 1. 前置：加购并进入结算页
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        InventoryPage(logged_in_driver).add_backpack()
        InventoryPage(logged_in_driver).go_to_cart()
        CartPage(logged_in_driver).click_checkout()

        # 2. 填写错误信息
        checkout_page = CheckoutPage(logged_in_driver)
        checkout_page.fill_info(case[1], case[2], case[3])

        with allure.step("断言报错"):
            assert case[4] in checkout_page.get_error_text()

    @allure.story("结算成功流程")
    def test_02_checkout_success(self, logged_in_driver):
        # 1. 前置：加购并进入结算页
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        InventoryPage(logged_in_driver).add_backpack()
        InventoryPage(logged_in_driver).go_to_cart()
        CartPage(logged_in_driver).click_checkout()

        # 2. 填写正确信息
        checkout_page = CheckoutPage(logged_in_driver)
        checkout_page.fill_info("John", "Doe", "123456")
        checkout_page.click_finish()

        with allure.step("断言订单成功提示"):
            assert checkout_page.get_success_msg() == "Thank you for your order!"