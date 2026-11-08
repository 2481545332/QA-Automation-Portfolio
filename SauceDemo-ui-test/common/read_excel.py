from openpyxl import load_workbook
import os


def read_excel(sheet_name):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_path, "data", "test_data.xlsx")
    wb = load_workbook(file_path)
    ws = wb[sheet_name]

    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row): continue
        # 将 None 转换为空字符串 ""
        clean_row = [str(cell) if cell is not None else "" for cell in row]
        data.append(clean_row)
    return data