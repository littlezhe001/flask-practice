import os
from datetime import datetime

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename

from app import db
from app.models import Record_photo, Record_video

upload_bp = Blueprint('upload', __name__)

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav' }
UPLOAD_FOLDER = r"E:\毕业设计\flask\photo"
UPLOAD_FOLDER_VIDEO = r"E:\毕业设计\flask\video"

def Allow_File(filename, allowed_extension) :
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extension
# 上传图片的api（已完成）
@upload_bp.route('/UploadPhoto', methods=['POST'])
def upload_photo():
    file = request.files['PhotoFile']
    if not Allow_File(file.filename, ALLOWED_PHOTO_EXTENSIONS):
        return jsonify({'error': 'Invalid file type'}), 400
    savedir_path = UPLOAD_FOLDER
    file_name = f'{secure_filename(file.filename)}'
    save_path = os.path.join(savedir_path, file_name)

    file.save(save_path)
    username = session['username']
    new_record = Record_photo(
        username = username,
        photo_name = file_name,
        upload_time = datetime.now()
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'File uploaded!',
        'filename': file_name,
    }), 200


@upload_bp.route('/UploadVideo', methods=['POST'])
def upload_video():
    file = request.files['VideoFile']
    if not Allow_File(file.filename, ALLOWED_VIDEO_EXTENSIONS) :
        return jsonify({'error': 'Invalid file type'}), 400
    savedir_path = UPLOAD_FOLDER_VIDEO
    file_name = f'{secure_filename(file.filename)}'
    save_path = os.path.join(savedir_path, file_name)
    file.save(save_path)

    username = session['username']
    new_record = Record_video(
        username = username,
        video_name = file_name,
        upload_time = datetime.now()
    )

    db.session.add(new_record)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'File uploaded!',
        'filename': file_name,
    }), 200