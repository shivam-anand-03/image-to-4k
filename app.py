from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import os
from werkzeug.utils import secure_filename
import io
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_to_4k(image_path, output_path):
    """Resize image to exact 4K dimensions (3840x2160) with metadata preservation"""
    img = Image.open(image_path)
    
    # Store original metadata
    metadata = {
        'format': img.format,
        'mode': img.mode,
        'size': img.size,
        'info': img.info.copy()
    }
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img
    elif img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    
    # Resize to exact 4K dimensions
    img_4k = img.resize((3840, 2160), Image.Resampling.LANCZOS)
    
    # Save with optimization
    img_4k.save(output_path, quality=95, optimize=True)
    
    return metadata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, WEBP, BMP, TIFF'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(filename)[0]
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        output_filename = f"{base_name}_4K_{timestamp}.jpg"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        file.save(input_path)
        
        # Process the image
        metadata = resize_to_4k(input_path, output_path)
        
        # Clean up input file
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'metadata': {
                'original_size': f"{metadata['size'][0]}x{metadata['size'][1]}",
                'new_size': '3840x2160',
                'original_format': metadata['format'],
                'original_mode': metadata['mode']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
