import torch
from TTS.api import TTS
# TTS 在 Ubuntu 18.04 上进行了测试，python >= 3.9， < 3.12..
		
# Get device 用GPU还是CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# List available TTS models 可以看都有些啥模型名字，注意此时模型文件都没有下载
# print(TTS().list_models())
# Init TTS 初始化，传入模型名字，这个路径就得用上面list里的路径，然后下载链接在python安装路径的TTS目录下，这个文件里写的.models.json
# 使用XTTS模型来实现音色转换功能
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
 
# Run TTS运行，必须设置语言
# Text to speech to a file 这是输出到文件了。
tts.tts_to_file(
    text="讲述的是在二十世纪前期的河南农村，一个孤独无助的农民", 
    speaker_wav="speaker/YangLan_yl.mp3", 
    file_path="output_YangLan_yl.wav",
    language="zh",  # 设置语言为中文
    # 添加更多参数来提高质量
    temperature=0.8,  # 温度参数，影响语音的随机性
    length_penalty=1.2,  # 长度惩罚
    repetition_penalty=15.0,  # 重复惩罚
    top_k=50,  # Top-K采样
    top_p=0.8,  # Top-P采样
    speed=1.2  # 语速
    )





    # 中文优化参数
    # temperature=0.6,           # 降低温度值获得更稳定输出
    # length_penalty=1.2,        # 稍微增加长度惩罚
    # repetition_penalty=15.0,   # 增加重复惩罚
    # top_k=30,                  # 减少Top-K值
    # top_p=0.7,                 # 降低Top-P值
    # speed=0.9,                 # 稍微放慢语速
    # enable_text_splitting=True,

## 参数说明
# 1. __temperature__（温度参数）
#    - 范围：0.1-1.0
#    - 值越低，输出越稳定、可预测
#    - 值越高，输出越多样化、创造性
#    - 推荐值：0.6-0.8

# 2. __length_penalty__（长度惩罚）
#    - 范围：0.5-2.0
#    - 值越高，生成的语音越长
#    - 值越低，生成的语音越短
#    - 推荐值：1.0-1.2

# 3. __repetition_penalty__（重复惩罚）
#    - 范围：5.0-20.0
#    - 值越高，减少重复输出
#    - 推荐值：10.0-15.0

# 4. __top_k__（Top-K采样）
#    - 范围：20-100
#    - 值越低，输出越确定
#    - 值越高，输出越多样化
#    - 推荐值：30-50

# 5. __top_p__（Top-P采样）
#    - 范围：0.5-0.95
#    - 值越低，输出越确定
#    - 值越高，输出越多样化
#    - 推荐值：0.7-0.8

# 6. __speed__（语速）
#    - 范围：0.5-2.0
#    - 值越低，语音越慢
#    - 值越高，语音越快
#    - 推荐值：0.8-1.0

# ## 进一步优化建议
# 1. __使用更高质量的参考音频__
#    - 确保参考音频清晰、无噪音
#    - 音频时长建议在5-15秒之间
#    - 选择与目标语音语调相似的音频

# 2. __调整文本内容__
#    - 适当分段，避免过长句子
#    - 使用更自然的中文表达方式
