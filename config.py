# config.py

import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    RESULTS_FOLDER = 'static/results'
    CHARTS_FOLDER = 'static/charts'

    ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
    ALLOWED_MIME_TYPES = {
        'video/mp4', 'video/x-msvideo', 'video/quicktime',
        'video/x-matroska', 'video/x-ms-wmv'
    }

    SUPPORTED_CODECS = {
        'mpeg2': {
            'name': 'MPEG-2',
            'codec': 'mpeg2video',
            'extension': '.mpv',
            'quality_param': '-qscale:v',
            'default_qualities': [2, 4, 6, 8],
            'quality_range': (1, 31)
        },
        'h264': {
            'name': 'H.264/AVC',
            'codec': 'libx264',
            'extension': '.mp4',
            'quality_param': '-crf',
            'default_qualities': [18, 23, 28, 33],
            'quality_range': (0, 51)
        },
        'hevc': {
            'name': 'HEVC/H.265',
            'codec': 'libx265',
            'extension': '.mp4',
            'quality_param': '-crf',
            'default_qualities': [20, 25, 30, 35],
            'quality_range': (0, 51)
        }
    }

    SUPPORTED_METRICS = {
        'psnr': {
            'name': 'PSNR',
            'description': 'Peak Signal-to-Noise Ratio',
            'unit': 'dB',
            'higher_better': True
        },
        'ssim': {
            'name': 'SSIM',
            'description': 'Structural Similarity Index',
            'unit': '',
            'higher_better': True
        },
        'vmaf': {
            'name': 'VMAF',
            'description': 'Video Multimethod Assessment Fusion',
            'unit': '',
            'higher_better': True
        }
    }

    ENCODING_TIMEOUT = 300      # 5 minutes
    ANALYSIS_TIMEOUT = 600      # 10 minutes
    MAX_CONCURRENT_JOBS = 2     # For heavy tasks

    CHART_DPI = 300
    CHART_FORMAT = 'png'
    CHART_STYLE = 'default'

    @staticmethod
    def init_app(app):
        for folder in [Config.UPLOAD_FOLDER, Config.RESULTS_FOLDER, Config.CHARTS_FOLDER]:
            Path(folder).mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod-secret-key'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
