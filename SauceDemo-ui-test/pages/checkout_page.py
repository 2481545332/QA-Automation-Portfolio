from selenium.webdriver.common.by import By
from base.base_page import BasePage


class CheckoutPage(BasePage):
    first_name = (By.ID, "first-name")
    last_name = (By.ID, "last-name")
    zip_code = (By.ID, "postal-code")
    continue_btn = (By.ID, "continue")
    error_msg = (By.CSS_SELECTOR, "[data-test='error']")
    finish_btn = (By.ID, "finish")
    complete_header = (By.CLASS_NAME, "complete-header")

    def fill_info(self, fname, lname, zipcode):
        self.input_text(self.first_name, fname)
        self.input_text(self.last_name, lname)
        self.input_text(self.zip_code, zipcode)
        self.click(self.continue_btn)

    def get_error_text(self):
        return self.get_text(self.error_msg)

    def click_finish(self):
        self.click(self.finish_btn)

    def get_success_msg(self):
        return self.get_text(self.complete_header)