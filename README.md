# Video Compression and Quality Analyzer

A comprehensive web application for comparing video compression algorithms (MPEG-2, H.264, HEVC) and analyzing trade-offs between file size, quality, and processing time.

## Features

- Multi-Codec Support: Compare MPEG-2, H.264, and HEVC compression
- Quality Metrics: PSNR, SSIM, and VMAF analysis
- Performance Metrics: Encoding time and decode speed
- BD-Rate Calculations: Industry-standard codec efficiency comparisons
- Interactive Web Interface: Drag & drop upload, results dashboard, charts
- Secure File Uploads and Size Limits
- Export Results: CSV, JSON, and high-resolution charts

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure FFmpeg installed with libx264, libx265, libvmaf support
4. Run the application: `python app.py`
5. Open browser to http://localhost:5000

## Usage

- Upload video clips (MP4, AVI, MOV, MKV)
- Select codecs and quality metrics
- Launch analysis and monitor progress
- View detailed results and export

## License

MIT License

## Program Structure

Recommended runtime structure and responsibilities:

- `app.py`: Flask app factory, routes, background analysis thread, in-memory status store.
- `config.py`: Centralized configuration (folders, timeouts, supported codecs/metrics, env configs).
- `modules/`
  - `video_processor.py`: Encodes videos via FFmpeg per codec/quality, writes `.meta` with encode time.
  - `quality_analyzer.py`: Computes PSNR/SSIM/VMAF using FFmpeg filters and collects bitrate/encode_time.
  - `file_handler.py`: File validation (extension/MIME/header), sanitization, safe path helpers, cleanup.
  - `chart_generator.py`: Generates RD-curves, comparison, and BD-Rate charts to `static/charts`.
- `utils/`
  - `helpers.py`: FFprobe wrappers, formatting helpers, environment checks (ffmpeg/ffprobe/vmaf).
  - `bd_rate.py`: BD-Rate calculator across codecs for VMAF/PSNR/SSIM.
- `Templates/`: Jinja templates (`base.html`, `index.html`).
- `static/`: Frontend assets (`css/`, `js/`, `uploads/`, `results/`, `charts/`).
- `tests/`: Pytest-based tests (unit and integration suggested below).

Suggested next steps for debugging and quality:

1. Environment checks on startup using `utils.helpers.validate_system_requirements()`; surface warnings in UI.
2. Add structured logging (JSON or key-value) for encode/analyze steps and FFmpeg stderr excerpts.
3. Introduce simple job queue cap via `config.MAX_CONCURRENT_JOBS` to throttle background threads.
4. Tests:
   - Unit: `bd_rate.py`, `file_handler.py` (sanitize/validation), helpers parsing.
   - Integration: Small sample clip through `video_processor` + `quality_analyzer` with tiny duration.
5. Export endpoints for CSV/JSON of results and charts download.

Quick start (Windows):

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python app.py
```

