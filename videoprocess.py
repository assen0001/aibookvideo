from moviepy import *
import os

def process_videos(video_urls, title_txt, author_txt, texts, time_data, book_id, audio_url):
    """
    视频合成函数
    
    参数:
    video_urls: 视频文件URL数组
    texts: 字幕文本数组
    time_data: 字幕时间数据数组，包含start_time和duration
    book_id: 书单ID
    audio_url: 音频文件URL
    title_txt: 标题
    author_txt: 作者
    
    返回:
    output_filename：生成后的路径+文件名
    """
    
    # 加载所有视频片段
    clips = []
    for vf in video_urls:
        clips.append(VideoFileClip(vf))
        
    # 合并视频
    final_clip = concatenate_videoclips(clips)

    # 添加标题和作者
    # title_txt = "《望庐山瀑布》"
    # author_txt = "唐 · 李白"

    # 创建标题文本片段
    title_clip = TextClip(
        text=title_txt,
        font="static/font/Alibaba-PuHuiTi-Bold.ttf",
        font_size=34, 
        size=(350,300),
        color='#000000',
        stroke_color='#ffffff',
        stroke_width=2,
        text_align='center',
        method='caption'
    )
    title_clip = (title_clip
                  .with_position(('center', 'top'))  # 水平居中，靠上部
                  .with_start(0.6)  # 开始时间600ms
                  .with_duration(2.2))  # 显示时长1200ms

    # 创建作者文本片段
    author_clip = TextClip(
        text=author_txt,
        font="static/font/Alibaba-PuHuiTi-Bold.ttf",
        font_size=28, 
        size=(350,400),
        color='#000000',
        stroke_color='#ffffff',
        stroke_width=2,
        text_align='center',
        method='caption'
    )
    author_clip = (author_clip
                   .with_position(('center', 'top'))  # 水平居中，靠上部，显示在标题下方
                   .with_start(0.8)  # 开始时间800ms
                   .with_duration(2.0))  # 显示时长1000ms

    # 添加字幕
    subtitle_clips = []
    for i, (text, time_info) in enumerate(zip(texts, time_data)):
        # 将毫秒转换为秒
        start_time_sec = time_info["start_time"] / 1000.0
        duration_sec = time_info["duration"] / 1000.0
        
        txt_clip = TextClip(
            text=text,
            font="static/font/Alibaba-PuHuiTi-Bold.ttf",
            font_size=20, 
            size=(420,150),
            color='#000000',
            stroke_color='#ffffff',
            stroke_width=2,
            text_align='center',
            method='caption'
        )
        
        # 设置字幕位置和时间
        txt_clip = (txt_clip
                   .with_position(('center', 'bottom'))
                   .with_start(start_time_sec)
                   .with_duration(duration_sec))
        
        subtitle_clips.append(txt_clip)
    
    # 组合视频和所有文本元素
    video_with_text = CompositeVideoClip([final_clip, title_clip, author_clip] + subtitle_clips)
    
    # 添加音频
    audio_clip = AudioFileClip(audio_url)
    final_video = video_with_text.with_audio(audio_clip)
    
    # 获取音频时长并限制视频长度
    audio_duration = audio_clip.duration  # 获取音频时长（秒）
    final_video = final_video.with_duration(audio_duration)
    
    # 创建输出目录（如果不存在）
    output_dir = f"static/uploads/videomerge"
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出处理后的视频
    output_filename = f"{output_dir}/video_{book_id}.mp4"
    final_video.write_videofile(output_filename, codec='libx264')
    
    print(f"视频合成完成，保存路径: {output_filename}")
    return output_filename

# # 示例调用（仅在直接运行此文件时执行）
# if __name__ == "__main__":
#     # 这里可以添加测试代码
#     pass


# from videoprocess import process_videos

# # 调用示例：
# get_merge_url = process_videos(
#     video_urls=["url1", "url2", "url3"],
#     texts=["字幕1", "字幕2", "字幕3"],
#     time_data=[{"start_time": 1000, "duration": 2000}, ...],
#     book_id="12345",
#     audio_url="audio_url"
# )




# 调用示例：
# process_videos(
#     video_urls=[
#         "http://47.98.194.143:9008/view?filename=ComfyUI_05765_.mp4",
#         "http://47.98.194.143:9008/view?filename=ComfyUI_05769_.mp4", 
#         "http://47.98.194.143:9008/view?filename=ComfyUI_05771_.mp4"
#     ],
#     texts=[
#     "《冯唐成事心法》是麦肯锡前咨询顾问、作家冯唐推出的职场生存指南",
#     "作为兼具医生、诗人、商业顾问多重身份的斜杠大叔，冯唐这次把曾国藩的处世哲学和现代管理学进行了魔幻混搭，堪称职场打工人自救手册",
#     "全书以知己、知人、知世、知智慧四重境界为框架，像拆解芯片一样剖析了职场进阶的底层逻辑",
#     "最让人眼前一亮的是他提炼的87个方法论"
#     ],
#     time_data=[
#         {"start_time": 400, "duration": 6913},
#         {"start_time": 7712, "duration": 11190},
#         {"start_time": 19302, "duration": 10209},
#         {"start_time": 29511, "duration": 5473}
#     ],
#     book_id="12345",
#     audio_url="http://127.0.0.1:5001/static/output/merged_book_43.wav"
# )
