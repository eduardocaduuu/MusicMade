# Deployment Guide - Render Free Tier

This guide explains how to deploy MusicMade to Render using the free tier.

## Prerequisites

- GitHub account
- Render account (sign up at https://render.com)
- This repository pushed to GitHub

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**
   - Go to https://render.com/dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the `MusicMade` repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**
   - Render will auto-generate most variables
   - Update `ALLOWED_ORIGINS` with your frontend URL
   - Update `REACT_APP_API_URL` with your backend URL

4. **Deploy**
   - Click "Apply"
   - Wait for all services to deploy (5-10 minutes)

### Option 2: Manual Deployment

#### Backend API

1. **Create Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
   - Settings:
     - Name: `musicmade-backend`
     - Environment: `Python 3`
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Plan: `Free`

2. **Add Environment Variables**
   ```
   DATABASE_URL=<from PostgreSQL service>
   REDIS_URL=<from Redis service>
   SECRET_KEY=<generate random string>
   ENVIRONMENT=production
   MAX_FILE_SIZE=104857600
   UPLOAD_PATH=/tmp/uploads
   MODELS_PATH=/tmp/models
   TEMP_PATH=/tmp/temp
   ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
   ```

#### Celery Worker

1. **Create Background Worker**
   - Dashboard → "New" → "Background Worker"
   - Connect same GitHub repository
   - Settings:
     - Name: `musicmade-worker`
     - Environment: `Python 3`
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Start Command: `cd backend && celery -A app.workers.celery_worker worker --loglevel=info --concurrency=1`
     - Plan: `Free`

2. **Add Same Environment Variables as Backend**

#### Frontend

1. **Create Static Site**
   - Dashboard → "New" → "Static Site"
   - Connect same GitHub repository
   - Settings:
     - Name: `musicmade-frontend`
     - Build Command: `cd frontend && npm install && npm run build`
     - Publish Directory: `frontend/build`
     - Plan: `Free`

2. **Add Environment Variables**
   ```
   REACT_APP_API_URL=https://musicmade-backend.onrender.com
   REACT_APP_WS_URL=wss://musicmade-backend.onrender.com
   ```

#### PostgreSQL Database

1. **Create PostgreSQL Database**
   - Dashboard → "New" → "PostgreSQL"
   - Settings:
     - Name: `musicmade-db`
     - Database Name: `musicmade`
     - Plan: `Free`

2. **Copy Connection String**
   - Copy the internal connection string
   - Add it to backend and worker as `DATABASE_URL`

#### Redis

1. **Create Redis Instance**
   - Dashboard → "New" → "Redis"
   - Settings:
     - Name: `musicmade-redis`
     - Plan: `Free`

2. **Copy Connection String**
   - Copy the internal connection string
   - Add it to backend and worker as `REDIS_URL`

## Free Tier Limitations

### Render Free Tier Constraints:

1. **Web Services**
   - Spin down after 15 minutes of inactivity
   - Spin up time: ~30-60 seconds on first request
   - 512 MB RAM
   - No persistent storage (use `/tmp`)

2. **Background Workers**
   - Same spin down behavior
   - Limited to 1 concurrent process

3. **Databases**
   - PostgreSQL: 1GB storage, expires after 90 days
   - Redis: 25MB storage

4. **Static Sites**
   - 100GB bandwidth/month
   - Global CDN

### Optimizations for Free Tier:

1. **File Storage**: Use `/tmp` directory (ephemeral)
   - Files are deleted when service spins down
   - Consider external storage (S3, Cloudinary) for production

2. **Processing**:
   - Use Demucs with `fast` quality for quicker results
   - Set worker concurrency to 1

3. **Database**:
   - Use SQLite for development
   - PostgreSQL free tier for production

## Monitoring

### Health Check Endpoints
- Backend: `https://your-backend.onrender.com/health`
- Frontend: `https://your-frontend.onrender.com`

### Logs
- View logs in Render Dashboard for each service
- Monitor for errors and performance issues

## Troubleshooting

### Service Won't Start
1. Check logs in Render Dashboard
2. Verify all environment variables are set
3. Check build command completed successfully

### Audio Separation Fails
1. Check worker logs
2. Verify Redis connection
3. Ensure file size is under 100MB
4. Check `/tmp` storage not full

### Slow Performance
1. First request after spin down takes 30-60s
2. Consider keeping services "warm" with periodic pings
3. Upgrade to paid plan for better performance

## Upgrade Path

For production use, consider:
1. **Starter Plan** ($7/month per service)
   - No spin down
   - More RAM (512MB - 2GB)
   - Better performance

2. **External Services**
   - AWS S3 for file storage
   - Dedicated Redis instance
   - PostgreSQL on AWS RDS

3. **Optimization**
   - CDN for static assets
   - Caching layer
   - Load balancing

## Support

- Render Docs: https://render.com/docs
- GitHub Issues: https://github.com/eduardocaduuu/MusicMade/issues
