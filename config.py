from datetime import timedelta


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)# 设置应用的密钥