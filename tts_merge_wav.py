import os
from pydub import AudioSegment
import numpy as np
from db_connection import get_db_connection

def merge_wav_with_metadata(input_dir, output_file, metadata_file, book_id, silence_duration):
    """
    合并wav文件并生成元数据文件
    
    Args:
        input_dir: 包含wav文件的目录路径
        output_file: 输出合并后的文件路径
        metadata_file: 元数据文件路径（可选）
        book_id: 书单编号
        silence_duration: 文件间添加的静音时长(毫秒)
    """
    # 获取所有wav文件，只读取以book_{book_id}开头的文件
    wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.wav') and f.startswith(f'voice_{book_id}_')]
    wav_files.sort()  # 按文件名排序
    
    if not wav_files:
        print("目录中没有找到wav文件")
        return
    
    print(f"找到 {len(wav_files)} 个wav文件")
    
    # 创建一个空的AudioSegment对象
    combined = AudioSegment.silent(duration=0)
    
    # 记录每个片段的信息
    segments_info = []
    
    # 逐个添加文件
    for i, wav_file in enumerate(wav_files):
        file_path = os.path.join(input_dir, wav_file)
        print(f"正在处理: {wav_file}")
        
        # 加载音频文件
        audio = AudioSegment.from_wav(file_path)

        # 如果不是最后一个文件，添加静音
        if i < len(wav_files) - 1:
            silence = AudioSegment.silent(duration=silence_duration)
            combined += silence            
        
        # 记录片段信息（从文件名中提取ID）
        file_id = int(wav_file.split('_')[-1].split('.')[0])

        # 记录片段信息
        segments_info.append({
            'filename': wav_file,
            'image_id': file_id,
            'start_time': len(combined),
            'duration': len(audio),
            'end_time': len(combined) + len(audio)
        })
        
        # 添加到合并后的音频中
        combined += audio
    
    # 导出合并后的文件
    print(f"正在保存合并后的文件: {output_file}")
    combined.export(output_file, format="wav")
    
    # 如果提供了元数据文件路径，保存元数据
    # if metadata_file:
    #     with open(metadata_file, 'w', encoding='utf-8') as f:
    #         f.write("filename,start_time,duration,end_time\n")
    #         for info in segments_info:
    #             f.write(f"{info['filename']},{info['start_time']},{info['duration']},{info['end_time']}\n")
    
    # 先判断是否已经存在该书单语音的元数据，如果有就删除它们
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询是否存在该book_id的数据
            select_sql = "SELECT id FROM `ai_voicelist` WHERE `book_id` = %s"
            cursor.execute(select_sql, (book_id,))
            result = cursor.fetchone()
            
            # 如果存在数据，则删除
            if result:
                delete_sql = "DELETE FROM `ai_voicelist` WHERE `book_id` = %s"
                cursor.execute(delete_sql, (book_id,))
            
            # 插入到ai_voicelist表
            for info in segments_info:
                sql = "INSERT INTO `ai_voicelist` (`book_id`, `images_id`, `voice_filename`, `start_time`, `duration`, `end_time`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (book_id, info['image_id'], info['filename'], info['start_time'], info['duration'], info['end_time']))
            
            # 插入到ai_voicemerge表
            sql = "INSERT INTO `ai_voicemerge` (`book_id`, `voice_url`) VALUES (%s, %s)"
            cursor.execute(sql, (book_id, output_file))

            # 更新ai_booklist表,更新书单状态为3（已字幕转语音）
            update_sql = "UPDATE `ai_booklist` SET `book_status`='3' WHERE (`id`=%s)"
            cursor.execute(update_sql, (book_id,))
        
            connection.commit()
            connection.close()
            print("数据库记录写入完成!")     
    except Exception as e:
        print(f"数据库写入失败: {str(e)}")
        raise
    
    print("文件合并完成!")
    # if metadata_file:
    #     print(f"元数据已保存到: {metadata_file}")

# if __name__ == "__main__":
#     # 使用示例
#     book_id = 43
#     silence_duration = 300
#     input_directory = "output"  # 替换为你的输入目录
#     output_filename = f"merged_with_metadata_{book_id}.wav"  # 输出文件名
#     segments_info = f"segments_info_{book_id}.csv" # 元数据信息文件


#     # 方法: 合并并生成元数据
#     merge_wav_with_metadata(input_directory, output_filename, segments_info, book_id, silence_duration)
