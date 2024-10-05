import requests
import json
import logging

# 初始化日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

API_KEY = "sk-BMaZPSlnDQpcwNAbMFe2xYrRMyej6I3WpzVeiFhOGgjgz9HL"  # 替换为你的API Key

# 检查API支持的模型列表
def list_supported_models(api_url, apikey):
    headers = {
        "Authorization": "Bearer " + apikey
    }
    url = f"{api_url}/v1/models"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # 返回所有可用模型的列表
    else:
        return f"请求失败，状态码：{response.status_code}"

# 从ChatGPT API获取流式回复
def get_response_stream_generate_from_ChatGPT_API(api_url, message_context, apikey, 
                                                  model="gpt-4-gizmo-g-dJgHhfRqQ", temperature=0.9, 
                                                  presence_penalty=0, max_tokens=2000):
    """
    从ChatGPT API获取流式回复
    :param api_url: API地址
    :param message_context: 上下文
    :param apikey: API Key
    :param model: 使用的模型
    :param temperature: 温度
    :param presence_penalty: 惩罚系数
    :param max_tokens: 最大token数量
    :return: 流式回复生成器
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + apikey
    }

    data = {
        "model": model,
        "temperature": temperature,
        "presence_penalty": presence_penalty,
        "max_tokens": max_tokens,
        "messages": message_context,
        "stream": True
    }

    logger.info("开始流式请求")
    logger.info(f"使用的模型: {model}")

    try:
        # 发送POST请求到自定义的API地址
        response = requests.request("POST", api_url, headers=headers, json=data, stream=True)

        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}, 内容：{response.text}")
            return None

        def generate():
            for line in response.iter_lines():
                if line:
                    # 将流中的数据解析为JSON
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data:"):
                        if line_str.strip() == "data: [DONE]":
                            break
                        line_json = json.loads(line_str[5:])
                        if "choices" in line_json and len(line_json["choices"]) > 0:
                            delta = line_json["choices"][0]["delta"]
                            if "content" in delta:
                                print(delta["content"], end="")
                                yield delta["content"]

        return generate()

    except Exception as e:
        logger.error(f"请求过程中出错：{str(e)}")
        return None

# 测试函数
def test_api():
    api_url = "https://api.gptgod.online/v1/chat/completions"  # 替换为你的API地址
    message_context = [{"role": "user", "content": "Hello, can you generate a test response?"}]
    
    # 调用获取流式数据的函数
    response_generator = get_response_stream_generate_from_ChatGPT_API(api_url, message_context, API_KEY)

    if response_generator:
        for content in response_generator:
            print(content)
    else:
        print("请求失败或未返回数据")

# 检查API支持的模型
def check_models():
    api_url = "https://api.gptgod.online"  # 替换为你的API地址
    models = list_supported_models(api_url, API_KEY)
    print("支持的模型列表:")
    print(models)

if __name__ == "__main__":
    # 选择测试内容：测试API请求 或 检查支持的模型
    test_api()  # 调用API进行测试
    # check_models()  # 检查支持的模型
