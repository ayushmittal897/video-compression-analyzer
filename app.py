# app.py

from flask import Flask, render_template, request, jsonify, send_file
import os
from modules.video_processor import VideoProcessor
from modules.quality_analyzer import QualityAnalyzer
from modules.chart_generator import ChartGenerator
from modules.file_handler import FileHandler
from utils.bd_rate import BDRateCalculator
from utils.helpers import get_video_info

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULTS_FOLDER'] = 'static/results'
app.config['CHARTS_FOLDER'] = 'static/charts'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHARTS_FOLDER'], exist_ok=True)

video_processor = VideoProcessor()
quality_analyzer = QualityAnalyzer()
chart_generator = ChartGenerator()
file_handler = FileHandler()
bd_calculator = BDRateCalculator()
processing_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config')
def get_config():
    from config import Config
    return jsonify({
        'supported_codecs': Config.SUPPORTED_CODECS,
        'supported_metrics': Config.SUPPORTED_METRICS,
        'upload_limits': {
            'max_size_mb': Config.MAX_CONTENT_LENGTH // (1024 * 1024)
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    validation = file_handler.validate_video_file(file)
    if not validation['valid']:
        return jsonify({'error': validation['error']}), 400
    filename = file_handler.sanitize_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    video_info = get_video_info(filepath)
    return jsonify({
        'success': True,
        'filename': filename,
        'video_info': video_info
    })

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    data = request.get_json()
    filename = data.get('filename')
    codecs = data.get('codecs', [])
    quality_settings = data.get('quality_settings', {})
    metrics = data.get('metrics', ['psnr', 'ssim', 'vmaf'])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    analysis_id = f"analysis_{filename}"
    processing_status[analysis_id] = {
        'status': 'starting',
        'progress': 0,
        'current_task': 'Initializing...',
        'results': None
    }
    import threading
    threading.Thread(target=run_analysis, args=(analysis_id, filepath, codecs, quality_settings, metrics)).start()
    return jsonify({'success': True, 'analysis_id': analysis_id})

@app.route('/api/status/<analysis_id>')
def get_analysis_status(analysis_id):
    return jsonify(processing_status.get(analysis_id, {'error': 'Not found'}))

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    status = processing_status.get(analysis_id)
    if not status or status['status'] != 'complete':
        return jsonify({'error': 'Analysis not complete'}), 400
    return jsonify(status['results'])

def run_analysis(analysis_id, filepath, codecs, quality_settings, metrics):
    try:
        processing_status[analysis_id]['status'] = 'processing'
        results = {
            'video_info': get_video_info(filepath),
            'codecs': {},
            'bd_rates': {}
        }
        for codec in codecs:
            processing_status[analysis_id]['current_task'] = f'Processing {codec}...'
            qualities = quality_settings.get(codec, [])
            codec_results = []
            for quality in qualities:
                encoded_path = video_processor.encode_video(filepath, codec, quality)
                quality_metrics = quality_analyzer.calculate_metrics(filepath, encoded_path, metrics)
                file_size = os.path.getsize(encoded_path) / (1024 * 1024)
                bitrate = quality_metrics.get('bitrate', 0)
                codec_results.append({
                    'quality': quality,
                    'bitrate': bitrate,
                    'file_size': round(file_size, 2),
                    'psnr': quality_metrics.get('psnr', 0),
                    'ssim': quality_metrics.get('ssim', 0),
                    'vmaf': quality_metrics.get('vmaf', 0),
                    'encode_time': quality_metrics.get('encode_time', 0)
                })
            results['codecs'][codec] = {
                'name': codec.upper(),
                'results': codec_results
            }
        if len(codecs) > 1:
            clist = list(codecs)
            for i in range(len(clist) - 1):
                bd_rates = bd_calculator.calculate_bd_rate(
                    results['codecs'][clist[i]]['results'],
                    results['codecs'][clist[i+1]]['results']
                )
                results['bd_rates'][f"{clist[i+1]}_vs_{clist[i]}"] = bd_rates
        # Generate charts
        processing_status[analysis_id]['current_task'] = 'Generating charts...'
        charts = chart_generator.generate_rd_curves(results, analysis_id)
        results['charts'] = charts
        processing_status[analysis_id]['status'] = 'complete'
        processing_status[analysis_id]['progress'] = 100
        processing_status[analysis_id]['current_task'] = 'Analysis complete!'
        processing_status[analysis_id]['results'] = results
    except Exception as e:
        processing_status[analysis_id]['status'] = 'error'
        processing_status[analysis_id]['error'] = str(e)

if __name__ == '__main__':
    app.run(debug=True)
# End of app.py