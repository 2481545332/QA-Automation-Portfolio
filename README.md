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

## jeecg-boot-allure报告截图

<img width="411" height="377" alt="屏幕截图 2026-11-06 083345" src="https://github.com/user-attachments/assets/450ccfe9-0d23-42d9-b9a9-dbfb69d82a00" />

<img width="943" height="410" alt="屏幕截图 2026-11-06 083259" src="https://github.com/user-attachments/assets/752cff50-cb75-4230-913a-bb8e1cf642e2" />

<img width="931" height="415" alt="屏幕截图 2026-11-06 083215" src="https://github.com/user-attachments/assets/1a7fcbc0-7b39-4477-84a3-6baff7705add" />

<img width="921" height="443" alt="屏幕截图 2026-11-06 083129" src="https://github.com/user-attachments/assets/084914c9-3cda-4e95-b0ef-e8f70c102b83" />

## saucedome-allure报告截图

<img width="780" height="857" alt="image" src="https://github.com/user-attachments/assets/a13f9ddd-ec59-4bf2-aa5f-7d89ac672814" />

<img width="1626" height="782" alt="image" src="https://github.com/user-attachments/assets/ac3de975-4d28-415b-a917-090f2e633111" />

<img width="1633" height="738" alt="image" src="https://github.com/user-attachments/assets/0093172d-6fb2-4b4b-9d81-36677f436607" />

<img width="1593" height="790" alt="image" src="https://github.com/user-attachments/assets/11237ff6-8617-4cf7-8ce6-6fe79ead1022" />

<img width="1598" height="826" alt="image" src="https://github.com/user-attachments/assets/86da48de-7e2e-43af-bf1c-217041f91bf3" />
