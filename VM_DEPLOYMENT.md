# Virtual Machine Deployment Guide

Complete guide to deploy the 4K Image Converter on a Virtual Machine.

## Prerequisites

- A Linux VM (Ubuntu 20.04+, Debian, or CentOS)
- Root or sudo access
- Minimum 1GB RAM, 1 CPU core
- At least 10GB free disk space
- Internet connection
- Open port 5000 (or your preferred port)

## Quick Start

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin -y

# Clone the repository
git clone <your-repo-url>
cd image-to-4k

# Start the application
docker-compose up -d

# Access at http://your-vm-ip:5000
```

## Detailed Setup

### 1. Prepare Your VM

**Update system packages:**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Install required tools:**
```bash
sudo apt-get install -y curl git nano
```

### 2. Install Docker

**Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Add your user to docker group** (optional, to avoid using sudo):
```bash
sudo usermod -aG docker $USER
```
*Note: Log out and log back in for this to take effect*

**Verify installation:**
```bash
docker --version
```

### 3. Install Docker Compose

**Install Docker Compose:**
```bash
sudo apt-get install docker-compose-plugin -y
```

**Verify installation:**
```bash
docker compose version
```

### 4. Deploy the Application

**Clone the repository:**
```bash
cd ~
git clone <your-repo-url>
cd image-to-4k
```

**Or upload files manually:**
```bash
# On your local machine:
scp -r /path/to/image-to-4k user@your-vm-ip:~/
```

**Create necessary directories:**
```bash
mkdir -p uploads outputs input
```

**Start the application:**
```bash
docker-compose up -d --build
```

**Check if it's running:**
```bash
docker-compose ps
docker-compose logs
```

### 5. Access the Application

Open your browser and navigate to:
```
http://your-vm-ip:5000
```

## Production Setup with Nginx

For production environments, use Nginx as a reverse proxy.

### Install Nginx

```bash
sudo apt-get install nginx -y
```

### Configure Nginx

**Create configuration file:**
```bash
sudo nano /etc/nginx/sites-available/image-converter
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or VM IP

    # Allow larger file uploads
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for large file uploads
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/image-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Set up SSL/HTTPS (Recommended)

**Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx -y
```

**Get SSL certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

**Auto-renewal is configured automatically!**

**Verify auto-renewal:**
```bash
sudo certbot renew --dry-run
```

## Firewall Configuration

### UFW (Ubuntu/Debian)

```bash
# Install UFW
sudo apt-get install ufw -y

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If not using Nginx, allow port 5000
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Firewalld (CentOS/RHEL)

```bash
# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# If not using Nginx
sudo firewall-cmd --permanent --add-port=5000/tcp

# Reload firewall
sudo firewall-cmd --reload
```

## Auto-Start on Boot

Create a systemd service to automatically start the application on boot.

**Create service file:**
```bash
sudo nano /etc/systemd/system/image-converter.service
```

**Add this content:**
```ini
[Unit]
Description=4K Image Converter
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-user/image-to-4k
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=your-user

[Install]
WantedBy=multi-user.target
```

**Replace `your-user` with your actual username!**

**Enable and start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable image-converter
sudo systemctl start image-converter
```

**Check service status:**
```bash
sudo systemctl status image-converter
```

## Management Commands

### Application Management

**View logs:**
```bash
docker-compose logs -f
```

**Stop the application:**
```bash
docker-compose down
```

**Start the application:**
```bash
docker-compose up -d
```

**Restart the application:**
```bash
docker-compose restart
```

**Rebuild and restart:**
```bash
docker-compose up -d --build
```

**Update from Git:**
```bash
git pull
docker-compose up -d --build
```

### Data Management

**Clear output files:**
```bash
rm -rf outputs/*
```

**Clear uploaded files:**
```bash
rm -rf uploads/*
```

**Clear input files:**
```bash
rm -rf input/*
```

**Clear all data:**
```bash
rm -rf outputs/* uploads/* input/*
```

**Check disk usage:**
```bash
du -sh outputs/ uploads/ input/
```

### System Monitoring

**Check Docker containers:**
```bash
docker ps
docker stats
```

**Check disk space:**
```bash
df -h
```

**Check memory usage:**
```bash
free -h
```

**Check logs:**
```bash
# Application logs
docker-compose logs -f --tail=100

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u image-converter -f
```

## Performance Optimization

### Increase Worker Processes

Edit `docker-compose.yml` or `Dockerfile` to increase Gunicorn workers:

```yaml
environment:
  - GUNICORN_WORKERS=8  # Adjust based on CPU cores
```

Or modify the Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "120", "app:app"]
```

### Set Up Swap (for low RAM VMs)

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make it permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Enable Gzip Compression in Nginx

Add to your Nginx config:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## Backup and Restore

### Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup outputs
tar -czf ~/backups/outputs-$(date +%Y%m%d).tar.gz outputs/

# Backup entire application
tar -czf ~/backups/image-to-4k-$(date +%Y%m%d).tar.gz ~/image-to-4k
```

### Restore

```bash
# Restore outputs
tar -xzf ~/backups/outputs-20240219.tar.gz -C ~/image-to-4k/
```

### Automated Backups

Create a cron job:
```bash
crontab -e
```

Add this line to backup daily at 2 AM:
```cron
0 2 * * * tar -czf ~/backups/outputs-$(date +\%Y\%m\%d).tar.gz ~/image-to-4k/outputs/
```

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs

# Check if port is already in use
sudo netstat -tulpn | grep 5000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clear Docker cache
docker system prune -a

# Clear old images
docker image prune -a
```

### Permission issues

```bash
# Fix directory permissions
sudo chown -R $USER:$USER ~/image-to-4k
chmod -R 755 ~/image-to-4k
```

### Nginx errors

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

## Security Best Practices

1. **Keep system updated:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Use SSH keys instead of passwords**

3. **Change default SSH port:**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change Port 22 to something else
   sudo systemctl restart ssh
   ```

4. **Install fail2ban:**
   ```bash
   sudo apt-get install fail2ban -y
   sudo systemctl enable fail2ban
   ```

5. **Set up automatic security updates:**
   ```bash
   sudo apt-get install unattended-upgrades -y
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

6. **Limit file upload sizes** - Already configured to 50MB

7. **Use HTTPS** - Follow the SSL setup above

## Cost Estimates

### Cloud Provider Pricing (Approximate)

- **DigitalOcean**: $6/month (1GB RAM, 1 CPU)
- **AWS EC2**: $8-10/month (t3.micro)
- **Google Cloud**: $7-10/month (e2-micro)
- **Linode**: $5/month (1GB RAM, 1 CPU)
- **Vultr**: $6/month (1GB RAM, 1 CPU)

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review this guide
3. Check GitHub issues
4. Create a new issue with logs and error messages

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [UFW Documentation](https://help.ubuntu.com/community/UFW)

---

Happy deploying! 🚀
