# 软件测试自动化实战作品集 (QA Automation Portfolio)

本项目为个人技术实战汇总库，包含 **接口自动化** 与 **UI 自动化** 两个独立的企业级测试框架模块。所有项目均采用分层设计，集成 Allure 报告与自动断言机制，代码已稳定跑通。

## 📁 模块导航

### 1. 接口自动化测试框架 (JeecgBoot-api-test)
*   **被测系统**：JeecgBoot 1.0（企业级后台管理系统）
*   **技术栈**：Python + Pytest + Requests + Allure + MySQL + YAML/Excel
*   **核心亮点**：多账号鉴权、OCR 验证码重试机制、MySQL 深度查库断言、跨部门越权安全漏洞检测。
*   👉 [查看接口自动化详细说明](JeecgBoot-api-test/readme.md)

### 2. UI 自动化测试框架 (SauceDemo-ui-test)
*   **被测系统**：SauceDemo（知名电商演示系统）
*   **技术栈**：Python + Pytest + Selenium + PO 模式 + Allure + Excel
*   **核心亮点**：严格遵循 PO 模式解耦、显式等待处理异步渲染、防状态污染设计、失败自动截图钩子。
*   👉 [查看 UI 自动化详细说明与测试文档](SauceDemo-ui-test/readme.md)

## 🚀 运行方式
进入各个子模块目录，执行 `python run.py` 即可一键运行用例并生成可视化的 Allure 测试报告。