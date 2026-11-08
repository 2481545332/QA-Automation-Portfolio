import os
import shutil
import subprocess
import pytest
import webbrowser
import http.server
import socketserver
import threading


def main():
    # 强制切换到项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    allure_results_dir = os.path.join(project_root, "allure-results")
    allure_report_dir = os.path.join(project_root, "allure-report")

    # 清理历史数据
    if os.path.exists(allure_results_dir):
        shutil.rmtree(allure_results_dir)

    print("🚀 开始执行测试用例...")
    # 运行测试 (这里会自动读取 pytest.ini 里的 --alluredir)
    pytest.main(["-s", "-v", "testcases/"])

    print("📊 正在生成 Allure 报告...")

    # 尝试调用系统的 allure 命令生成报告
    try:
        # shell=True 允许系统去环境变量里找 allure
        res = subprocess.run(f"allure generate {allure_results_dir} -o {allure_report_dir} --clean", shell=True,
                             capture_output=True)
        if res.returncode != 0:
            print("⚠️ 警告：系统没有找到 allure 命令行工具，无法生成好看的 HTML 报告。")
            print("请访问 https://allure.qatools.ru/ 下载并配置环境变量。")
            return
    except Exception as e:
        print(f"执行 allure 命令失败: {e}")
        return

    # 核心修复：不使用 allure serve（因为它会找不着），而是用 Python 起本地服务器
    print("✅ 报告生成成功！正在启动本地服务器解决跨域问题...")

    # 切换工作目录到报告文件夹
    os.chdir(allure_report_dir)

    # 定义一个简单的 HTTP 服务器
    PORT = 8888
    Handler = http.server.SimpleHTTPRequestHandler

    # 在新线程中启动服务器
    httpd = socketserver.TCPServer(("", PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # 自动打开浏览器
    print(f"🌐 报告地址: http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")

    # 保持主线程阻塞，直到用户按 Ctrl+C
    input("按回车键 (Enter) 结束服务器并退出...\n")
    httpd.shutdown()


if __name__ == "__main__":
    main()