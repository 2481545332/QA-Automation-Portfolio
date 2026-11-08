import pytest
import allure
from common.read_excel import ReadExcel
from common.path import EXCEL_PATH
from common.logger import logger
# 引入 conftest 里的辅助函数，用于发请求
from conftest import get_client_by_token_type, FINANCE_DEPT_ID, DEV_DEPT_ID

# 1. 读取 role 总表数据
excel_role = ReadExcel(EXCEL_PATH, "role").get_data()


@allure.feature("部门角色模块")
@allure.story("接口测试-全维度数据驱动")
@pytest.mark.parametrize("case", excel_role, ids=lambda x: x["case_id"])
def test_role_module(get_custom_token, db_conn, temp_role, case):
    # 1. 解析 Excel 参数
    case_id = case["case_id"]
    api_type = case["api_type"]
    case_title = case["case_title"]
    role_name = case["role_name"]
    depart_type = case["depart_type"]
    token_type = case["token_type"]
    target_id_type = case.get("target_id_type", "none")
    page_no = case.get("page_no", 1)
    expect_code = case["expect_code"]
    expect_success = str(case["expect_success"]).upper() == "TRUE"

    allure.dynamic.title(f"{case_id} - {case_title}")
    logger.info(f"===== 开始执行 {case_id}: {case_title} =====")

    # 获取发请求的 Client 和目标部门 ID
    client = get_client_by_token_type(get_custom_token, token_type)
    target_depart_id = FINANCE_DEPT_ID if depart_type == "finance" else DEV_DEPT_ID

    # 2. 智能前置造数 (调用 conftest 里的神器)
    target_id = None
    target_ids_str = None

    if api_type == "deleteBatch" and target_id_type == "valid":
        # 批删：造 2 条
        ids_list = temp_role(depart_type, count=2)
        target_ids_str = ",".join(ids_list)
    elif target_id_type == "valid":
        # 造 1 条有效的
        target_id = temp_role(depart_type)
        target_ids_str = target_id
    elif target_id_type == "invalid":
        # 造假的
        target_id = "fake_id_9999"
        target_ids_str = "fake_id_111,fake_id_222"
    elif target_id_type == "dev":
        # 造 1 条研发部的（为了测越权）
        target_id = temp_role("dev")


    # 3. 核心路由分发 (7 个接口)
    resp = None
    if api_type == "add":
        resp = client.send(path="/sys/sysDepartRole/add", method="POST",
                           json={"roleName": role_name, "departId": target_depart_id})
    elif api_type == "list":
        resp = client.send(path="/sys/sysDepartRole/list", method="GET", params={"pageNo": page_no, "pageSize": 10})
    elif api_type == "queryById":
        resp = client.send(path="/sys/sysDepartRole/queryById", method="GET", params={"id": target_id})
    elif api_type == "post_edit":
        resp = client.send(path="/sys/sysDepartRole/edit", method="POST",
                           json={"id": target_id, "roleName": role_name, "departId": target_depart_id})
    elif api_type == "put_edit":
        resp = client.send(path="/sys/sysDepartRole/edit", method="PUT",
                           json={"id": target_id, "roleName": role_name, "departId": target_depart_id,
                                 "description": "全量编辑"})
    elif api_type == "delete":
        resp = client.send(path="/sys/sysDepartRole/delete", method="DELETE", params={"id": target_id})
    elif api_type == "deleteBatch":
        resp = client.send(path="/sys/sysDepartRole/deleteBatch", method="DELETE", params={"ids": target_ids_str})
    else:
        raise ValueError(f"❌ 未知 api_type: {api_type}")

    # 4. 基础断言
    logger.info(f"响应结果: {resp}")
    actual_code = resp.get("code")
    assert str(actual_code) == str(expect_code), f"❌ 预期 code={expect_code}, 实际={actual_code}"

    actual_success = resp.get("success")
    if actual_code == 401: actual_success = False
    assert actual_success == expect_success, f"❌ 预期 success={expect_success}, 实际={actual_success}"

    # 5. 深度业务断言
    if expect_code == 200 and actual_success is True:

        # 5.1 越权查询校验
        if api_type == "list" and token_type == "dev" and target_id_type == "valid":
            records = resp.get("result", {}).get("records", [])
            found_ids = [r["id"] for r in records]
            assert target_id not in found_ids, "❌ 高危越权漏洞：研发部查到了财务部角色！"
            logger.success("✅ 越权查询校验通过")

        # 5.2 编辑查库
        elif api_type in ["post_edit", "put_edit"] and target_id:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT role_name FROM sys_depart_role WHERE id = %s", (target_id,))
                res = cursor.fetchone()
                assert res and res[0] == role_name, f"❌ 数据库校验：编辑未生效"
                logger.success("✅ 数据库校验：编辑成功")

        # 5.3 删除查库
        elif api_type in ["delete", "deleteBatch"] and target_id_type == "valid":
            with db_conn.cursor() as cursor:
                if api_type == "delete":
                    cursor.execute("SELECT id FROM sys_depart_role WHERE id = %s", (target_id,))
                    assert cursor.fetchone() is None, "❌ 数据库校验：记录未删除"
                else:
                    for rid in target_ids_str.split(","):
                        cursor.execute("SELECT id FROM sys_depart_role WHERE id = %s", (rid,))
                        assert cursor.fetchone() is None, f"❌ 数据库校验：{rid} 未删除"
                logger.success("✅ 数据库校验：删除成功")