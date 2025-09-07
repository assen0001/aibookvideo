import pymysql
import os
from flask import jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库配置
db_config = {
    'ZC_MYSQL_SERVER': os.getenv('ZC_MYSQL_SERVER'),
    'ZC_MYSQL_USERNAME': os.getenv('ZC_MYSQL_USERNAME'),
    'ZC_MYSQL_PASSWORD': os.getenv('ZC_MYSQL_PASSWORD'),
    'ZC_MYSQL_NAME': os.getenv('ZC_MYSQL_NAME'),
    'ZC_MYSQL_PORT': os.getenv('ZC_MYSQL_PORT'),
    'N8N_URL': os.getenv('N8N_URL'),
    'COMFYUI_URL': os.getenv('COMFYUI_URL'),
    'COQUITTS_URL': os.getenv('COQUITTS_URL'),
    'AIBOOKVIDEO_URL': os.getenv('AIBOOKVIDEO_URL')
}



def get_db_connection():
    return pymysql.connect(
        host=db_config['ZC_MYSQL_SERVER'],
        user=db_config['ZC_MYSQL_USERNAME'],
        password=db_config['ZC_MYSQL_PASSWORD'],
        database=db_config['ZC_MYSQL_NAME'],
        port=int(db_config['ZC_MYSQL_PORT']),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_config():
    return jsonify({
        'N8N_URL': db_config.get('N8N_URL'),
        'COMFYUI_URL': db_config.get('COMFYUI_URL'),
        'COQUITTS_URL': db_config.get('COQUITTS_URL'),
        'AIBOOKVIDEO_URL': db_config.get('AIBOOKVIDEO_URL')
    })
