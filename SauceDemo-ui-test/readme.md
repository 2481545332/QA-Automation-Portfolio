# SauceDemo 电商系统 UI 自动化测试框架

基于 **Python + Pytest + Selenium + PO 模式 + Allure** 搭建的 Web UI 自动化回归测试框架。本项目针对 SauceDemo（知名开源电商演示系统）的核心购物流程进行了自动化覆盖。

## 📌 项目简介
- **被测系统**：SauceDemo (https://www.saucedemo.com/)
- **测试范围**：登录模块、商品列表模块、购物车模块、订单结算模块。
- **用例规模**：20 条核心回归测试用例（覆盖正常流程与异常校验）。
- **设计目标**：采用 Page Object 模式实现代码高复用；通过 Session 级 Fixture 实现一次登录全局复用；结合 Excel 实现数据驱动；集成 Allure 生成高度可视化的测试报告。

## 🛠️ 技术栈
| 分类 | 技术 |
| :--- | :--- |
| 测试框架 | Pytest |
| UI 驱动 | Selenium 4.x |
| 设计模式 | Page Object (PO) |
| 数据驱动 | openpyxl (Excel) |
| 测试报告 | Allure |
| 日志系统 | Loguru |

## 📂 项目结构
```text
sauce_demo_ui_test/
├── config/          # 环境与账号配置
├── common/          # 公共工具（日志、Excel读取）
├── base/            # BasePage 底层封装（显式等待、截图）
├── pages/           # PO 对象层（元素定位与业务动作分离）
├── data/            # Excel 测试数据
├── testcases/       # 测试用例层（数据驱动与业务断言）
├── docs/            # 项目管理文档（计划、用例、缺陷报告）
├── pytest.ini       # Pytest 配置文件
└── run.py           # 一键执行入口