# Render Deployment Guide

## Step-by-Step Instructions to Deploy on Render

### Prerequisites
- A GitHub account
- A Render account (free at https://render.com)

### Steps:

1. **Push your code to GitHub:**
   ```bash
   cd /home/shivam/Desktop/image-to-4k
   git init
   git add .
   git commit -m "Initial commit - 4K batch image converter"
   # Create a new repository on GitHub, then:
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://dashboard.render.com
   - Click "New +" button → Select "Web Service"
   - Click "Build and deploy from a Git repository"
   - Connect your GitHub account if not already connected
   - Select your repository
   - Render will auto-detect the settings from render.yaml

3. **Or use Blueprint (Automatic):**
   - Go to https://dashboard.render.com
   - Click "New +" button → Select "Blueprint"
   - Connect your GitHub repository
   - Click "Apply" - Render will automatically configure everything from render.yaml

4. **Access your app:**
   - After deployment completes, you'll get a URL like: `https://your-app-name.onrender.com`
   - The app is now live and accessible from anywhere!

### Important Notes:

✅ **Free Tier Limitations:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep may take 30-60 seconds
- 750 hours/month free (enough to keep it running 24/7)

✅ **Storage:**
- Uploaded and converted images are temporary
- Files will be cleared when the service restarts
- For persistent storage, consider using cloud storage (S3, Cloudinary)

✅ **Performance:**
- Free tier has limited CPU/memory
- Good for personal use and demos
- For production, consider upgrading to paid tier

### Troubleshooting:

**Build fails?**
- Check that all files are committed to Git
- Verify requirements.txt is present
- Check build logs in Render dashboard

**App crashes?**
- Check the logs in Render dashboard
- Ensure PORT environment variable is not hardcoded
- Verify gunicorn is in requirements.txt

**Slow performance?**
- Free tier has limited resources
- Consider upgrading to paid tier
- Optimize image processing for large files

### Manual Configuration (if not using render.yaml):

If you prefer manual setup:
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Auto-Deploy**: Yes

Enjoy your deployed 4K Image Converter! 🚀
