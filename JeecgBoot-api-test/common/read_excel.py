# ============================================================
# 导入区
# ============================================================
from openpyxl import load_workbook
# load_workbook 是 openpyxl 提供的“打开 Excel 文件”的函数，
# 调用后得到的是一个 Workbook 对象（相当于整个 .xlsx 文件）

from common.logger import logger
# 项目自定义的日志对象，后面用 logger.info / logger.warning / logger.error 打印日志


# ============================================================
# 类定义
# ============================================================
class ReadExcel:
    """
    Excel 读取类。
    设计目标：不关心具体是哪张表、表头叫什么，只把“一行数据”读成 dict，
    让调用方（各测试用例文件）自己去取需要的字段。
    """

    def __init__(self, file_path, sheet_name, header_row=1):
        """
        构造函数：创建对象时执行一次，用来保存“读哪个文件、读哪个 sheet”这些配置。

        :param file_path:  Excel 文件的完整路径（字符串）
        :param sheet_name: 要读取的工作表名字（Excel 底部的标签页名）
        :param header_row: 表头在第几行（从 1 开始数），默认第 1 行。
                           如果表头上方还有标题行，就传 2、3……
        """
        # self.xxx 表示“把值存到这个对象身上”，后续方法里能通过 self.xxx 取出来
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.header_row = header_row

    # --------------------------------------------------------
    # 核心方法：读取并返回数据
    # --------------------------------------------------------
    def get_data(self, field_map: dict | None = None, skip_empty_row: bool = True):
        """
        读取 sheet 内容，返回 list[dict]。

        返回示例：
        [
            {"case_id": 1, "case_title": "正常登录", "username": "admin", ...},
            {"case_id": 2, "case_title": "密码错误", "username": "admin", ...},
        ]

        :param field_map:
            可选。类型是“字典或 None”，用于把 Excel 表头名映射成代码里的字段名。
            比如 Excel 写的是中文“用户名”，代码想用 "username"：
                field_map = {"用户名": "username", "密码": "password"}
            不传（None）就保留 Excel 原表头名。

        :param skip_empty_row:
            是否跳过整行都为空的行（Excel 里常有“只有格式没有内容”的空行）。
            默认 True 表示跳过。
        """
        # ① 打开 Excel 文件
        # read_only=True  ：只读模式打开，不把整本表载入内存，读大文件更快更省内存；
        #                   代价是不能修改文件、部分特性受限（读数据完全够用）。
        # data_only=True  ：如果单元格是公式（比如 =A1+B1），读取公式“计算后的值”而不是公式文本；
        #                   注意：如果这个文件从没被 Excel 打开保存过，公式缓存值可能读出来是 None。
        wb = load_workbook(filename=self.file_path, read_only=True, data_only=True)

        # ② try / except / finally 结构：
        #    try    里放正常逻辑；
        #    except 里捕获异常（打印日志后 raise 重新抛出，让上层知道出错了）；
        #    finally 里放“无论成功失败都一定要执行”的收尾代码（关闭文件）。
        #    这样保证文件句柄一定被释放，不会泄漏。
        try:
            # ③ 拿到指定的工作表（sheet）
            # wb["login"] 相当于“取 workbook 里名字叫 login 的那个 sheet”
            sheet = wb[self.sheet_name]

            # ④ iter_rows：按“行”迭代 sheet 数据
            #    values_only=True 表示只返回单元格的“值”，
            #    默认返回的是 Cell 对象（带样式、坐标等一堆属性，这里用不到）。
            #    返回值是一个“迭代器”：像流水线，取一次出一行，不会一次性把所有行塞进列表。
            rows = sheet.iter_rows(values_only=True)

            # ⑤ 跳过表头之前的若干行
            #    range(self.header_row - 1)：
            #      如果 header_row=1，range(0) 是空的，循环一次都不执行，符合预期；
            #      如果 header_row=3，range(2) → 执行 2 次，把第 1、2 行丢掉。
            #    next(rows, None)：
            #      next() 从迭代器里“取下一个元素”；
            #      第二个参数 None 是“默认值”——如果迭代器已经空了，就返回 None 而不是报错。
            #      这里只为了“消耗掉”前面的行，取出来的值不需要用，所以没赋值给变量。
            for _ in range(self.header_row - 1):
                next(rows, None)

            # ⑥ 取出表头行
            #    同样用 next(rows, None)，这一次把结果存到 header。
            #    如果表是空的，header 会是 None。
            header = next(rows, None)

            # ⑦ 空表保护：没有表头直接返回空列表，避免后面代码报错
            if header is None:
                logger.warning(f"[{self.sheet_name}] 空表，无表头")
                return []  # return 会直接结束方法，finally 照样会执行（关闭文件）

            # ⑧ 表头清洗（列表推导式）
            #    [表达式 for i, h in enumerate(header)]
            #    enumerate(header) 会同时给出“下标 i”和“元素 h”。
            #    这里的表达式：
            #       str(h).strip()  ：把表头转成字符串并去掉首尾空格（防止 " 用户名 " 这种脏数据）；
            #       条件“h is not None and str(h).strip()”为真，就用清洗后的值；
            #       否则（None 或者空白表头）用 "col_{i}" 生成占位列名，避免后面 key 是空字符串。
            header = [
                str(h).strip() if h is not None and str(h).strip() else f"col_{i}"
                for i, h in enumerate(header)
            ]

            # ⑨ 准备装结果的列表
            data_list = []

            # ⑩ 逐行处理数据（表头已经取走了，剩下的都是数据行）
            for row in rows:
                # 跳过整行为空的行
                #   all(条件 for v in row)：对 row 里每个值 v 判断条件，
                #   “全部为 True”时 all 才返回 True。
                #   这里条件是“v 是 None 或者 转字符串去空格后是空串”，
                #   即：每个单元格都是空的 → 整行为空 → continue 跳过这一行。
                if skip_empty_row and all(v is None or str(v).strip() == "" for v in row):
                    continue

                # ⑪ 行长度和表头对齐，防止后面 zip 错位
                #    iter_rows 有时会因为 Excel 里残留的格式，
                #    返回的列数比表头多（尾部一堆 None）或少。
                row = list(row)[: len(header)]
                #    [: len(header)] 是“切片”——只保留前 N 个元素，多出来的截掉。
                #    转 list(...) 是因为切片结果可迭代，但下面要对它做 += 拼接，需要是列表。

                #    如果行比表头短，用 None 补足：
                #    [None] * 缺的个数  → 生成一个全是 None 的列表，再拼到后面。
                row += [None] * (len(header) - len(row))

                # ⑫ 把表头和数据行“拉链式”配对成字典
                #    zip(header, row) 会把两组元素两两组合：
                #    ("case_id", 1), ("case_title", "正常登录"), ...
                #    dict(...) 再把这些键值对变成 {"case_id": 1, "case_title": "正常登录", ...}
                record = dict(zip(header, row))

                # ⑬ 值清洗（字典推导式）
                #    {k: 表达式 for k, v in record.items()}
                #    遍历原字典的每个键值对，生成一个新字典：
                #       v 是 None     → 转成 ""
                #       v 是字符串    → v.strip() 去掉首尾空格
                #       v 是数字/布尔等 → 原样保留
                #    isinstance(v, str) 用来判断 v 是不是字符串类型。
                record = {
                    k: ("" if v is None else (v.strip() if isinstance(v, str) else v))
                    for k, v in record.items()
                }

                # ⑭ 应用字段名映射（可选）
                #    field_map = {"用户名": "username"}
                #    对每个 原表头名(src) -> 目标名(target)，从 record 里取 src 的值放给 target；
                #    record.get(src, "") 意思是“取不到就返回空字符串”而不是报错。
                #    注意：用了 field_map 后，返回的 dict 只包含映射里列出的字段，其余字段会被丢弃。
                if field_map:
                    record = {target: record.get(src, "") for src, target in field_map.items()}

                # ⑮ 这一行处理完毕，加入结果列表
                data_list.append(record)

            # ⑯ 打印日志（成功时才有）
            logger.info(f"读取Excel[{self.sheet_name}]，一共 {len(data_list)} 条")

            # ⑰ 返回结果
            return data_list

        # ⑱ 任何异常都会被捕获到这里（KeyError sheet 名不对 / 文件不存在 / IO 错误等）
        except Exception as e:
            #    记录错误日志，方便排查
            logger.error(f"读取Excel失败[{self.sheet_name}]：{e}")
            #    raise 不带参数 = “把刚才捕获到的异常原样重新抛出”，
            #    这样上层（pytest）还能看到完整报错信息并判定用例失败。
            #    不写 raise 的话异常就被“吃掉”了，问题会被掩盖。
            raise

        # ⑲ 无论成功失败都执行
        finally:
            #    关闭工作簿，释放文件句柄和内存。
            #    read_only=True 模式尤其必须关闭，否则文件会一直占用。
            wb.close()