# JeecgBoot 接口自动化测试框架

基于 **Python + Pytest + Requests + Allure** 搭建的 JeecgBoot 开源系统接口自动化框架，覆盖**登录、部门角色、知识库文档**三大模块，共 **44 条**接口用例。支持 Excel / YAML 双数据驱动、验证码 OCR 识别、数据库查库校验、Fixture 自动造数与清理，并包含**跨部门越权安全测试**。

## 一、项目简介

- **被测系统**：JeecgBoot 1.0（本地部署）
- **测试类型**：接口功能测试 + 数据一致性校验 + 跨部门越权安全测试
- **用例规模**：登录 8 条、部门角色 19 条、知识库文档 17 条，合计 **44 条**。
- **设计目标**：用例只关心「入参 → 断言」，登录鉴权、造数、清理全部由 fixture 统一处理；用例可重复执行，不污染测试环境。

## 二、技术栈

| 分类 | 技术 |
|------|------|
| 核心框架 | Python 3, Pytest 7.4, Requests |
| 测试报告 | Allure |
| 数据驱动 | openpyxl (Excel), PyYAML (YAML) |
| 验证码识别 | ddddocr |
| 数据库 | MySQL, PyMySQL (DictCursor) |
| 日志与配置 | loguru, PyYAML |

## 三、项目结构

```text
jeecg-boot-auto-test/
├── config/                  # 环境配置
│   ├── config.yaml          # 真实环境配置（含账号密码，已加入 gitignore）
│   └── config_example.yaml  # 配置模板
├── common/                  # 公共工具封装
│   ├── captcha_helper.py    # 验证码获取与 OCR 识别
│   ├── data_util.py         # 造数工具（唯一名称/编码生成）
│   ├── db_util.py           # MySQL 操作封装（查库、清理）
│   ├── logger.py            # loguru 日志（含 Windows GBK 编码兜底）
│   ├── path.py              # 路径常量管理
│   ├── read_config.py       # 读取 config.yaml，全局单例
│   ├── read_excel.py        # Excel 数据驱动读取
│   ├── read_yaml.py         # YAML 数据驱动读取
│   └── request_util.py      # 请求封装（Session、Token、原始响应返回）
├── data/                    # 测试数据
│   ├── jeecg-boot.xlsx      # 登录(8条)、角色(19条) 数据驱动
│   └── doc.yaml             # 知识库文档(17条) 数据驱动
├── testcases/               # 测试用例集
│   ├── test_login.py        # 登录模块（数据驱动）
│   ├── test_role.py         # 部门角色模块（数据驱动）
│   └── test_doc.py          # 知识库文档模块（数据驱动）
├── conftest.py              # 全局 Fixture（鉴权、多账号、DB、造数与清理）
├── init_data.py             # 初始化跨部门越权测试账号
├── pytest.ini               # pytest 配置文件
├── run.py                   # 一键执行脚本（清理旧数据、跑用例、生成并打开 Allure）
└── requirements.txt         # 依赖清单
```

## 四、框架设计核心

### 1. 配置层
`config.yaml` 按 `env` 区分环境，管理 `base_url`、账号、MySQL 等。`read_config.py` 实例化为单例，消除代码中的硬编码。

### 2. 请求层
`RequestUtil` 封装 `Session` 维持会话，自动携带 `X-Access-Token`。提供 `return_raw=True` 选项，用于获取验证码图片等非 JSON 响应。

### 3. 数据层与造数
- **双引擎驱动**：登录、角色走 Excel（`openpyxl`）；文档走 YAML（`PyYAML`），结构更清晰。
- **数据隔离**：`data_util.py` 使用「时分秒+随机串」生成唯一名称，防止并发冲突。

### 4. 夹具层 (conftest.py)
- `get_custom_token`：**多账号登录工厂**，传入账号密码返回专属 Client，用于跨部门越权测试。
- `temp_role` / `temp_doc`：**数据清理神器**。自动调接口造数 → 查库拿真实 ID → 用例结束用 admin 权限兜底强删。保证断言失败也能清理脏数据。

### 5. 核心亮点机制
- **验证码 3 次重试**：解决 OCR 偶发识别失败导致的用例中断。
- **隔离级别修正**：`db_conn` 将 MySQL 隔离级别改为 `READ COMMITTED`，解决接口写入后同一连接查不到数据的断言误判。
- **日志编码兜底**：重写 loguru 控制台 `sink`，解决 Windows GBK 下打印 emoji 报错导致 `pytest` 退出码为 1 的问题。

## 五、安全测试实战（越权漏洞）

在部门角色和文档模块中，利用财务（finance）和研发（dev）两个账号进行交叉操作，验证权限隔离机制：

| 用例编号 | 测试场景 | 测试结果 |
|---------|---------|---------|
| DOC-06 | 研发越权查询财务文档列表 | ✅ 拦截有效（列表 API 有部门隔离） |
| DOC-10 | 研发越权修改财务文档 | ❌ **漏洞成立**（查库确认文件名被篡改） |
| DOC-15 | 研发越权删除财务文档 | ❌ **漏洞成立**（查库确认记录被物理删除） |

*(注：测试采用「造数名与修改名分离 + 查库比对」的方式，彻底避免同名导致的假漏洞误报。)*

## 六、环境准备与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制模板并修改你的本地环境配置：

```bash
cp config/config_example.yaml config/config.yaml
```

### 3. 初始化测试账号

```bash
python init_data.py
```
*(自动创建 `test_finance` 和 `test_dev` 账号，用于越权用例)*

### 4. 执行用例

```bash
# 一键跑全量 + 生成并打开 Allure 报告
python run.py

# 跑指定模块
pytest testcases/test_login.py -v
pytest testcases/test_doc.py -v
```
## 📚 项目测试资产与文档

- [被测系统接口清单 (API-List)](docs/API-List.md)
- [接口自动化测试用例清单 (Test-Cases)](docs/Test-Cases.md)
- [全量测试点分析与脑图架构 (Test-Architecture)](docs/Test-Architecture.md)
- [自动化测试缺陷报告 (Bug-Report)](docs/Bug-Report.md)