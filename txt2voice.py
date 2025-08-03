from flask import Blueprint, request, jsonify, render_template
from common import get_db_connection

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
            UPDATE ai_voicelist 
            SET voider_status = %s 
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
            SELECT id, voider_url, create_time, voider_status
            FROM ai_voicelist
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
            DELETE FROM ai_voicelist 
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
