from flask import Blueprint, request, jsonify, render_template
from common import get_db_connection

videolist_bp = Blueprint('videolist', __name__)

@videolist_bp.route('/videolist')
def videolist_page():
    return render_template('videolist.html')

@videolist_bp.route('/get_videos/<int:book_id>')
def get_videos(book_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 基础查询
            sql = """
                SELECT
                    i.id AS image_id,
                    i.paragraph_initial,
                    GROUP_CONCAT(v.video_url ORDER BY v.id SEPARATOR ',') AS video_urls,
                    GROUP_CONCAT(v.video_status ORDER BY v.id SEPARATOR ',') AS video_statuses
                FROM ai_imageslist i
                LEFT JOIN ai_videolist v ON i.id = v.images_id
                WHERE i.book_id = %s
                GROUP BY i.id, i.paragraph_initial
            """
            params = [book_id]
            
            # 获取总数
            count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as t"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']
            
            # 添加分页
            sql += " LIMIT %s OFFSET %s"
            params.extend([per_page, (page - 1) * per_page])
            
            cursor.execute(sql, params)
            result = cursor.fetchall()
            
            return jsonify({
                'data': result,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })
    finally:
        connection.close()

@videolist_bp.route('/update_video_status', methods=['POST'])
def update_video_status():
    data = request.json
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE ai_videolist SET video_status = %s WHERE video_url = %s"
            cursor.execute(sql, (data['value'], data['video_url']))
            connection.commit()
            return jsonify({'status': 'success'})
    finally:
        connection.close()
