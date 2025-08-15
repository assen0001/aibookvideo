from flask import Blueprint, render_template, request, jsonify
from common import get_db_connection

autovideo_bp = Blueprint('autovideo', __name__)

@autovideo_bp.route('/autovideo')
def autovideo_page():
    return render_template('autovideo.html')

@autovideo_bp.route('/autovideo/create', methods=['POST'])
def create_autovideo():
    data = request.json
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 插入数据到ai_booklist表
            sql = """INSERT INTO ai_booklist 
                    (book_name, book_author, book_note, book_supplement_prompt, sdxl_prompt_styler)
                    VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                data['book_name'],
                data['book_author'],
                data['book_note'],
                data['book_supplement_prompt'],
                data.get('sdxl_prompt_styler', '')
            ))
            connection.commit()
            
            # 获取自增ID
            book_id = cursor.lastrowid
            
            return jsonify({'status': 'success', 'book_id': book_id})
    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        connection.close()
