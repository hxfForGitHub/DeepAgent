import os
import httpx
from opensandbox.config import ConnectionConfigSync
from datetime import timedelta
from opensandbox import SandboxSync


def get_or_create_sandbox(config, sandbox_id=None, image=None):
    """
    获取或创建沙箱
    Args:
        config: ConnectionConfigSync 配置
        sandbox_id: 可选，要连接的现有沙箱ID
        image: 可选，创建新沙箱时使用的镜像
    Returns:
        SandboxSync 实例
    """
    sandbox = None
    
    if sandbox_id:
        # 连接到现有沙箱
        print(f"[INFO] 正在连接到现有沙箱: {sandbox_id}")
        try:
            sandbox = SandboxSync.connect(sandbox_id, connection_config=config)
            print(f"[INFO] 成功连接到沙箱: {sandbox_id}")
            return sandbox
        except Exception as e:
            print(f"[WARNING] 连接沙箱失败: {e}，将创建新沙箱")
    # 如果没有提供sandbox_id或连接失败，创建新沙箱
    if sandbox is None:
        if not image:
            image = "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.2"
        print(f"[INFO] 正在创建新沙箱，使用镜像: {image}")
        sandbox = SandboxSync.create(
            image,
            entrypoint=["/opt/opensandbox/code-interpreter.sh"],
            env = {"PYTHON_VERSION": "3.11"},
            resource={"cpu": "2", "memory": "2Gi"},
            timeout = timedelta(minutes=30),
            connection_config=config,
            # 网络路由限制，非必填
            # network_policy=NetworkPolicy(  # 沙箱网络路由限制策略
            #     defaultAction="deny",
            #     egress=[
            #         NetworkRule(action="allow", target="pypi.org"),
            #         NetworkRule(action="allow", target="*.github.com"),
            #     ]
            # )
        )
        print(f"[INFO] 成功创建新沙箱，ID: {sandbox.id}")
        return sandbox
def list_running_sandboxes(config):
    pass
# 这些个skill需要在本地下载好，或写好，也可以让程序去下载，然后再同步到沙箱里面，才能去执行。
# 沙箱就是运行 agent 觉得不安全的代码，比如执行系统命令，访问文件系统等。
# 有沙箱，就把这些可能的风险，把风险都限制在沙箱里面，不会影响到主系统的安全。
# 所以需要执行的东西，需要先同步到沙箱里面，才能去执行。
def sync_skills_to_sandbox(backend, local_skills_path, sandbox_skills_path):
    """
    智能同步技能目录到沙箱
    只上传沙箱中不存在的技能目录
    Args:
        backend: OpenSandbox后端实例
        local_skills_path: 本地技能目录路径
        sandbox_skills_path: 沙箱中技能目录路径
    """
    # 1. 确保沙箱技能目录存在
    print(f"[DEBUG] 确保沙箱技能目录存在")
    result = backend.execute(f"mkdir -p {sandbox_skills_path}")
    if hasattr(result, 'exit_code') and result.exit_code != 0:
        print(f"[WARNING] 创建沙箱目录失败: {result}")
    # 2. 获取沙箱中已存在的技能目录
    print(f"[DEBUG] 检查沙箱中已存在的技能目录...")
    # 方法1: 尝试使用ls命令
    list_cmd = f"ls -1 {sandbox_skills_path}/ 2>/dev/null || true"
    result = backend.execute(list_cmd)
    # 调试：打印结果
    print(f"[DEBUG] ls命令结果: {result}")
    print(f"[DEBUG] 结果类型: {type(result)}")
    # 检查结果对象的属性
    if hasattr(result, '__dict__'):
        print(f"[DEBUG] 结果对象属性: {result.__dict__}")
    existing_skills = set()
    # 尝试从结果中提取输出
    if hasattr(result, 'stdout'):
        output = result.stdout
    elif hasattr(result, 'output'):
        output = result.output
    elif hasattr(result, 'result'):
        output = result.result
    elif isinstance(result, str):
        output = result
    else:
        # 如果是对象，尝试转换为字符串
        output = str(result)
    print(f"[DEBUG] 提取的输出: {output}")
    if output:
        # 按行分割，过滤掉空行和隐藏文件
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('.'):
                # 检查是否是目录（通过检查结尾是否有斜杠）
                if line.endswith('/'):
                    line = line[:-1]
                existing_skills.add(line)
    print(f"[DEBUG] 沙箱中已存在的技能: {existing_skills}")
    # 3. 获取本地技能目录
    local_skills = set()
    if os.path.exists(local_skills_path):
        for item in os.listdir(local_skills_path):
            item_path = os.path.join(local_skills_path, item)
            if os.path.isdir(item_path):
                local_skills.add(item)
    print(f"[DEBUG] 本地技能目录: {local_skills}")
    # 4. 计算需要上传的技能（本地有但沙箱中没有的）
    skills_to_upload = local_skills - existing_skills
    print(f"[DEBUG] 需要上传的技能: {skills_to_upload}")
    # 5. 上传缺失的技能
    uploaded_count = 0
    for skill_name in skills_to_upload:
        skill_local_path = os.path.join(local_skills_path, skill_name)
        skill_sandbox_path = f"{sandbox_skills_path}/{skill_name}"
        print(f"[DEBUG] 上传技能: {skill_name}")
        print(f"  本地路径: {skill_local_path}")
        print(f"  沙箱路径: {skill_sandbox_path}")
        # 递归复制整个技能目录
        for root, dirs, files in os.walk(skill_local_path):
            # 计算相对路径
            rel_path = os.path.relpath(root, skill_local_path)
            if rel_path == ".":
                sandbox_dir = skill_sandbox_path
            else:
                sandbox_dir = f"{skill_sandbox_path}/{rel_path.replace(os.sep, '/')}"
            # 在沙箱中创建目录
            if rel_path != ".":  # 主目录已创建
                result = backend.execute(f"mkdir -p {sandbox_dir}")
                if hasattr(result, 'exit_code') and result.exit_code != 0:
                    print(f"[WARNING] 创建目录失败: {sandbox_dir}")
            # 复制文件
            for file in files:
                local_file = os.path.join(root, file)
                if rel_path == ".":
                    sandbox_file = f"{skill_sandbox_path}/{file}"
                else:
                    sandbox_file = f"{skill_sandbox_path}/{rel_path.replace(os.sep, '/')}/{file}"
                # 读取本地文件内容
                try:
                    with open(local_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 上传到沙箱
                    result = backend.upload_files([(sandbox_file, content.encode("utf-8"))])
                    if result:
                        print(f"  ✓ 上传文件: {file}")
                    else:
                        print(f"  ✗ 上传文件失败: {file}")
                except Exception as e:
                    print(f"[ERROR] 读取/上传文件 {local_file} 失败: {e}")
        uploaded_count += 1
        print(f"[DEBUG] 完成上传技能: {skill_name}\n")
    # 6. 验证上传结果
    if uploaded_count > 0:
        print(f"[DEBUG] 验证上传结果...")
        result = backend.execute(f"ls -la {sandbox_skills_path}")
        if hasattr(result, 'stdout'):
            print(f"[DEBUG] 沙箱技能目录内容:\n{result.stdout if result.stdout else '空'}")
        else:
            print(f"[DEBUG] 沙箱技能目录内容: {result}")
    print(f"[DEBUG] 技能同步完成。上传了 {uploaded_count}/{len(skills_to_upload)} 个技能")
    # 返回上传的技能数量
    return uploaded_count
# 配置连接
# 配置连接
config = ConnectionConfigSync(
    domain="http://localhost:8080",
    api_key="your-secret-api-key",
    use_server_proxy=False,
    request_timeout=timedelta(seconds=60),
    transport=httpx.HTTPTransport(limits=httpx.Limits(max_connections=20)),
)
