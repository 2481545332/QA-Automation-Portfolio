# conftest.py
import pytest
import pymysql
import ddddocr
import uuid

from common.read_config import read_config
from common.request_util import RequestUtil
from common.captcha_helper import get_captcha_by_flag
from common.logger import logger


LOGIN_USER = {"username": "admin", "password": "123456"}


# ---------- 基础资源 ----------

@pytest.fixture(scope="session")
def ocr():
    """整个测试会话只实例化一次 OCR"""
    return ddddocr.DdddOcr()


@pytest.fixture(scope="session")
def db_conn():
    """
    session 级 mysql 连接。
    注意隔离级别必须改成 READ COMMITTED，否则接口提交后本连接查不到新数据。
    """
    mysql_info = read_config.get_mysql_info()
    conn = pymysql.connect(
        host=mysql_info["host"],
        port=mysql_info["port"],
        user=mysql_info["user"],
        password=mysql_info["password"],
        database=mysql_info["database"],
        charset="utf8mb4",
        autocommit=True,   # 可选：只做查询时建议开；需要事务回滚则删掉
    )
    with conn.cursor() as cursor:
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    yield conn
    try:
        conn.close()
    except Exception as e:
        logger.warning(f"关闭 mysql 连接失败：{e}")


@pytest.fixture(scope="session")
def http_util_session():
    """session 级请求实例，给 login_token 用，解决 scope 依赖冲突"""
    util = RequestUtil()
    yield util
    try:
        util.clear_token()
        # util.close()   # 如果 RequestUtil 内部有 requests.Session，补这一行
    except Exception as e:
        logger.warning(f"session 级 http_util 清理失败：{e}")


@pytest.fixture(scope="function")
def http_util():
    """function 级：每条用例全新实例，无残留 header/token"""
    util = RequestUtil()
    yield util
    try:
        util.clear_token()
        # util.close()
    except Exception as e:
        logger.warning(f"function 级 http_util 清理失败：{e}")


# ---------- 登录 token ----------

@pytest.fixture(scope="session")
def login_token(http_util_session, ocr):
    """session 级前置登录：全局只登一次，返回 token"""
    logger.info("===== 执行全局前置登录 =====")

    # ① 补 captcha_flag；② 解包三元组
    send_captcha, real_captcha, check_key = get_captcha_by_flag(
        http_util_session, ocr, captcha_flag="right"
    )
    logger.info(f"全局登录：checkKey={check_key} 识别={real_captcha} 传入={send_captcha!r}")

    # ③ 复用 LOGIN_USER
    resp_login = http_util_session.send(
        path="/sys/login",
        method="POST",
        json={**LOGIN_USER, "captcha": send_captcha, "checkKey": check_key},
        timeout=20,
    )
    logger.info(f"全局登录返回：{resp_login}")

    # ④ raise 代替 assert
    if not resp_login.get("success"):
        raise RuntimeError(f"session 前置登录失败：{resp_login}")
    token = (resp_login.get("result") or {}).get("token")
    if not token:
        raise RuntimeError(f"登录成功但未返回 token：{resp_login}")

    logger.info(f"全局登录成功，token 前 8 位：{token[:8]}...")

    yield token

    # 可选：登出，用 try/except 兜住，避免污染用例结果
    # try:
    #     http_util_session.send(
    #         path="/sys/logout", method="POST",
    #         headers={"X-Access-Token": token}, timeout=20,
    #     )
    # except Exception as e:
    #     logger.warning(f"登出失败（不影响用例结果）：{e}")


# ---------- 业务便捷 fixture ----------

@pytest.fixture(scope="function")
def auth_http(http_util, login_token):
    """已带上 token 的请求对象，用例直接用它发请求"""
    http_util.set_token(login_token)
    yield http_util
    # http_util 自己的 teardown 会 clear_token，这里不用再清


# ======= 用于登录其它账号 =======

# 注意：需要确保顶部已经导入了 RequestUtil
# from common.request_util import RequestUtil
# from common.captcha_helper import get_captcha_by_flag

@pytest.fixture(scope="session")
def get_custom_token(http_util_session, ocr):
    """
    动态登录工厂：传入指定账号密码，返回该账号专属的请求对象。
    这个 fixture 被设计成“工厂模式”：它返回的不是数据，而是一个“函数”。
    你在用例里调用这个函数，传不同账号，就能拿到不同人的 Token。
    """

    # 定义了 _login 这个内部函数，真正的登录逻辑在这里面
    def _login(username, password):
        # 设置最大重试次数，防止死循环
        max_retries = 3

        for attempt in range(max_retries):
            # 1. 获取并识别验证码
            send_captcha, real_captcha, check_key = get_captcha_by_flag(
                http_util_session, ocr, captcha_flag="right"
            )

            # 2. 组装当前账号的登录参数
            logger.info(f"【排查】准备组装JSON前，check_key的值是: {check_key}")
            login_json = {
                "username": username,
                "password": password,
                "captcha": send_captcha,
                "checkKey": check_key
            }

            logger.info(f"【排查】组装后的 login_json 是: {login_json}")

            # 3. 发送登录请求
            resp = http_util_session.send(path="/sys/login", method="POST", json=login_json, timeout=20)

            # 4. 判断是否成功
            if resp.get("success"):
                # 成功：提取 Token，并创建新实例返回
                token = resp["result"]["token"]
                new_util = RequestUtil()
                new_util.set_token(token)
                return new_util
            else:
                # 失败：记录日志，准备重试
                logger.warning(
                    f"⚠️ 账号 {username} 登录失败，原因：{resp.get('message')}，准备进行第 {attempt + 1} 次重试...")

        # 5. 如果循环了 3 次都没 return，说明彻底失败了，才报错中断用例
        raise RuntimeError(f"账号 {username} 重试 {max_retries} 次登录均失败！最后一次报错：{resp.get('message')}")

    return _login


# =========================================================================
# 🌟 部门角色模块 - 专属造数与清理夹具
# =========================================================================
# 先定义常量，避免在用例里写死
FINANCE_DEPT_ID = "67fc001af12a4f9b8458005d3f19934a"
DEV_DEPT_ID = "5159cde220114246b045e574adceafe9"


def get_client_by_token_type(get_custom_token, token_type):
    """根据账号类型获取登录态的 Client"""
    if token_type == "finance":
        # 财务部
        return get_custom_token("test_finance", "123456")
    elif token_type == "dev":
        # 研发部
        return get_custom_token("test_dev", "123456")
    elif token_type == "none":
        #管理员
        return RequestUtil()
    raise ValueError(f"未知 token_type: {token_type}")


@pytest.fixture(scope= "function")
def temp_role(get_custom_token, db_conn):
    """
    【核心造数夹具】自动建角色、返 ID、用完自动清理

    使用方式：
        role_id = temp_role("finance")        # 造1个财务部角色
        ids_list = temp_role("dev", count=2)  # 造2个研发部角色
    """
    created_ids = []  # 内部列表：记录本次用例过程中造过的所有 ID，用于后置清理

    # 内部工厂函数：真正的造数逻辑
    def _create(depart_type="finance", count=1):
        # 1. 获取财务部的操作权限（统一用财务账号去建数据）
        finance_client = get_client_by_token_type(get_custom_token, "finance")
        dept_id = FINANCE_DEPT_ID if depart_type == "finance" else DEV_DEPT_ID
        ids = []

        # 2. 循环创建 count 条数据
        for i in range(count):
            # 每次生成一个独一无二的名字，防止数据库唯一性冲突
            unique_name = f"夹具角色_{uuid.uuid4().hex[:6]}"

            # 发请求创建
            finance_client.send(path="/sys/sysDepartRole/add", method="POST",
                                json={"roleName": unique_name, "departId": dept_id})

            # 3. 查库获取刚刚创建的 ID（因为接口不返回 ID）
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT id FROM sys_depart_role WHERE role_name = %s", (unique_name,))
                res = cursor.fetchone()
                if res:
                    ids.append(res[0])  # 返回给用例用
                    created_ids.append(res[0])  # 记小本本上，待会要删

        # 根据用例要的数量决定返回单个 ID 还是 ID 列表
        return ids[0] if count == 1 else ids

    # ================= 核心分割线 =================
    # yield 之前：前置准备（Setup）
    yield _create
    # yield 之后：后置清理（Teardown）
    # ================= 核心分割线 =================

    # 4. 用例执行完毕，无论成功还是报错，都会执行下面的清理逻辑
    if created_ids:
        logger.info(f"🧹 开始清理测试数据，准备删除ID: {created_ids}")
        try:
            # 统一用 admin 账号去批量删除，保证清理权限最高
            admin_client = get_custom_token("admin", "123456")
            ids_str = ",".join(created_ids)
            admin_client.send(path="/sys/sysDepartRole/deleteBatch", method="DELETE", params={"ids": ids_str})
            logger.info("✅ 测试数据清理完成")
        except Exception as e:
            # 加 try-except 是为了防止报错打断用例的最终结果
            logger.warning(f"⚠️ 测试数据清理失败: {e}")

# =========================================================================
# 🌟 知识库文档模块 - 专属造数与清理夹具
# =========================================================================
@pytest.fixture
def temp_doc(get_custom_token, db_conn):
    """知识库文档造数与管理夹具"""
    created_docs = []

    def _create(depart_type="finance", file_name=None):
        # 1. 确定用哪个账号造数据
        finance_client = get_client_by_token_type(get_custom_token, "finance")
        if depart_type == "dev":
            client = get_client_by_token_type(get_custom_token, "dev")
        else:
            client = finance_client

        # 2. 如果没有指定名字，就随机生成一个唯一的名字
        doc_name = file_name or f"自动造数文档_{uuid.uuid4().hex[:6]}.txt"

        # 3. 发请求造数
        payload = {
            "fileName": doc_name,
            "fileType": "txt",
            "izFolder": 0,
            "storeType": "local"
        }
        res = client.send(path="/sys/files/add", method="POST", json=payload)

        # 4. 去数据库反查真实的 ID
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT id FROM sys_files WHERE file_name = %s", (doc_name,))
            result = cursor.fetchone()
            doc_id = result[0] if result else "fake_id_123"
            created_docs.append(doc_id)

        return doc_id, doc_name, client

    yield _create

    # ================= 后置清理 =================
    # 优化后的清理逻辑
    if created_docs:
        logger.info(f"🧹 开始清理测试数据，准备删除ID: {created_docs}")
        admin_client = get_custom_token("admin", "123456")
        for doc_id in created_docs:
            try:
                res = admin_client.send(path="/sys/files/delete", method="DELETE", params={"id": doc_id})
                if not res.get("success"):
                    logger.warning(f"⚠️ 文档 {doc_id} 清理失败，接口返回：{res}")
            except Exception as e:
                logger.error(f"❌ 文档 {doc_id} 清理异常：{e}")