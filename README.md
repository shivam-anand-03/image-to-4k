# 4K Image Batch Converter

A web application to convert multiple images to 4K resolution (3840x2160) with metadata preservation.

## Features

- 🖼️ **Batch Processing** - Convert multiple images at once
- 📥 **Individual Downloads** - Download each converted image separately
- � **Download All** - Download all converted images as a single ZIP file
- 🗑️ **Folder Management** - Clear input and output folders with one click
- 📊 Preserve and display original image metadata
- 🎨 Modern, responsive UI with drag-and-drop support
- 🐳 Fully Dockerized for easy deployment
- ☁️ **Deploy to Render** - One-click cloud deployment
- 🖥️ **VM-Ready** - Easy deployment on any virtual machine
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

## Deploy to a Virtual Machine (VM)

### Prerequisites
- A Linux VM (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- SSH access to the VM
- Open port 5000 (or your preferred port)

### Step-by-Step VM Deployment

1. **SSH into your VM:**
```bash
ssh user@your-vm-ip
```

2. **Install Docker and Docker Compose** (if not already installed):
```bash
# Update package list
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

3. **Clone or upload your application:**
```bash
# Option 1: Clone from GitHub
git clone <your-repo-url>
cd image-to-4k

# Option 2: Upload files via SCP
# On your local machine:
# scp -r /home/shivam/Desktop/image-to-4k user@your-vm-ip:~/
```

4. **Deploy with Docker Compose:**
```bash
# Make sure you're in the application directory
cd ~/image-to-4k

# Create necessary directories
mkdir -p uploads outputs input

# Build and start the application
docker-compose up -d --build

# Check if it's running
docker-compose ps
```

5. **Access the application:**
- Open your browser and navigate to: `http://your-vm-ip:5000`
- If using a domain, point your DNS to the VM IP
- For HTTPS, set up a reverse proxy (Nginx) with Let's Encrypt

### Configure Nginx as Reverse Proxy (Optional but Recommended)

1. **Install Nginx:**
```bash
sudo apt-get install nginx -y
```

2. **Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/image-converter
```

3. **Add this configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or use your VM IP

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/image-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Set up SSL with Let's Encrypt (Optional):**
```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Managing the VM Deployment

**View logs:**
```bash
docker-compose logs -f
```

**Stop the application:**
```bash
docker-compose down
```

**Restart the application:**
```bash
docker-compose restart
```

**Update the application:**
```bash
git pull  # If using Git
docker-compose up -d --build
```

**Clear data manually:**
```bash
# Clear outputs
rm -rf outputs/*

# Clear uploads
rm -rf uploads/*

# Clear input
rm -rf input/*
```

**Set up auto-start on boot:**
```bash
# Create a systemd service
sudo nano /etc/systemd/system/image-converter.service
```

Add this content:
```ini
[Unit]
Description=4K Image Converter
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-user/image-to-4k
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=your-user

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable image-converter
sudo systemctl start image-converter
```

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
2. Use the **File Management** panel to:
   - Download all converted images as a ZIP file
   - Clear the input folder
   - Clear the output folder
3. Click the upload area or drag and drop images
4. Wait for the conversion to complete
5. View the metadata of original and converted images
6. Download individual images or use "Download All"

## API Endpoints

- `GET /` - Web interface
- `POST /upload` - Upload and convert images (batch)
- `GET /download/<filename>` - Download a specific converted image
- `GET /download-all` - Download all converted images as ZIP
- `GET /list-outputs` - List all files in output folder
- `POST /clear-input` - Clear all files from input folder
- `POST /clear-output` - Clear all files from output folder
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
