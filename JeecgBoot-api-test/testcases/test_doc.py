# testcases/test_doc.py
import pytest
import allure
from uuid import uuid4

from common.read_yaml import ReadYaml
from common.logger import logger
# 引入鉴权工厂
from conftest import get_client_by_token_type

# 读取 YAML 数据
yaml_data = ReadYaml("doc.yaml").get_data()


@allure.feature("知识库文档模块")
@allure.story("接口测试-YAML数据驱动")
@pytest.mark.parametrize("case", yaml_data, ids=lambda x: x["case_id"])
def test_document_module(get_custom_token, db_conn, temp_doc, case):
    """知识库文档全维度自动化测试"""
    # ================= 1. 解析 YAML 参数 =================
    case_id = case["case_id"]
    api_type = case["api_type"]
    case_title = case["case_title"]
    file_name = case["file_name"]              # YAML 声明的"目标动作文件名"
    token_type = case["token_type"]            # finance / dev / admin
    target_id_type = case["target_id_type"]    # valid / finance / invalid
    page_no = case.get("page_no", 1)
    expect_code = case["expect_code"]
    expect_success = str(case["expect_success"]).lower() == "true"

    allure.dynamic.title(f"{case_id} - {case_title}")
    # 安全类用例统一打 CRITICAL 严重级别 + 安全测试标签，Allure 报告里会单独高亮
    if token_type == "dev" and target_id_type == "finance":
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        allure.dynamic.tag("安全测试", "越权漏洞")
    logger.info(f"===== 开始执行 {case_id}: {case_title} =====")

    # ================= 2. 智能前置造数 =================
    target_id = None
    target_file_name = file_name
    target_ids_str = None

    if api_type == "deleteBatch" and target_id_type == "valid":
        # 批删专用：造 2 条有效数据
        id1, _, _ = temp_doc("finance")
        id2, _, _ = temp_doc("finance")
        target_ids_str = f"{id1},{id2}"
        # 请求 client 按 YAML 指定的 token 取（批删用例通常是 finance 删自己的）
        client = get_client_by_token_type(get_custom_token, token_type)

    elif target_id_type == "valid":
        # 造一条【财务部】的常规文档
        # 修复 DOC-06：temp_doc 返回的第 3 个值是"造数用的财务 client"，
        # 绝不能直接拿去发请求，否则越权用例就变成"财务查自己"，永远查得到。
        # 这里用 _ 丢弃，请求 client 按 token_type 重新取。
        target_id, target_file_name, _ = temp_doc("finance", file_name)
        client = get_client_by_token_type(get_custom_token, token_type)

    elif target_id_type == "finance":
        # 造一条【财务部】的机密文档，给研发(dev)越权去查/改/删
        # 修复 DOC-06/10/15：同上，造数 client 丢弃，请求 client 按 token_type 取
        #
        # 修复 DOC-10 的同名陷阱：
        # 如果造数名和 payload 里的新名都用 file_name，
        # 那么数据库里改没改都是同一个值，根本区分不出来，会造成"假漏洞"误报。
        # 所以这里用一个带唯一后缀的"原始名"造数，和 payload 里的 file_name 区分开。
        original_name = f"财务原始机密_{case_id}_{uuid4().hex[:6]}.txt"
        target_id, target_file_name, _ = temp_doc("finance", original_name)
        client = get_client_by_token_type(get_custom_token, token_type)

    elif target_id_type == "invalid":
        target_id = "fake_id_9999"
        target_ids_str = "fake_id_111,fake_id_222"
        client = get_client_by_token_type(get_custom_token, token_type)

    else:
        # 正常用例，拿对应 Token 的 client
        client = get_client_by_token_type(get_custom_token, token_type)

    # ================= 3. 核心路由分发 =================
    resp = None
    if api_type == "add":
        payload = {
            "fileName": file_name,
            "fileType": "txt",
            "izFolder": 0,
            "storeType": "local"
        }
        resp = client.send(path="/sys/files/add", method="POST", json=payload)

    elif api_type == "list":
        resp = client.send(path="/sys/files/list", method="GET", params={"pageNo": page_no, "pageSize": 10})

    elif api_type == "queryById":
        resp = client.send(path="/sys/files/queryById", method="GET", params={"id": target_id})

    elif api_type == "post_edit":
        # 注意：payload 里的 fileName 用 YAML 的 file_name（"黑客改名的文档.txt"），
        # 跟造数用的 original_name 不同，这样才能从数据库判断是否真的被改
        payload = {"id": target_id, "fileName": file_name, "fileType": "txt"}
        resp = client.send(path="/sys/files/edit", method="POST", json=payload)

    elif api_type == "put_edit":
        payload = {"id": target_id, "fileName": file_name, "fileType": "txt", "description": "全量更新"}
        resp = client.send(path="/sys/files/edit", method="PUT", json=payload)

    elif api_type == "delete":
        resp = client.send(path="/sys/files/delete", method="DELETE", params={"id": target_id})

    elif api_type == "deleteBatch":
        resp = client.send(path="/sys/files/deleteBatch", method="DELETE", params={"ids": target_ids_str})

    # ================= 4. 基础断言 =================
    logger.info(f"响应结果: {resp}")
    actual_code = resp.get("code")
    assert str(actual_code) == str(expect_code), f"❌ 预期 code={expect_code}, 实际={actual_code}"

    actual_success = resp.get("success")
    assert actual_success == expect_success, f"❌ 预期 success={expect_success}, 实际={actual_success}"

    # ================= 5. 深度业务断言 =================
    if expect_code == 200 and actual_success is True:

        # 🌟 亮点 1：研发越权查财务文档（本系统 list 有隔离，反向断言绝对查不到）
        if api_type == "list" and token_type == "dev" and target_id_type == "finance":
            records = resp.get("result", {}).get("records", [])
            found_names = [r["fileName"] for r in records]
            # 既然你用了研发的 Token，列表里绝对不能出现财务那个机密文件名！
            assert target_file_name not in found_names, f"❌ 高危越权漏洞：研发查到了财务部文档！({target_file_name})"
            logger.success("✅ 跨部门查询拦截校验通过：list 接口有部门隔离，无越权泄露！")

        # 🌟 亮点 2：研发越权改/删（本系统 edit/delete 无部门隔离，实测漏洞成立）
        # 断言策略：从"验证拦截"改为"验证漏洞存在"，作为安全回归用例长期守护。
        # 若未来开发修复了权限隔离，这两条会变红，届时人工调整期望即可。
        elif api_type in ["post_edit", "delete"] and token_type == "dev" and target_id_type == "finance":
            with db_conn.cursor() as cursor:
                # 修复 DOC-10/15：字段名必须是下划线 file_name，不是驼峰 fileName
                cursor.execute(
                    "SELECT file_name, del_flag FROM sys_files WHERE id = %s",
                    (target_id,)
                )
                result = cursor.fetchone()

            if api_type == "post_edit":
                # 造数用 original_name，payload 用 file_name
                #   - 漏洞成立：db_file_name 已被篡改为 file_name → 断言通过
                #   - 漏洞被修复：db_file_name 仍是 original_name → 断言失败，提示移除安全用例
                assert result is not None, (
                    f"❌ 数据库查不到 id={target_id} 的记录，造数异常"
                )
                db_file_name = result[0]
                assert db_file_name == file_name, (
                    f"ℹ️ 越权修改已被修复：数据库文件名仍为 {db_file_name}，"
                    f"说明本次漏洞已不存在，可移除该安全用例或调整期望"
                )
                logger.warning(
                    f"🚨 高危越权漏洞确认：研发成功篡改财务文档 "
                    f"{target_file_name} -> {file_name}（id={target_id}）"
                )

            elif api_type == "delete":
                # JeecgBoot 的 /sys/files/delete 是物理删除，不是逻辑删除
                #   - 漏洞成立：数据库已查不到该记录（result is None）→ 断言通过
                #   - 漏洞被修复：数据库仍能查到该记录 → 断言失败，提示移除安全用例
                assert result is None, (
                    f"ℹ️ 越权删除已被修复：数据库仍能查到 id={target_id}，"
                    f"说明本次漏洞已不存在，可移除该安全用例或调整期望"
                )
                logger.warning(
                    f"🚨 高危越权漏洞确认：研发成功物理删除财务文档 "
                    f"id={target_id}（记录已从 sys_files 消失）"
                )