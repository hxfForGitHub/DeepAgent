"""端到端测试：创建 OpenSandbox 沙箱并执行命令"""
from datetime import timedelta
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync


def test_create_sandbox():
    config = ConnectionConfigSync(
        domain="http://localhost:8080",
        api_key="your-secret-api-key",
        use_server_proxy=False,
        request_timeout=timedelta(seconds=60),
    )

    print("正在创建沙箱...")
    sandbox = SandboxSync.create(
        "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.2",
        entrypoint=["/opt/opensandbox/code-interpreter.sh"],
        env={"PYTHON_VERSION": "3.11"},
        timeout=timedelta(minutes=30),
        resource={"cpu": "2", "memory": "2Gi"},
        connection_config=config,
    )
    print(f"沙箱创建成功！ID: {sandbox.id}")

    result = sandbox.commands.run("echo 'Hello from sandbox!' && python --version")
    if result.logs.stdout:
        print(f"输出: {result.logs.stdout[0].text}")
    print(f"退出码: {result.exit_code}")

    sandbox.close()
    print("沙箱已关闭")


if __name__ == "__main__":
    test_create_sandbox()
