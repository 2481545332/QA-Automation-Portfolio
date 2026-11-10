from selenium.webdriver.common.by import By
from base.base_page import BasePage


class CartPage(BasePage):
    item_name = (By.CLASS_NAME, "inventory_item_name")
    checkout_btn = (By.ID, "checkout")
    continue_shopping_btn = (By.ID, "continue-shopping")

    def get_item_name(self):
        return self.get_text(self.item_name)

    def click_checkout(self):
        self.click(self.checkout_btn)

    def click_continue_shopping(self):
        self.click(self.continue_shopping_btn)