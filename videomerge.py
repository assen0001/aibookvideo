from flask import Blueprint, request, jsonify, render_template
from common import get_db_connection
from videoprocess import process_videos

videomerge_bp = Blueprint('videomerge', __name__)

@videomerge_bp.route('/videomerge')
def videomerge():
    return render_template('videomerge.html')

@videomerge_bp.route('/get_video_list', methods=['GET'])
def get_video_list():
    book_id = request.args.get('book_id')
    if not book_id:
        return jsonify({'error': 'book_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, videomerge_url, bilibili_url, create_time
            FROM ai_videomerge
            WHERE book_id = %s
            ORDER BY id DESC
        """, (book_id,))
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        print(f"Error fetching video list: {str(e)}")
        return jsonify({'error': f"数据库查询失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@videomerge_bp.route('/delete_video', methods=['POST'])
def delete_video():
    data = request.get_json()
    if not data or 'video_id' not in data:
        return jsonify({'error': 'video_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM ai_videomerge 
            WHERE id = %s
        """, (data['video_id'],))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"Error deleting video: {str(e)}")
        return jsonify({'error': f"删除失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@videomerge_bp.route('/create_video', methods=['POST'])
def create_video():
    data = request.get_json()
    if not data or 'book_id' not in data:
        return jsonify({'error': 'book_id参数缺失'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 查询分镜视频
        cursor.execute("""
            SELECT video_url FROM ai_videolist WHERE book_id = %s and video_status = 1
        """, (data['book_id'],))
        video_rows = cursor.fetchall()
        video_urls = []
        for row in video_rows:
            if row and len(row) > 0:
                video_urls.append(f"http://47.98.194.143:9008/view?filename={row['video_url']}")
        
        # 查询字幕
        cursor.execute("""
            SELECT paragraph_initial FROM ai_imageslist WHERE book_id = %s
        """, (data['book_id'],))
        texts = []
        for row in cursor._rows:
            if row and len(row) > 0:
                texts.append(row['paragraph_initial'])
        
        # 查询字幕元数据
        cursor.execute("""
            SELECT start_time, duration FROM ai_voicelist WHERE book_id = %s
        """, (data['book_id'],))
        time_data = []
        for row in cursor._rows:
            if row and len(row) > 1:
                time_data.append({"start_time": row['start_time'], "duration": row['duration']})
        
        # 查询语音文件
        cursor.execute("""
            SELECT a.book_name, a.book_author, b.voice_url 
            FROM ai_booklist a LEFT JOIN ai_voicemerge b on a.id = b.book_id
            WHERE a.id = %s and b.voice_status = 1
        """, (data['book_id'],))
        voice_row = cursor._rows
        audio_url = f"http://192.168.1.101:5001/{voice_row[0]['voice_url']}"
        title_txt = voice_row[0]['book_name']
        author_txt = voice_row[0]['book_author']
        
        # 调用视频合成函数
        merge_url = process_videos(
            video_urls=video_urls, 
            title_txt=title_txt,
            author_txt=author_txt, 
            texts=texts,
            time_data=time_data,
            book_id=data['book_id'],
            audio_url=audio_url
        )
        
        # 保存结果到数据库
        cursor.execute("""
            INSERT INTO ai_videomerge (book_id, videomerge_url)
            VALUES (%s, %s)
        """, (data['book_id'], merge_url))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"Error creating video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"视频合成失败: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    