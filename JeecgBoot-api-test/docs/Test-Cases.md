# JeecgBoot 接口自动化测试用例清单

本清单展示了本项目中的核心自动化测试用例，涵盖**登录模块**、**部门角色模块**和**知识库文档模块**，共计 44 条用例（含安全越权测试）。

## 一、登录模块 (Login)

| 用例编号 | 模块 | 用例标题 | 测试分类 | 前置条件 | 请求方法 | 接口路径 | 请求参数 (JSON/Params) | 预期结果（断言） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LOGIN-01 | 登录模块 | 正确账号密码登录成功 | 正向 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"admin","password":"123456","captcha":"...","checkKey":"..."}` | HTTP=200, code=200, success=true, 且 result.token 不为空 |
| LOGIN-02 | 登录模块 | 密码错误无法登录 | 异常 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"admin","password":"wrong","captcha":"...","checkKey":"..."}` | HTTP=200, success=false, message 包含“密码错误” |
| LOGIN-03 | 登录模块 | 账号为空无法登录 | 异常 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"","password":"123456","captcha":"...","checkKey":"..."}` | HTTP=200, success=false |
| LOGIN-04 | 登录模块 | 传入过期的验证码 Key | 异常 | 无 | POST | `/sys/login` | `{"username":"admin","checkKey":"expired_key"}` | HTTP=200, code=412, message 包含“验证码错误” |
| LOGIN-05 | 登录模块 | 传入错误的验证码 | 异常 | 无 | POST | `/sys/login` | `{"username":"admin","captcha":"wrong","checkKey":""}` | HTTP=200, code=413, message 包含“验证码错误” |
| LOGIN-06 | 登录模块 | 账号或密码超长边界测试 | 边界 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"A"*256, "password":"123456","captcha":"...","checkKey":"..."}` | HTTP=200，不应出现数据库异常，应正常拦截 |
| LOGIN-07 | 登录模块 | 用户不存在 | 异常 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"admin1", "password":"123456","captcha":"...","checkKey":"..."}` | HTTP=200, code=401, message 包含"该用户不存在请重新登录" |
| LOGIN-08 | 登录模块 | SQL 注入尝试登录 | 安全 | 获取正确的验证码 | POST | `/sys/login` | `{"username":"admin' OR 1=1 --", "password":"1"}` | HTTP=200, success=false，系统未发生注入泄漏 |

## 二、部门角色模块 (Role)

| 用例编号 | 模块 | 用例标题 | 测试分类 | 前置条件 | 请求方法 | 接口路径 | 请求参数 (JSON/Params) | 预期结果（断言） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ROLE-01 | 部门角色 | 财务部正常新增角色 | 正向 | 财务部账号登录 | POST | `/sys/sysDepartRole/add` | `{"roleName": "财务角色_01", "departId": "<财务部ID>"}` | HTTP=200, success=true, 提示“添加成功！”，查库校验数据落盘 |
| ROLE-02 | 部门角色 | 新增角色名称为空 | 异常 | 财务部账号登录 | POST | `/sys/sysDepartRole/add` | `{"roleName": "", "departId": "<财务部ID>"}` | HTTP=200, success=false, 提示参数校验失败 |
| ROLE-03 | 部门角色 | 角色名称超长边界测试 | 边界 | 财务部账号登录 | POST | `/sys/sysDepartRole/add` | `{"roleName": "测"*200, "departId": "<财务部ID>"}` | HTTP=200，验证数据库是否报错或提示字段超长 |
| ROLE-04 | 部门角色 | 无Token新增角色 | 权限 | 无 | POST | `/sys/sysDepartRole/add` | `{"roleName": "无权限角色", "departId": "<财务部ID>"}` | HTTP=200或401, code=401, 提示“Token失效” |
| ROLE-05 | 部门角色 | 财务越权给研发建角色 | 安全 | 财务部账号登录 | POST | `/sys/sysDepartRole/add` | `{"roleName": "越权角色", "departId": "<研发部ID>"}` | HTTP=200, success=false (若成功则记录高危越权漏洞) |
| ROLE-06 | 部门角色 | 正常分页查询角色列表 | 正向 | 财务部账号登录 | GET | `/sys/sysDepartRole/list` | Params: `pageNo=1&pageSize=10` | HTTP=200, 返回 records 数组 |
| ROLE-07 | 部门角色 | 负数分页边界测试 | 边界 | 财务部账号登录 | GET | `/sys/sysDepartRole/list` | Params: `pageNo=-1&pageSize=10` | HTTP=200，后端不抛 500 异常，有默认处理机制 |
| ROLE-08 | 部门角色 | 研发越权查财务角色 | 安全 | 财务部建好角色，研发部登录 | GET | `/sys/sysDepartRole/list` | Params: `pageNo=1&pageSize=100` | 研发部的 records 中不包含财务部建的角色 |
| ROLE-09 | 部门角色 | 查询真实存在的角色 | 正向 | 存在真实角色 | GET | `/sys/sysDepartRole/queryById` | Params: `id=<真实角色ID>` | HTTP=200, 返回角色详情 JSON |
| ROLE-10 | 部门角色 | 查询不存在的角色 | 异常 | 财务部账号登录 | GET | `/sys/sysDepartRole/queryById` | Params: `id=fake_id_123` | HTTP=200或500，提示“数据不存在” |
| ROLE-11 | 部门角色 | POST部分编辑-改名 | 正向 | 存在真实角色 | POST | `/sys/sysDepartRole/edit` | `{"id": "<真实角色ID>", "roleName": "新名字", "departId": "<财务部ID>"}` | HTTP=200, success=true, 修改成功 |
| ROLE-12 | 部门角色 | POST越权编辑研发角色 | 安全 | 研发部存在真实角色 | POST | `/sys/sysDepartRole/edit` | `{"id": "<研发角色ID>", "roleName": "黑客改名"}` | HTTP=200, success=false (若成功则有越权漏洞) |
| ROLE-13 | 部门角色 | PUT全量编辑-合法数据 | 正向 | 存在真实角色 | PUT | `/sys/sysDepartRole/edit` | `{"id": "<真实角色ID>", "roleName": "全量改名", "departId": "<财务部ID>", "description": "全量更新"}` | HTTP=200, success=true |
| ROLE-14 | 部门角色 | PUT全量编辑-必填项为空 | 异常 | 存在真实角色 | PUT | `/sys/sysDepartRole/edit` | `{"id": "<真实角色ID>", "roleName": "", "departId": ""}` | HTTP=200, success=false (系统应拦截必填校验) |
| ROLE-15 | 部门角色 | 正常单条删除 | 正向 | 存在真实角色 | DELETE | `/sys/sysDepartRole/delete` | Params: `id=<真实角色ID>` | HTTP=200, success=true, 查库确认 del_flag 变更为1 |
| ROLE-16 | 部门角色 | 删除不存在的角色ID | 异常 | 财务部账号登录 | DELETE | `/sys/sysDepartRole/delete` | Params: `id=fake_id_123` | HTTP=200, success=false 或提示数据不存在 |
| ROLE-17 | 部门角色 | 财务越权删除研发角色 | 安全 | 研发部存在真实角色 | DELETE | `/sys/sysDepartRole/delete` | Params: `id=<研发角色ID>` | HTTP=200, success=false (若成功则证明有越权漏洞) |
| ROLE-18 | 部门角色 | 正常批量删除 | 正向 | 存在多个真实角色 | DELETE | `/sys/sysDepartRole/deleteBatch` | Params: `ids=<ID1>,<ID2>` | HTTP=200, success=true |
| ROLE-19 | 部门角色 | 批量删除包含假ID | 异常 | 存在真实角色 | DELETE | `/sys/sysDepartRole/deleteBatch` | Params: `ids=<真实ID>,fake_999` | HTTP=200或500，验证事务处理（全部回滚或跳过假ID） |

## 三、知识库文档模块 (Document)

| 用例编号 | 模块 | 用例标题 | 测试分类 | 前置条件 | 请求方法 | 接口路径 | 请求参数 (JSON/Params) | 预期结果（断言） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| DOC-01 | 知识库文档 | 财务部正常新增文档 | 正向 | 财务部账号登录 | POST | `/sys/files/add` | `{"fileName": "财务报表.txt", "fileType": "txt", "fileSize": 1024, "izFolder": 0}` | HTTP=200, success=true, 提示“添加成功！”，查库校验 |
| DOC-02 | 知识库文档 | 新增文档名称为空 | 异常 | 财务部账号登录 | POST | `/sys/files/add` | `{"fileName": "", "fileType": "txt"}` | HTTP=200, success=false (验证必填项拦截) |
| DOC-03 | 知识库文档 | 文件名包含XSS脚本 | 安全 | 财务部账号登录 | POST | `/sys/files/add` | `{"fileName": "<script>alert(1)</script>", "fileType": "txt"}` | HTTP=200，后端应转义或拦截，不可原样返回导致前端弹窗 |
| DOC-04 | 知识库文档 | 无Token新增文档 | 权限 | 无 | POST | `/sys/files/add` | `{"fileName": "匿名文档.txt", "fileType": "txt"}` | HTTP=200或401, code=401, 提示“Token失效” |
| DOC-05 | 知识库文档 | 正常分页查询文档列表 | 正向 | 财务部账号登录 | GET | `/sys/files/list` | Params: `pageNo=1&pageSize=10` | HTTP=200, 返回 records 数组 |
| DOC-06 | 知识库文档 | 负数分页边界测试 | 边界 | 财务部账号登录 | GET | `/sys/files/list` | Params: `pageNo=-1&pageSize=10` | HTTP=200，后端不抛 500 异常 |
| DOC-07 | 知识库文档 | 研发部越权查财务部文档 | 安全 | 财务部建过文档，研发部登录 | GET | `/sys/files/list` | Params: `pageNo=1&pageSize=100` | 研发部的列表不包含财务部的文档（核心高危漏洞检测点） |
| DOC-08 | 知识库文档 | 查询真实存在的文档 | 正向 | 存在真实文档 | GET | `/sys/files/queryById` | Params: `id=<真实文档ID>` | HTTP=200, 返回文档详情 JSON |
| DOC-09 | 知识库文档 | 查询不存在的文档 | 异常 | 财务部账号登录 | GET | `/sys/files/queryById` | Params: `id=fake_id_123` | HTTP=200或500，提示“数据不存在” |
| DOC-10 | 知识库文档 | POST部分编辑-修改文件名 | 正向 | 存在真实文档 | POST | `/sys/files/edit` | `{"id": "<真实文档ID>", "fileName": "新名字.txt", "fileType": "txt"}` | HTTP=200, success=true, 查库校验文件名已更新 |
| DOC-11 | 知识库文档 | POST越权编辑研发文档 | 安全 | 研发部存在真实文档 | POST | `/sys/files/edit` | `{"id": "<研发文档ID>", "fileName": "黑客改名.txt"}` | HTTP=200, success=false (若成功则有越权修改漏洞) |
| DOC-12 | 知识库文档 | PUT全量编辑-合法数据 | 正向 | 存在真实文档 | PUT | `/sys/files/edit` | `{"id": "<真实文档ID>", "fileName": "全量改名.txt", "fileType": "txt"}` | HTTP=200, success=true |
| DOC-13 | 知识库文档 | PUT全量编辑-必填项为空 | 异常 | 存在真实文档 | PUT | `/sys/files/edit` | `{"id": "<真实文档ID>", "fileName": ""}` | HTTP=200, success=false (系统应拦截必填校验) |
| DOC-14 | 知识库文档 | 正常删除自己的文档 | 正向 | 财务部登录，且存在真实文档 | DELETE | `/sys/files/delete` | Params: `id=<财务文档ID>` | HTTP=200, success=true, 查库校验 del_flag 变更为1 |
| DOC-15 | 知识库文档 | 删除不存在的文档ID | 异常 | 财务部账号登录 | DELETE | `/sys/files/delete` | Params: `id=fake_id_123` | HTTP=200, success=false 或提示数据不存在 |
| DOC-16 | 知识库文档 | 研发越权删除财务文档 | 安全 | 财务部存在真实文档，研发登录 | DELETE | `/sys/files/delete` | Params: `id=<财务文档ID>` | HTTP=200, success=false (若成功则证明有越权删除漏洞) |
| DOC-17 | 知识库文档 | 正常批量删除 | 正向 | 存在多个真实文档 | DELETE | `/sys/files/deleteBatch` | Params: `ids=<ID1>,<ID2>` | HTTP=200, success=true |