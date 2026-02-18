# 4K Image Batch Converter

A web application to convert multiple images to 4K resolution (3840x2160) with metadata preservation.

## Features

- 🖼️ **Batch Processing** - Convert multiple images at once
- 📥 **Individual Downloads** - Download each converted image separately
- 📊 Preserve and display original image metadata
- 🎨 Modern, responsive UI with drag-and-drop support
- 🐳 Fully Dockerized for easy deployment
- ☁️ **Deploy to Render** - One-click cloud deployment
- ⚡ Fast processing with Pillow
- 📥 Easy upload and download

## Supported Formats

- PNG
- JPG/JPEG
- WEBP
- BMP
- TIFF

## Quick Start

### Using Docker (Recommended)

1. Build and run with docker-compose:
```bash
docker-compose up -d
```

2. Access the application at: http://localhost:5000

### Using Docker directly

1. Build the image:
```bash
docker build -t 4k-image-converter .
```

2. Run the container:
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --name 4k-converter \
  4k-image-converter
```

3. Access at: http://localhost:5000

## Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file and deploy

### Method 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: image-to-4k-converter
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
5. Click "Create Web Service"

### Important Notes for Render Deployment

- The free tier on Render has limited storage
- Uploaded and converted images are stored temporarily
- For production use, consider using object storage (S3, Cloudinary, etc.)
- The service will sleep after 15 minutes of inactivity (free tier)

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access at: http://localhost:5000

## Usage

1. Open the web interface in your browser
2. Click the upload area or drag and drop an image
3. Wait for the conversion to complete
4. View the metadata of original and converted image
5. Download your 4K image

## API Endpoints

- `GET /` - Web interface
- `POST /upload` - Upload and convert image
- `GET /download/<filename>` - Download converted image
- `GET /health` - Health check endpoint

## Configuration

- Max file size: 50MB (configurable in app.py)
- Output format: JPEG with 95% quality
- Target resolution: 3840x2160 (4K)

## Docker Commands

Stop the container:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

Rebuild after changes:
```bash
docker-compose up -d --build
```

## Notes

- RGBA images are automatically converted to RGB
- The application uses LANCZOS resampling for best quality
- Processed images are saved in the `outputs` folder
- Original uploads are automatically cleaned up after processing

## License

MIT
