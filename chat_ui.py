import tkinter as tk
from tkinter import Frame, Label, Scrollbar
import threading
from ai_api import aiAgent  # 确保 ai_api.py 存在并正确实现 aiAgent

class ChatApplication:
    def __init__(self, master):
        self.master = master
        master.title("基于大模型的智慧文件管理系统")
        master.configure(bg="#FFFFFF")

        self.font = ("Helvetica", 12)
        self.text_color = "#333333"
        self.bg_color = "#FFFFFF"
        self.user_bubble_color = "#DCF8C6"
        self.bot_bubble_color = "#E5E5EA"
        self.button_color = "#007AFF"

        # 创建聊天记录显示区域
        self.chat_history = tk.Canvas(master, bg=self.bg_color, highlightthickness=0)
        self.chat_frame = tk.Frame(self.chat_history, bg=self.bg_color)
        self.scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=self.chat_history.yview)
        self.chat_history.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_history.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", self._on_frame_configure)

        # 创建输入框架
        input_frame = tk.Frame(master, bg=self.bg_color)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        # 输入文本框
        self.user_input = tk.Text(
            input_frame, height=3, font=self.font, wrap=tk.WORD,
            bg="#F8F8F8", fg=self.text_color, relief=tk.FLAT,
            insertbackground=self.text_color
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self._on_enter_pressed)

        # 发送按钮
        self.send_button = tk.Button(
            input_frame, text="Send", command=self.send_message,
            bg=self.button_color, fg="white", font=self.font, relief=tk.FLAT,
            activebackground="#005BBB", cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)

        # 让Bot先说一句话
        self._update_chat_history("Bot", "你好，我是智能文件管理助手，有什么我可以帮忙的吗？\n 输入/set_file 设置文件路径，/set_ai设置需要调用的大模型！", self.bot_bubble_color, "w")
        
        self.aiAgent = aiAgent()  # 初始化 AI 代理

    def _on_frame_configure(self, event):
        """让 Canvas 适应 frame 大小"""
        self.chat_history.configure(scrollregion=self.chat_history.bbox("all"))
        self.chat_history.itemconfig(self.chat_history.create_window((0, 0), window=self.chat_frame, anchor="nw"), width=self.chat_history.winfo_width())

    def _on_enter_pressed(self, event):
        """检测回车键"""
        if not event.state & 0x1:
            self.send_message()
            return "break"
        return None

    def send_message(self):
        """发送用户消息，并使用线程获取 Bot 回复"""
        user_text = self.user_input.get("1.0", tk.END).strip()

        if user_text:
            self.user_input.delete("1.0", tk.END)
            self._update_chat_history("You", user_text, self.user_bubble_color, "e")

            # 启动后台线程处理 AI 回复
            threading.Thread(target=self._get_bot_reply, args=(user_text,), daemon=True).start()

    def _get_bot_reply(self, user_text):
        """后台线程调用 AI 并更新 UI"""
        bot_reply = self.get_bot_reply(user_text)
        self.master.after(0, lambda: self._update_chat_history("Bot", bot_reply, self.bot_bubble_color, "w"))

    def _update_chat_history(self, sender, message, bubble_color, alignment):
        """更新聊天窗口"""
        bubble = Frame(self.chat_frame, bg=bubble_color, padx=10, pady=5)
        Label(bubble, text=message, bg=bubble_color, fg=self.text_color, font=self.font, wraplength=self.chat_history.winfo_width() - 50, justify="left").pack()

        bubble.pack(anchor=alignment, pady=5, padx=10, fill=tk.NONE)
        self.chat_history.update_idletasks()
        self.chat_history.yview_moveto(1.0)

    def get_bot_reply(self, user_message):
        """处理用户指令，或调用 AI 代理获取回复"""
        user_message = user_message.lower()

        if "/set_file" in user_message:
            parts = user_message.split(" ", 1)
            if len(parts) > 1:
                path = parts[1]
                self.aiAgent.edit_path(path)
                return "已设置文件路径为：" + path
            else:
                return "请提供文件路径，如：/set_file 路径"

        elif "/set_ai" in user_message:
            parts = user_message.split(" ")
            if len(parts) >= 3:
                api_key, baseurl = parts[1], parts[2]
                self.aiAgent.set_api_key(api_key)
                self.aiAgent.set_base_url(baseurl)
                return f"已设置\napi_key：{api_key}\nbase_url：{baseurl}"
            else:
                return "请提供 API 相关信息，如：/set_ai API_KEY BASE_URL"

        else:
            return self.aiAgent.chat_with_params(user_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(root)
    root.geometry("500x600")
    root.minsize(400, 300)
    root.mainloop()
