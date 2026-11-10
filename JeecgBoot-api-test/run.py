import os
import shutil
import pytest
import subprocess
import webbrowser
import sys


def run_allure_report():
    allure_dir = "allure-results"
    report_dir = "allure-report"
    log_file_path = os.path.join("logs", "run.log")

    # 💡 新增：建一个本地 temp 文件夹，避开系统 Temp 的权限问题
    local_temp = os.path.abspath("local_temp")
    os.makedirs(local_temp, exist_ok=True)

    # 1. 清理旧allure结果
    if os.path.exists(allure_dir):
        shutil.rmtree(allure_dir)
        print("✅ 已清理历史allure结果")

    # 2. 清空旧日志
    if os.path.exists(log_file_path):
        os.remove(log_file_path)


    # 3. 执行pytest（透传命令行的参数）
    print("🚀 开始执行测试用例")
    # sys.argv[1:] 会把你在终端敲的 `-m smoke` 原封不动传给 pytest
    ret_code = pytest.main(sys.argv[1:])
    print(f"\n📌 pytest执行返回码：{ret_code}")

    # 4. 生成并打开报告
    if os.path.exists(allure_dir) and len(os.listdir(allure_dir)) > 0:
        print("\n🚀 正在生成 Allure 报告...")

        # 💡 核心改动：通过环境变量告诉底层的 Java，把临时文件放到我们刚刚建的 local_temp 里
        env = os.environ.copy()
        env["TEMP"] = local_temp
        env["TMP"] = local_temp

        subprocess.run(
            f"allure generate {allure_dir} -o {report_dir} --clean",
            shell=True,
            env=env  # 传入修改后的环境变量
        )

        report_path = os.path.abspath(os.path.join(report_dir, "index.html"))
        if os.path.exists(report_path):
            print(f"✅ 报告生成成功！正在浏览器打开：{report_path}")
            webbrowser.open(f"file:///{report_path}")
        else:
            print("❌ 报告生成失败，找不到 index.html")
    else:
        print("❌ allure结果目录为空，不启动报告！")


if __name__ == "__main__":
    run_allure_report()