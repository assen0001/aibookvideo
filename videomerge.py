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
