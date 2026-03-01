from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import os
from werkzeug.utils import secure_filename
import io
from datetime import datetime
import shutil
import zipfile

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
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        tool_name = request.form.get('toolName', '').strip()
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        errors = []
        
        for index, file in enumerate(files, start=1):
            if not allowed_file(file.filename):
                errors.append(f'{file.filename}: Invalid file type')
                continue
            
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:21]  # Include microseconds for uniqueness
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
                
                # Generate output filename based on tool name
                if tool_name:
                    # Use tool name with sequential numbering: toolname_image_001.jpg, toolname_image_002.jpg, etc.
                    safe_tool_name = secure_filename(tool_name).replace(' ', '_')
                    output_filename = f"{safe_tool_name}_image_{index:03d}.jpg"
                else:
                    # Use original behavior with base name
                    base_name = os.path.splitext(filename)[0]
                    output_filename = f"{base_name}_4K_{timestamp}.jpg"
                
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                
                file.save(input_path)
                
                # Process the image
                metadata = resize_to_4k(input_path, output_path)
                
                # Clean up input file
                os.remove(input_path)
                
                results.append({
                    'success': True,
                    'original_name': filename,
                    'filename': output_filename,
                    'index': index,
                    'metadata': {
                        'original_size': f"{metadata['size'][0]}x{metadata['size'][1]}",
                        'new_size': '3840x2160',
                        'original_format': metadata['format'],
                        'original_mode': metadata['mode']
                    }
                })
            
            except Exception as e:
                errors.append(f'{file.filename}: {str(e)}')
        
        return jsonify({
            'results': results,
            'errors': errors,
            'total': len(files),
            'successful': len(results),
            'tool_name': tool_name
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}', 'results': [], 'errors': [str(e)], 'total': 0, 'successful': 0}), 500

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

@app.route('/list-outputs')
def list_outputs():
    """List all files in the output folder"""
    try:
        files = []
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            for filename in os.listdir(app.config['OUTPUT_FOLDER']):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2)
                    })
        return jsonify({'files': files, 'count': len(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-all')
def download_all():
    """Download all output files as a zip"""
    try:
        if not os.path.exists(app.config['OUTPUT_FOLDER']):
            return jsonify({'error': 'Output folder not found'}), 404
        
        files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) 
                if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f))]
        
        if not files:
            return jsonify({'error': 'No files to download'}), 404
        
        # Create zip file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in files:
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                zf.write(file_path, filename)
        
        memory_file.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'4k_images_{timestamp}.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-input', methods=['POST'])
def clear_input():
    """Clear all files from the input folder"""
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return jsonify({'success': True, 'message': 'Input folder cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-output', methods=['POST'])
def clear_output():
    """Clear all files from the output folder"""
    try:
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            for filename in os.listdir(app.config['OUTPUT_FOLDER']):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return jsonify({'success': True, 'message': 'Output folder cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
