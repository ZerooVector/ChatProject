import openai
import requests 
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

class ChatManager:
    def __init__(self, api_key, model_name="gpt-3.5-turbo", max_tokens=4096, persona="", max_messages=10):
        self.messages = []
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.set_persona(persona)

    def set_persona(self, persona):
        """Set or change the persona of the model."""
        self.persona = persona
        self.messages = []
        if self.persona:
            self.messages.append({"role": "system", "content": f"You are {self.persona}."})

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
        # Instead of checking token count, we simply limit the number of messages
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_response(self):
        # def get_response(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenAI Python v0.2.4"
        }

        data = {
            "model": self.model_name,
            "messages": self.messages
        }

        url = "https://api.openai.com/v1/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
            return response.json()['choices'][0]['message']['content']
        except requests.Timeout:
            return "AITLE&&||-||"
        except requests.RequestException as e:
            return f"AIERROR||-||"+e


    def clear_messages(self):
        self.messages = []
        if self.persona:
            self.messages.append({"role": "system", "content": f"You are {self.persona}."})

# 使用方式
openai.api_key = "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"  # Replace with your API key

chat_manager = ChatManager(api_key=openai.api_key, persona="如果文本正在陈述某种事实观点，请你回复一个“典！”字；如果文本在明显偏袒某一方、维护某一方的利益，或者在宣传某物，请你回复一个“孝！”字；如果文本中出现了明显急躁、愤怒、消极、烦躁的情感，请你回复一个“急！”字，其余时候，你只需回复“逆天！”。注意：你只需回复上文引号中的几个选项，无需回复多余内容！")

chat_manager.add_message("user", "你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「提瓦特」的幻想世界，在这里，被神选中的人将被授予「神之眼」，导引元素之力。你将扮演一位名为「旅行者」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的同伴们，和他们一起击败强敌，找回失散的亲人——同时，逐步发掘「原神」的真相 ")
response_content = chat_manager.get_response()
chat_manager.add_message("assistant", response_content)

print(response_content)
