# -*- coding: utf-8 -*-
"""
用例数据构造工具
----------------
作用：为「部门角色」「知识库文档」等模块生成不重复的测试数据，
      保证每次执行都不会和库里已有数据、也不会和并发执行的其他用例撞名称。

约定：
1. 所有名称/编码都带时间戳 + 随机串后缀，用例结束后可以按后缀精准清理脏数据；
2. 入参传 None 表示「该字段不传」，构造方法会自动把 key 去掉，
   这样才能真正测出「仅传必填参数」的场景（传 null 和 不传 对后端 updateById/insert 行为不同）；
3. 部门 id 不硬编码在用例里，统一从 config.yaml 的 depart_id 读取。
"""

import time
import uuid

from common.read_config import read_config


def unique_suffix():
    """生成唯一的后缀：时分秒 + 6位随机串，例：171530_9f3ac1"""
    return time.strftime("%H%M%S") + "_" + uuid.uuid4().hex[:6]


def build_role_data(**overrides):
    """
    构造「部门角色」新增/编辑入参（字段名与接口文档 sys_depart_role 对象一致）
    :param overrides: 需要覆盖的字段，例如 build_role_data(roleName="") ；传 None 表示该字段不传
    :return: dict，可直接作为 json 请求体
    """
    suffix = unique_suffix()
    data = {
        "roleName": "自动化角色_" + suffix,      # 部门角色名称
        "roleCode": "auto_role_" + suffix,       # 部门角色编码
        "departId": read_config.get_depart_id(),  # 部门id
        "description": "接口自动化创建",          # 描述
    }
    data.update(overrides)
    # 过滤掉值为 None 的字段：None 代表「不传这个参数」
    return {key: value for key, value in data.items() if value is not None}


def build_doc_data(**overrides):
    """
    构造「知识库文档」新增/编辑入参（字段名与接口文档 sys_files 对象一致）
    :param overrides: 需要覆盖的字段；传 None 表示该字段不传
    :return: dict
    """
    suffix = unique_suffix()
    data = {
        "fileName": "自动化文档_" + suffix,        # 文件名称
        "fileType": "doc",                        # 文档类型：doc=word
        "fileSize": 12.5,                          # 文件大小（kb）
        "url": "knowledge/auto_" + suffix + ".doc",  # 文件地址
        "storeType": "manage",                     # manage=知识库
        "parentId": "0",                           # 父级id，0 表示根目录
        "izFolder": "0",                           # 是否文件夹：0-否
        "izStar": "0",                             # 是否标星：0-否
        "sharePerms": "1",                         # 分享权限：1-关闭分享
        "enableDown": "1",                         # 是否允许下载
        "enableUpdat": "1",                        # 是否允许修改
        "delFlag": "0",                            # 删除状态：0-正常
        "downCount": 0,                            # 下载次数
        "readCount": 0,                            # 阅读次数
    }
    data.update(overrides)
    return {key: value for key, value in data.items() if value is not None}
