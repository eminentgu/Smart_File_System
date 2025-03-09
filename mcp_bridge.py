import subprocess
import json
import sys
import time


class MCP_File:
    def __init__(self,path = "/Users/Eminent/CodeSpace/MCP/test"):
        self.path = path
    def run_server(self, command):
        # 启动服务进程
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    def edit_path(self,path):
        self.path = path
    def send_request(self,process, input_data):
        # 将输入数据转换为 JSON 格式
        input_json = json.dumps(input_data) + "\n"
        
        # 向子进程发送输入数据
        process.stdin.write(input_json)
        process.stdin.flush()
        
        # 读取子进程的输出
        output = process.stdout.readline()
        
        # 解析输出
        try:
            output_data = json.loads(output)
            return output_data
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response: {output}", file=sys.stderr)
            return None



    def go(self,params):       
        # 启动服务的命令
        command = [
            "node",
            "/usr/local/lib/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
            self.path
        ]
        
        # 启动服务
        server_process = self.run_server(command)
        time.sleep(1)  # 等待服务启动完成
    
        input_data ={
        "jsonrpc": "2.0",
        "method":"tools/call",
        "params": params,
        "id": 1
        }
    
        result = self.send_request(server_process, input_data)
        
        server_process.terminate()
        
        if result:
            print("Response from server:")
            print(json.dumps(result, indent=2))
            return json.dumps(result, indent=2)
        else:
            #print("No response received from the server.")
            return "server error, No response , report to user please"
        
    
        