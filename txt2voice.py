from flask import Blueprint, request, jsonify, render_template
from common import get_db_connection
from tts_create import text_to_speech_multiple
from tts_merge_wav import merge_wav_with_metadata
from datetime import datetime

txt2voice_bp = Blueprint('txt2voice', __name__)

@txt2voice_bp.route('/txt2voice')
def txt2voice():
    return render_template('txt2voice.html')

@txt2voice_bp.route('/get_subtitle_content', methods=['GET'])
def get_subtitle_content():
    book_id = request.args.get('book_id')
    if not book_id:
        return jsonify({'error': 'book_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT paragraph_initial
            FROM ai_imageslist
            WHERE book_id = %s
            ORDER BY id
        """, (book_id,))
        results = cursor.fetchall()
        if not results:
            return jsonify({'error': f'找不到book_id={book_id}的内容'}), 404
        paragraphs = [row['paragraph_initial'] for row in results]
        return jsonify({'paragraph_initial': '\\n'.join(paragraphs)})
    except Exception as e:
        print(f"Error fetching subtitle content: {str(e)}")
        print(f"Query parameters: book_id={book_id}")
        return jsonify({
            'error': f"数据库查询失败: {str(e)}",
            'details': f"查询参数: book_id={book_id}"
        }), 500
    finally:
        cursor.close()
        conn.close()

@txt2voice_bp.route('/update_voice_status', methods=['POST'])
def update_voice_status():
    data = request.get_json()
    if not data or 'voice_id' not in data or 'status' not in data:
        return jsonify({'error': '参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ai_voicemerge 
            SET voice_status = %s 
            WHERE id = %s
        """, (data['status'], data['voice_id']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"Error updating voice status: {str(e)}")
        return jsonify({'error': f"更新失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@txt2voice_bp.route('/get_voice_list', methods=['GET'])
def get_voice_list():
    book_id = request.args.get('book_id')
    if not book_id:
        return jsonify({'error': 'book_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, voice_url, create_time, voice_status
            FROM ai_voicemerge
            WHERE book_id = %s
            ORDER BY id DESC
        """, (book_id,))
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        print(f"Error fetching voice list: {str(e)}")
        return jsonify({'error': f"数据库查询失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@txt2voice_bp.route('/delete_voice', methods=['POST'])
def delete_voice():
    data = request.get_json()
    if not data or 'voice_id' not in data:
        return jsonify({'error': 'voice_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM ai_voicemerge 
            WHERE id = %s
        """, (data['voice_id'],))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"Error deleting voice: {str(e)}")
        return jsonify({'error': f"删除失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@txt2voice_bp.route('/txt2voice_create', methods=['POST'])
def create_book_tts():
    try:
        # 从POST请求体中获取参数
        data = request.get_json()
        book_id = data.get('book_id')   # 书单编号
        speaker_wav = data.get('speaker_wav', "LiJing_lj")  # 使用现有音色
        speed = data.get('speed', 1.2)   # 语速
        
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
            print(f'paragraph_array length is: {len(paragraph_array)}')
                
        output_dir = "static/uploads/voice"    # 输出目录
        speaker_wav = "static/speaker/" + speaker_wav + ".mp3"  # 音色文件
        
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
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()
