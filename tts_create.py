import torch
from TTS.api import TTS
import os

def text_to_speech_multiple(book_id, texts, speaker_wav, speed, output_dir):
    """
    将多行文本转换为语音文件
    
    Args:
        book_id: 书单编号 
        texts: 文本列表，二维数据（id,paragraph_initial）
        speaker_wav: 演示音频文件路径
        speed: 语速
        output_dir: 输出目录
    """

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # Get device 用GPU还是CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Init TTS 初始化，使用XTTS模型来实现音色转换功能
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
        
    for i, text_data in enumerate(texts, 1):
        if text_data['paragraph_initial'].strip():  # 如果文本不为空
            # 生成文件名，使用id编号
            file_path = f"{output_dir}/voice_{book_id}_{text_data['id']:03d}.wav"
            
            # Run TTS运行，必须设置语言
            tts.tts_to_file(
                text=text_data['paragraph_initial'], 
                speaker_wav=speaker_wav, 
                file_path=file_path,
                language="zh",  # 设置语言为中文
                # 添加更多参数来提高质量
                temperature=0.7,  # 温度参数，影响语音的随机性
                length_penalty=1.0,  # 长度惩罚
                repetition_penalty=10.0,  # 重复惩罚
                top_k=50,  # Top-K采样
                top_p=0.8,  # Top-P采样
                speed=float(speed)  # 语速
            )
            print(f"已生成: {file_path}")

# # 要转换的文本内容
# texts = [
#     "我记得那天，广陵的烟花格外娇艳",
#     "三月的天气也暖洋洋的",
#     "我送别了好友孟浩然，他要去遥远的江南了，望着他乘坐的孤帆渐渐消失在碧空之下",
#     "我的心情啊，也如同这长江水般奔流不息，思路万千",
#     "“故人西辞黄鹤楼”，第一句我琢磨了许久"
# ]
# speaker_wav="speaker/JackMa_mayun.mp3"
# output_dir="static/output"
# book_id=43

# # 调用函数，将文本转换为语音
# text_to_speech_multiple(book_id, texts, speaker_wav, output_dir)
