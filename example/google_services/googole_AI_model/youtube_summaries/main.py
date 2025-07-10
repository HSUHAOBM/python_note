from google import genai
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
import json

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()


def get_prompt(prompt_type):
    prompts = {
        "transcript": """You must perform a full, complete transcription of the video/audio.
        Include every spoken word, without summarizing, condensing, paraphrasing, or omitting any dialogue.
        Preserve the natural speech, including pauses, repetitions, filler words (e.g., "um," "uh," "you know").
        Do not add timestamps, do not add any description, explanation, or interpretation.
        Only output the plain text of the spoken content, from start to end, in exact order.""",
        "timestamps": "Generate a timestamped transcript of the video. Each line must follow this format: [hh:mm:ss] Dialogue. Return only timestamp + dialogue.",
        "summary": "Provide a concise summary of the main points in nested bullets, using quotes only when absolutely essential for clarity.",
        "scene": """Please provide a detailed description of the scene in the video, including:
        - Setting
        - Objects
        - People
        - Lighting
        - Colors
        - Camera Angle/Movement
        Start output directly with the response.""",
        "clips": """Extract shareable clips for social media:
        - Timestamp: [hh:mm:ss]-[hh:mm:ss]
        - Transcript: Verbatim text
        - Rationale: Why this clip is engaging (20 words max).
        Start output directly with the response."""
    }
    return prompts.get(prompt_type, "Provide a concise summary of the main points.")


def save_to_file(answer_text, filename="output.txt"):
    os.makedirs("output", exist_ok=True)
    file_path = os.path.join("output", filename)
    logging.info("開始儲存檔案...")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(answer_text)
    logging.info(f"✅ AI 回答已儲存到：{file_path}")


def send_request(api_key, input_mode, input_path, prompt_type):
    try:
        logging.info("初始化 Google GenAI 客戶端...")
        client = genai.Client(api_key=api_key)

        logging.info("準備生成提示文字...")
        prompt = get_prompt(prompt_type)

        if input_mode == "youtube":
            logging.info("處理 YouTube 影片連結...")
            contents = f"Analyze the following YouTube video: {input_path}. {prompt} Based on the language spoken in the video."
        elif input_mode == "audio":
            contents = f"{prompt} Based on the language spoken in the audio."
        else:
            raise ValueError("input_mode 只能是 'youtube' 或 'audio'")

        logging.info("發送請求至 Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{
                "parts": [
                    {"text": prompt},
                    {"file_data": {"file_uri": input_path}}
                ]
            }]
        )

        logging.info("成功接收到 API 回應！")
        # 確保 response 是 GenerateContentResponse 類型
        candidates = response.candidates if hasattr(
            response, 'candidates') else []
        usage = response.usage_metadata if hasattr(
            response, 'usage_metadata') else {}

        answer_text = candidates[0].content.parts[0].text if candidates else "No Answer"

        logging.info("=== 資訊 ===")
        logging.info(f"usageMetadata: {usage}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prompt_type}_{timestamp}.txt"
        save_to_file(answer_text, filename)

    except Exception as e:
        logging.exception(f"發生錯誤: {e}")


if __name__ == '__main__':
    api_key = os.getenv("API_KEY")

    # 這裡選擇要使用的模式
    # youtube: 使用 YouTube 網址
    # audio: 使用本地音檔
    input_mode = "youtube"

    # 路徑
    input_path = "https://www.youtube.com/watch?v=8iPubWDcqdU"
    # input_path = "audio/sample.wav"

    # 這裡可以選擇你想要的 prompt 類型
    prompt_type = "transcript"  # transcript / timestamps / summary / scene / clips
    # transcript = 純逐字稿
    # timestamps = 有時間標記的逐字稿
    # summary = 摘要
    # scene = 場景描述
    # clips = 社群短片

    try:
        logging.info("程式開始執行...")
        send_request(api_key, input_mode, input_path, prompt_type)
        logging.info("程式執行完成！")
    except Exception as e:
        logging.error(f"發生錯誤: {e}")
