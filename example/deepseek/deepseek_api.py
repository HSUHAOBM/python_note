from openai import OpenAI

"""
    串接 DeepSeek API
    需申請 API Key
    token 需要費用
    文件 https://api-docs.deepseek.com/zh-cn/
"""


client = OpenAI(api_key={"api_key"},
                base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
