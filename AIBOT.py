from google import genai
import yaml
import os
# from RAG import The_RAG_Process

CONFIG_FILE = 'config.yaml'

with open(CONFIG_FILE, 'r') as config_file:
    config = yaml.load(config_file,Loader=yaml.FullLoader)

model = "gemini-2.0-flash"
client = genai.Client(api_key=config['gemini']['api_key'])

knowledge_file_path="knowledge_base"

def is_kb_empty(file_path):
    return os.stat(file_path).st_size == 0


#这段是没有kb的时候用RAG，可能和zhipu的逻辑不一样
# def get_zhipuai_response(prompt):
#     """根据是否有 knowledge_base 来决定是否使用 RAG 处理"""
    
#     knowledge_base_path = "knowledge_base"

#     # **检查知识库是否为空**
#     if os.path.exists(knowledge_base_path) and os.listdir(knowledge_base_path):
#         print("知识库不为空，使用 RAG 处理用户问题。")
#         prompt = The_RAG_Process(prompt)  # **使用 RAG 处理 prompt**
#     else:
#         print("知识库为空，直接用 LLM 生成回答。")

#     # 让 ZhipuAI 处理问题
#     messages = [
#         {"role": "system", "content": "You are a chatbot."},
#         {"role": "user", "content": prompt}
#     ]

#     response = client.chat.completions.create(
#         model="glm-4-0520",
#         messages=messages
#     )

#     return response.choices[0].message.content




def get_response(prompt):

    # if is_kb_empty(knowledge_file_path):
    #     prompt=The_RAG_Process(prompt)

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    try:
        answer = response.text
    except:
        answer = "System Error."

    return answer

