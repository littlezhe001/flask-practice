import os

from flask import session, jsonify, current_app, send_from_directory, Blueprint
from werkzeug.utils import secure_filename

from app.models import Record_photo, Record_video

preview_bp = Blueprint('preview', __name__)

# 获取图片上传的历史
@preview_bp.route('/GetHistory', methods=['GET'])
def get_history():
    # 检查用户是否登录
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    username = session['username']
    try:
        # 查询该用户的所有上传记录，按时间降序排列
        records = Record_photo.query.filter_by(username=username) \
            .order_by(Record_photo.upload_time.desc()) \
            .all()
        # 构建返回数据
        history_data = []
        for record in records:
            history_data.append({
                'photo_name': record.photo_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                # 'photo_url': f'/photo/{record.photo_name}'  # 假设图片可以通过此URL访问
            })

        return jsonify({
            'success': True,
            'data': history_data,
            'count': len(history_data)
        })

    except Exception as e:
        return jsonify({
            'error': '获取历史记录失败',
            'details': str(e)
        }), 500

@preview_bp.route('/GetHistory_Video', methods=['GET'])
def get_history_video():
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    username = session['username']
    try:
        # 查询该用户的所有上传记录，按时间降序排列
        records = Record_video.query.filter_by(username=username) \
            .order_by(Record_video.upload_time.desc()) \
            .all()
        # 构建返回数据
        history_data = []
        for record in records:
            history_data.append({
                'video_name': record.video_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return jsonify({
            'success': True,
            'data': history_data,
            'count': len(history_data)
        })

    except Exception as e:
        return jsonify({
            'error': '获取历史记录失败',
            'details': str(e)
        }), 500

# 生成图片的url
@preview_bp.route('/uploaded_photos/<filename>')
def server_image(filename):
    # 1. 安全验证文件名
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        return "Invalid filename", 400

    # 2. 获取配置的上传目录路径
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return "Server configuration error", 500

    # 3. 检查文件是否存在
    file_path = os.path.join(upload_folder, safe_filename)
    if not os.path.isfile(file_path):
        return "File not found", 404

    # 4. 返回文件
    return send_from_directory(upload_folder, safe_filename)