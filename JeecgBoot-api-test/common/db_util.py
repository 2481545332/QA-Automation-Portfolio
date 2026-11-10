import pymysql
from common.logger import logger

class DBUtil:
    def __init__(self, conn):
        """
        :param conn: 外部传入的pymysql数据库连接对象（来自conftest的session fixture）
        """
        self.conn = conn
        # 获取游标，用来执行sql
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        # DictCursor：查询结果返回字典，key是字段名，方便取数据，而不是元组，自动化断言更方便

    def query_one(self, sql, args=None):
        """查询单条数据，用于：根据唯一编码查角色/字典/文档，断言数据是否存在"""
        try:
            logger.info(f"执行查询SQL：{sql}，参数：{args}")
            self.cursor.execute(sql, args or ())
            # fetchone 拿第一条匹配数据
            result = self.cursor.fetchone()
            logger.info(f"查询结果：{result}")
            return result
        except Exception as e:
            logger.error(f"单条查询失败：{e}")
            raise e

    def query_all(self, sql, args=None):
        """查询多条数据，用于：统计条数、按名称模糊查多条、批量造数后的校验"""
        try:
            logger.info(f"执行查询SQL：{sql}，参数：{args}")
            self.cursor.execute(sql, args or ())
            result = self.cursor.fetchall()
            logger.info(f"查询结果条数：{len(result)}，结果：{result}")
            return result
        except Exception as e:
            logger.error(f"多条查询失败：{e}")
            raise e

    def count(self, sql, args=None):
        """
        统计条数，专门给「db 数量 +1 / 数量不变」这类断言用
        :param sql: 必须是 SELECT COUNT(*) AS cnt ... 形式
        :return: int
        """
        row = self.query_one(sql, args)
        # DictCursor 返回字典，直接用 cnt 字段取值
        return int(row["cnt"]) if row else 0

    def execute_sql(self, sql, args=None):
        """
        执行增、删、改等写操作（用例脏数据清理、造数、断言前后数据修复都用它）
        :return: 影响行数，配合断言「删除条数和 ids 长度一致」
        """
        try:
            logger.info(f"执行写操作SQL：{sql}，参数：{args}")
            self.cursor.execute(sql, args or ())
            # 写操作必须提交事务，否则其他连接（接口所在的应用）查不到
            self.conn.commit()
            rowcount = self.cursor.rowcount
            logger.info(f"写操作成功，影响行数：{rowcount}")
            return rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"写操作失败，已回滚！{e}")
            raise e

    def delete_by_sql(self, sql, args=None):
        """执行删除SQL，脏数据清理用，DML语句，需要commit"""
        try:
            logger.info(f"执行删除SQL：{sql}，参数：{args}")
            self.cursor.execute(sql, args or ())
            # 删除属于写操作，提交事务
            self.conn.commit()
            logger.info(f"删除成功，影响行数：{self.cursor.rowcount}")
        except Exception as e:
            # 出错就回滚，防止部分SQL执行成功，数据错乱
            self.conn.rollback()
            logger.error(f"删除失败，已回滚！{e}")
            raise e

    def close_cursor(self):
        """关闭游标，连接是session级别，不在这关闭；连接在conftest的fixture最后统一关闭"""
        if self.cursor:
            self.cursor.close()
            logger.info("游标已关闭")