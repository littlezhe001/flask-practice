from flask import Blueprint, request, jsonify, session
from flask_login import login_user
from app import db
from app.models import User  # 假设 User 模型定义在 models.py 中

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 检查必要字段
    if not username or not password:
        return jsonify({'error': '用户名和密码为必填项'}), 400

    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户已存在'}), 409

    # 创建新用户并保存到数据库
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': '注册成功'}), 201


# 登录接口：接收 JSON 格式数据，验证用户后登录
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码为必填项'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)  # 使用 Flask-Login 的 login_user 进行登录
        session.permanent = True  # 启用持久会话，使用 app.config 中的有效期设置
        session['username'] = user.username
        return jsonify({'message': '登录成功'}), 200
    else:
        return jsonify({'error': '用户名或密码错误'}), 401