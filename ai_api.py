from openai import OpenAI
import json
from mcp_bridge import MCP_File



class aiAgent:
	def __init__(self):
		self.client = OpenAI(
			api_key = "X",
			base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"#base_url = "https://api.moonshot.cn/v1",
		)
		self.content_1 = '''
						你是一个文件管理助手，你现在可以使用这些工具
						{"tools":[{"name":"read_file","description":"Read the complete contents of a file from the file system. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"write_file","description":"Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"edit_file","description":"Make line-based edits to a text file. Each edit replaces exact line sequences with new content. Returns a git-style diff showing the changes made. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"},"edits":{"type":"array","items":{"type":"object","properties":{"oldText":{"type":"string","description":"Text to search for - must match exactly"},"newText":{"type":"string","description":"Text to replace with"}},"required":["oldText","newText"],"additionalProperties":false}},"dryRun":{"type":"boolean","default":false,"description":"Preview changes using git-style diff format"}},"required":["path","edits"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"create_directory","description":"Create a new directory or ensure a directory exists. Can create multiple nested directories in one operation. If the directory already exists, this operation will succeed silently. Perfect for setting up directory structures for projects or ensuring required paths exist. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"list_directory","description":"Get a detailed listing of all files and directories in a specified path. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is essential for understanding directory structure and finding specific files within a directory. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"directory_tree","description":"Get a recursive tree view of files and directories as a JSON structure. Each entry includes 'name', 'type' (file/directory), and 'children' for directories. Files have no children array, while directories always have a children array (which may be empty). The output is formatted with 2-space indentation for readability. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"move_file","description":"Move or rename files and directories. Can move files between directories and rename them in a single operation. If the destination exists, the operation will fail. Works across different directories and can be used for simple renaming within the same directory. Both source and destination must be within allowed directories.","inputSchema":{"type":"object","properties":{"source":{"type":"string"},"destination":{"type":"string"}},"required":["source","destination"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"search_files","description":"Recursively search for files and directories matching a pattern. Searches through all subdirectories from the starting path. The search is case-insensitive and matches partial names. Returns full paths to all matching items. Great for finding files when you don't know their exact location. Only searches within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"},"pattern":{"type":"string"},"excludePatterns":{"type":"array","items":{"type":"string"},"default":[]}},"required":["path","pattern"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"get_file_info","description":"Retrieve detailed metadata about a file or directory. Returns comprehensive information including size, creation time, last modified time, permissions, and type. This tool is perfect for understanding file characteristics without reading the actual content. Only works within allowed directories.","inputSchema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"}},
{"name":"list_allowed_directories","description":"Returns the list of directories that this server is allowed to access. Use this to understand which directories are available before trying to access files.","inputSchema":{"type":"object","properties":{},"required":[]}}]}
						你现在在工作目录'''
		self.content_2 = ''' ，用户接下来会要求做各种不同的文件操作，如果你需要使用这些工具，你必须以json文件格式返回每次的内容，格式如下，注意，多个文件的读取要将文件放在[]列表中传参数：
						{"method":"tools/call", 
						"params":{"name":"","arguments":{}},
						"message":{}
						}
						如果你需要进行文件操作，你必须包含"method":"tools/call"字段，不调用工具则包含"method":"done"，
						"params"是你调用工具时使用的，
						"message"是你返回给用户的信息，不能为空
						你需要在下轮回答中等待工具调用返回的结果，并根据结果，做出相应的调整，并继续任务，直到你认为无法完成或者完成了任务，那么在message中以文本格式包含最终结果，无论如何你的返回都是json格式。
						'''
		self.messages = []
		self.path = "/Users/Eminent/CodeSpace/MCP/test"
		self.mcp_file = MCP_File()


	def set_api_key(self,api_key):
		self.client.api_key = api_key

	def set_base_url(self,baseurl):
		self.client.base_url = baseurl

	def edit_path(self, path):
		self.mcp_file.edit_path(path)
		self.path = path

	def make_messages(self, input: str, n: int = 10) -> list[dict]:
		
		self.messages.append({
			"role": "user",
			"content": input,	
		})
		new_messages = []
		system_messages = [
							{"role": "system", "content": self.content_1 + self.path + self.content_2},
						]
 
		new_messages.extend(system_messages)
		if len(self.messages) > n:
			self.messages = self.messages[-n:]
		new_messages.extend(self.messages)
		return new_messages
	
	def chat(self,input: str) -> str:
		# 携带 messages 与 Kimi 大模型对话
		completion = self.client.chat.completions.create(
			model="deepseek-v3",#"moonshot-v1-8k",
			messages=self.make_messages(input),
			temperature=0.3,
			response_format={"type": "json_object"}
		)
		assistant_message = completion.choices[0].message
		self.messages.append(assistant_message)
		return assistant_message.content
	def chat_with_params(self, input):
		answers = self.chat(input)
		content = json.loads(answers)
		while("method" in content and content["method"] == "tools/call"):
			print("method:", content["method"])
			print("params:", content["params"])
			print("AI要求调用MCP Server")
			print("==============querying mcp server=============================")
			mcp_res = self.mcp_file.go(content["params"])
			print("==============feeding mcp_servers res to AI ==================")
			answers = self.chat(mcp_res)
			content = json.loads(answers)
		print("done")
		print("message:", content["message"])
		return str(content["message"].replace(r"\\n", "\n"))



 





 
 
	
 
 
