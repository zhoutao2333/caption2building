import subprocess

# 定义要运行的命令行命令
command = ['python', 'detect.py', '--save-txt', '--project', 'result', '--name', 'exp']

# 运行命令并捕获输出
result = subprocess.run(command, capture_output=True, text=True)

# 输出命令的标准输出和标准错误输出
print(result.stdout)
print(result.stderr)
