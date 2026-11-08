# JeecgBoot 被测系统接口清单

本清单梳理了本次接口自动化测试涉及的核心 API，包含登录鉴权、部门角色管理与知识库文档管理三大模块。

| 编号 | 所属模块 | 接口名称 | 请求方法 | URL 路径 | 是否需 Token | 请求关键参数 | 响应关键字段 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| API-01 | 登录模块 | 获取验证码 | GET | `/sys/randomImage/{key}` | 否 | `key` | `result`, `success` | 返回 base64 图片流 |
| API-02 | 登录模块 | 登录接口 | POST | `/sys/login` | 否 | `captcha`, `checkKey`, `username`, `password` | `result.token`, `success` | 获取全局 X-Access-Token |
| API-03 | 部门角色 | 部门角色-添加 | POST | `/sys/sysDepartRole/add` | 是 | `createBy`, `departId`, `description`, `roleCode`, `roleName` 等 | `success`, `message`, `result` | 新增部门角色 |
| API-04 | 部门角色 | 部门角色-通过id删除 | DELETE | `/sys/sysDepartRole/delete` | 是 | `id` | `success`, `message`, `result` | 物理删除 |
| API-05 | 部门角色 | 部门角色-批量删除 | DELETE | `/sys/sysDepartRole/deleteBatch` | 是 | `ids` (逗号分隔) | `success`, `message`, `result` | 批量删除操作 |
| API-06 | 部门角色 | 部门角色-编辑 | POST | `/sys/sysDepartRole/edit` | 是 | `id`, `departId`, `roleName`, `roleCode` 等 | `success`, `message`, `result` | POST 局部更新 |
| API-07 | 部门角色 | 部门角色-全量编辑 | PUT | `/sys/sysDepartRole/edit` | 是 | `id`, `departId`, `roleName`, `roleCode` 等 | `success`, `message`, `result` | PUT 全量更新 |
| API-08 | 部门角色 | 部门角色-分页列表查询 | GET | `/sys/sysDepartRole/list` | 是 | `pageNo`, `pageSize`, `roleName`, `departId` 等 | `success`, `message`, `result` | 默认分页查询 |
| API-09 | 部门角色 | 部门角色-通过id查询 | GET | `/sys/sysDepartRole/queryById` | 是 | `id` | `success`, `message`, `result` | 获取角色详情 |
| API-10 | 知识库-文档 | 知识库-文档-添加 | POST | `/sys/files/add` | 是 | `fileName`, `fileType`, `fileSize`, `izFolder`, `storeType` 等 | `success`, `message`, `result` | 新增文档或文件夹 |
| API-11 | 知识库-文档 | 知识库-文档-通过id删除 | DELETE | `/sys/files/delete` | 是 | `id` | `success`, `message`, `result` | 物理删除 |
| API-12 | 知识库-文档 | 知识库-文档-批量删除 | DELETE | `/sys/files/deleteBatch` | 是 | `ids` (逗号分隔) | `success`, `message`, `result` | 批量删除操作 |
| API-13 | 知识库-文档 | 知识库-文档-编辑 | POST | `/sys/files/edit` | 是 | `id`, `fileName`, `fileType`, `parentId`, `sharePerms` 等 | `success`, `message`, `result` | POST 局部更新 |
| API-14 | 知识库-文档 | 知识库-文档-全量编辑 | PUT | `/sys/files/edit` | 是 | `id`, `fileName`, `fileType`, `parentId`, `sharePerms` 等 | `success`, `message`, `result` | PUT 全量更新 |
| API-15 | 知识库-文档 | 知识库-文档-分页列表查询 | GET | `/sys/files/list` | 是 | `pageNo`, `pageSize`, `fileName`, `storeType`, `parentId` 等 | `success`, `message`, `result` | 分页及权限过滤 |
| API-16 | 知识库-文档 | 知识库-文档-通过id查询 | GET | `/sys/files/queryById` | 是 | `id` | `success`, `message`, `result` | 获取文档详情 |