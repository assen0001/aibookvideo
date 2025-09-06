import requests
import tempfile
import os
from moviepy import *
from datetime import datetime


def download_file(url, file_type="video"):
    """
    下载文件到临时目录
    
    参数:
    url: 文件URL地址
    file_type: 文件类型（video/audio），用于日志显示
    
    返回:
    local_path: 下载到本地的临时文件路径
    """
    try:
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        
        # 从URL中提取文件名
        if 'filename=' in url:
            filename = os.path.basename(url.split('filename=')[-1])
        else:
            # 对于音频文件，从路径中提取文件名
            filename = os.path.basename(url)
            if '?' in filename:
                filename = filename.split('?')[0]
        
        local_path = os.path.join(temp_dir, filename)
        
        # 下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"{file_type}文件下载完成: {url} -> {local_path}")
        return local_path
        
    except Exception as e:
        print(f"{file_type}文件下载失败 {url}: {str(e)}")
        raise


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
    print("加载视频片段...")
    clips = []
    local_paths = []  # 保存本地文件路径用于后续清理
    
    for vf in video_urls:
        try:
            # 先下载视频到本地
            local_path = download_file(vf, "视频")
            local_paths.append(local_path)
            
            # 加载本地视频文件
            clips.append(VideoFileClip(local_path))
            print(f"已加载视频片段: {local_path}")
            
        except Exception as e:
            print(f"加载视频失败 {vf}: {str(e)}")
            raise
    
    print(f"已加载视频片段：{len(clips)}")
    
    # 合并视频
    final_clip = concatenate_videoclips(clips)

    # 创建标题文本片段（带滑入动画）
    title_clip = TextClip(
        text=title_txt,
        font="static/font/Alibaba-PuHuiTi-Bold.ttf",
        font_size=42, 
        size=(480,300),
        color='#FFB600',
        # bg_color='red',
        stroke_color='#000000',
        stroke_width=2,
        text_align='center',
        method='caption'
    )
    
    # 定义标题滑入动画函数
    def title_position(t):
        # 动画持续时间（秒）
        anim_duration = 0.3
        
        if t < anim_duration:
            # 从底部开始向上滑动
            start_y = 50  # 初始位置（方框底部）
            end_y = 0      # 结束位置（方框顶部）
            progress = t / anim_duration  # 动画进度（0到1）
            current_y = start_y - (start_y - end_y) * progress
            return ('center', current_y)
        else:
            # 动画结束后保持在顶部位置
            return ('center', 0)
    
    title_clip = (title_clip
                  .with_position(title_position)  # 应用动画函数
                  .with_start(0.6)  # 开始时间600ms
                  .with_duration(2.2))  # 显示时长2.2秒

    # 创建作者文本片段
    author_clip = TextClip(
        text=author_txt,
        font="static/font/Alibaba-PuHuiTi-Bold.ttf",
        font_size=30, 
        size=(300,450),  
        color='#FFB600',
        # bg_color='#eeeeee',
        stroke_color='#000000',
        stroke_width=2,
        text_align='center',
        method='caption'
    )
    author_clip = (author_clip
                   .with_position(title_position)  # 应用动画函数
                   .with_start(0.8)  # 开始时间800ms
                   .with_duration(2.0))  # 显示时长2.0秒

    # 添加字幕
    subtitle_clips = []
    for i, (text, time_info) in enumerate(zip(texts, time_data)):
        # 将毫秒转换为秒
        start_time_sec = time_info["start_time"] / 1000.0
        duration_sec = time_info["duration"] / 1000.0
        
        txt_clip = TextClip(
            text=text,
            font="static/font/Alibaba-PuHuiTi-Medium.ttf",
            font_size=21, 
            size=(420,160),
            color='#FFB600',
            stroke_color='#000000',
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
    try:
        # 先下载音频文件到本地
        audio_local_path = download_file(audio_url, "音频")
        local_paths.append(audio_local_path)
        
        # 加载本地音频文件
        audio_clip = AudioFileClip(audio_local_path)
        final_video = video_with_text.with_audio(audio_clip)
        print(f"已加载音频文件: {audio_local_path}")
        
    except Exception as e:
        print(f"加载音频失败 {audio_url}: {str(e)}")
        raise
    
    # 获取音频时长并限制视频长度
    audio_duration = audio_clip.duration  # 获取音频时长（秒）
    final_video = final_video.with_duration(audio_duration)

    
    # 创建输出目录（如果不存在）
    output_dir = f"static/uploads/videomerge"
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出处理后的视频
    now = datetime.now()
    num = now.strftime("%H%M%S")
    output_filename = f"{output_dir}/video_{book_id}_{num}.mp4"
    final_video = final_video.with_effects([vfx.Resize((1080, 1440))])  # 使用with_effects应用缩放
    final_video.write_videofile(output_filename, 
                              codec='libx264',
                              ffmpeg_params=['-vf', 'scale=1080:1440'])  # 添加缩放滤镜

    # 在函数最后添加清理代码
    try:
        # 删除临时下载的文件
        for local_path in local_paths:
            if os.path.exists(local_path):
                os.remove(local_path)
                print(f"已清理临时文件: {local_path}")
    except Exception as e:
        print(f"清理临时文件时出错: {str(e)}")
    
    print(f"视频合成完成，保存路径: {output_filename}")
    return output_filename



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
#         "http://47.98.194.143:9008/view?filename=ComfyUI_05769_.mp4"
#     ],
#     texts=[
#     "《冯唐成事心法》是麦肯锡前咨询顾问、作家冯唐推出的职场生存指南",
#     "作为兼具医生、诗人、商业顾问多重身份的斜杠大叔"
#     ],
#     time_data=[
#         {"start_time": 400, "duration": 6913},
#         {"start_time": 7712, "duration": 8190}
#     ],
#     book_id="12345",
#     audio_url="http://127.0.0.1:5001/static/output/voice_52_1309.wav",
#     title_txt="《望庐山瀑布》",
#     author_txt="唐 · 李白"
# )

