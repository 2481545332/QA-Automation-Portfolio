from openpyxl import Workbook
import os


def generate():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_path, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    wb = Workbook()

    # Sheet1: 登录异常数据
    ws1 = wb.active
    ws1.title = "login"
    ws1.append(["case_id", "username", "password", "expected_error"])
    ws1.append([1, "locked_out_user", "secret_sauce", "Sorry, this user has been locked out"])
    ws1.append([2, "standard_user", "wrong_pwd", "Username and password do not match"])
    ws1.append([3, "", "secret_sauce", "Username is required"])
    ws1.append([4, "standard_user", "", "Password is required"])
    ws1.append([5, "invalid_user", "secret_sauce", "Username and password do not match"])

    # Sheet2: 结算信息数据
    ws2 = wb.create_sheet("checkout")
    ws2.append(["case_id", "first_name", "last_name", "zip_code", "expected_error"])
    ws2.append([1, "", "Doe", "12345", "Error: First Name is required"])
    ws2.append([2, "John", "", "12345", "Error: Last Name is required"])
    ws2.append([3, "John", "Doe", "", "Error: Postal Code is required"])

    save_path = os.path.join(data_dir, "test_data.xlsx")
    wb.save(save_path)
    print(f"✅ Excel 数据文件已生成: {save_path}")


if __name__ == "__main__":
    generate()