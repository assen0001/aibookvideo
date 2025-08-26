from flask import Flask, jsonify, request
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common import get_db_connection
from tts_create import text_to_speech_multiple
from tts_merge_wav import merge_wav_with_metadata
from datetime import datetime


@app.route('/txt2voice_create', methods=['POST'])
def create_book_tts():
    try:
        # 从POST请求体中获取参数
        data = request.get_json()
        book_id = data.get('book_id')   # 书单编号
        speaker_wav = data.get('speaker_wav', "JackMa_mayun")  # 使用现有音色
        speed = data.get('speed', 1.0)   # 语速
        
        if not book_id:
            return jsonify({"error": "book_id is required"}), 400
        else:
            print(f'book_id is: {book_id}')
        
        # 获取数据库连接
        connection = get_db_connection()
        
        # 执行查询字幕文本
        with connection.cursor() as cursor:
            sql = "SELECT id,paragraph_initial from ai_imageslist WHERE book_id = %s"
            cursor.execute(sql, (book_id,))
            results = cursor.fetchall()
        
        # 提取id和paragraph_initial到数组（二维数据）
        paragraph_array = [
            {'id': row['id'], 'paragraph_initial': row['paragraph_initial']} 
            for row in results if row['paragraph_initial']
        ]
        
        if not paragraph_array:
            return jsonify({"error": "未找到书单内容"}), 404
        else:
            # print(f'paragraph_array is: {paragraph_array}')
            print(f'paragraph_array length is: {len(paragraph_array)}')
                
        output_dir = "static/output"    # 输出目录
        speaker_wav = "speaker/" + speaker_wav + ".mp3"  # 音色文件
        
        # 调用TTS函数
        print('开始生成语音文件...')
        text_to_speech_multiple(
            book_id=book_id,
            texts=paragraph_array,
            speaker_wav=speaker_wav,
            speed=speed,
            output_dir=output_dir
        )
        
        # 合并所有语音文件
        now = datetime.now()
        num = now.strftime("%H%M%S")
        merged_filename = f"{output_dir}/merged_book_{book_id}_{num}.wav"     # 合成的语音文件
        metadata_filename = f"{output_dir}/segments_info_{book_id}_{num}.csv"     # 元数据文件
        
        # 合并语音文件
        print('开始合并语音文件...')
        merge_wav_with_metadata(
            input_dir=output_dir,
            output_file=merged_filename,
            metadata_file=metadata_filename,
            book_id=book_id,
            silence_duration=300    # 段落间隔，注意：须跟N8N中调用comfyui图生视频的时长计算量保持一至
        )
        
        print('合并语音文件完成')
        return jsonify({
            "message": "success",
            "book_id": book_id
            # "total_segments": len(paragraph_array),
            # "output_file": merged_filename,
            # "metadata_file": metadata_filename
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()