import allure
from pages.inventory_page import InventoryPage


@allure.feature("商品模块")
class TestInventory:

    @allure.story("商品列表展示与加购")
    def test_01_check_page_title(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        page = InventoryPage(logged_in_driver)
        assert page.get_title() == "Products"

    @allure.story("商品列表展示与加购")
    def test_02_sort_price(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")

        page = InventoryPage(logged_in_driver)

        with allure.step("1. 执行价格从低到高排序"):
            page.sort_by_price_low_to_high()

        with allure.step("2. 获取排序后的商品价格列表"):
            prices = page.get_product_prices()
            allure.attach(str(prices), name="当前页面价格列表", attachment_type=allure.attachment_type.TEXT)

        with allure.step("3. 断言：价格列表是否真正实现了升序排列"):
            assert len(prices) > 0, "页面上未抓取到任何商品价格"
            assert prices == sorted(prices), f"排序失败！当前价格为: {prices}"

    @allure.story("商品列表展示与加购")
    def test_03_add_backpack(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        page = InventoryPage(logged_in_driver)
        page.add_backpack()
        assert page.get_cart_count() == "1"

    @allure.story("商品列表展示与加购")
    def test_04_add_bike_light(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        page = InventoryPage(logged_in_driver)
        page.add_bike_light()
        assert int(page.get_cart_count()) >= 1

    @allure.story("商品列表展示与加购")
    def test_05_cart_icon_click(self, logged_in_driver):
        logged_in_driver.get("https://www.saucedemo.com/inventory.html")
        page = InventoryPage(logged_in_driver)
        page.go_to_cart()
        assert "cart" in logged_in_driver.current_url