import allure
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@allure.feature("购物车模块")
class TestCart:
    def setup_method(self):
        # 购物车用例的前置：必须加购一件商品
        pass

    @allure.story("购物车管理")
    def test_01_cart_item_name(self, logged_in_driver):
        # 前置造数：加购背包
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        InventoryPage(logged_in_driver).add_backpack()

        InventoryPage(logged_in_driver).go_to_cart()
        cart_page = CartPage(logged_in_driver)
        assert "Sauce Labs Backpack" in cart_page.get_item_name()

    @allure.story("购物车管理")
    def test_02_continue_shopping(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/cart.html")
        cart_page = CartPage(logged_in_driver)
        cart_page.click_continue_shopping()
        assert "inventory.html" in logged_in_driver.current_url

    @allure.story("购物车管理")
    def test_03_checkout_entry(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/cart.html")
        cart_page = CartPage(logged_in_driver)
        cart_page.click_checkout()
        assert "checkout-step-one" in logged_in_driver.current_url

    @allure.story("购物车管理")
    def test_04_cart_empty_check(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/cart.html")
        assert "cart" in logged_in_driver.current_url

    @allure.story("购物车管理")
    def test_05_cart_ui_element(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/cart.html")
        cart_page = CartPage(logged_in_driver)
        assert cart_page.find(cart_page.checkout_btn).is_displayed()