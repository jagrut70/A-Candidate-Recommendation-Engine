# Deployment Guide

This guide provides instructions for deploying the AI Candidate Recommendation Engine to various platforms.

## 🚀 Deployment Options

### Option 1: Heroku (Recommended)

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository

#### Steps
1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   heroku config:set SECRET_KEY=your_secret_key
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Open App**
   ```bash
   heroku open
   ```

### Option 2: Railway

#### Steps
1. **Connect Repository**
   - Go to [Railway](https://railway.app/)
   - Connect your GitHub repository
   - Select the repository

2. **Set Environment Variables**
   - Add `OPENAI_API_KEY` and `SECRET_KEY` in Railway dashboard

3. **Deploy**
   - Railway will automatically deploy from your repository
   - Access the provided URL

### Option 3: Render

#### Steps
1. **Create New Web Service**
   - Go to [Render](https://render.com/)
   - Connect your GitHub repository
   - Select "Web Service"

2. **Configure**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add `OPENAI_API_KEY` and `SECRET_KEY`

3. **Deploy**
   - Render will automatically deploy your application

### Option 4: Streamlit Cloud

#### Steps
1. **Create Streamlit App**
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository

2. **Configure**
   - Set environment variables in Streamlit Cloud dashboard
   - Deploy automatically

### Option 5: Replit

#### Steps
1. **Create Repl**
   - Go to [Replit](https://replit.com/)
   - Create new Python repl
   - Import your GitHub repository

2. **Configure**
   - Add environment variables in Replit secrets
   - Run the application

## 🔧 Environment Variables

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI summaries
- `SECRET_KEY`: Flask secret key for session management

### Optional Variables
- `PORT`: Port number (automatically set by deployment platforms)

## 📋 Pre-deployment Checklist

- [ ] All files committed to Git repository
- [ ] Environment variables configured
- [ ] `requirements.txt` updated with exact versions
- [ ] `Procfile` created for Heroku/Railway
- [ ] `runtime.txt` specifies Python version
- [ ] Application tested locally
- [ ] OpenAI API key is valid and has quota

## 🐛 Common Deployment Issues

### Heroku Issues
- **H10 Error**: Check if the app is running and logs
- **H14 Error**: Ensure `Procfile` is correct
- **Build Failures**: Check `requirements.txt` compatibility

### General Issues
- **Environment Variables**: Ensure all required variables are set
- **Port Issues**: Most platforms set PORT automatically
- **Memory Issues**: Consider upgrading dyno/plan for larger models

## 📊 Performance Considerations

### Resource Requirements
- **Memory**: Minimum 512MB RAM (1GB recommended)
- **Storage**: ~500MB for model files
- **CPU**: Standard tier sufficient for most use cases

### Optimization Tips
- **Model Loading**: First deployment may take longer due to model download
- **Caching**: Consider implementing Redis for session storage
- **CDN**: Use CDN for static files in production

## 🔒 Security Considerations

### Production Security
- **HTTPS**: Enable HTTPS in production
- **API Keys**: Never commit API keys to repository
- **File Uploads**: Implement proper file validation
- **Rate Limiting**: Consider implementing rate limiting

### Environment Variables
```bash
# Example .env file (DO NOT COMMIT)
OPENAI_API_KEY=sk-your-openai-key-here
SECRET_KEY=your-secret-key-here
PORT=8080
```

## 📞 Support

For deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Verify environment variables
4. Test locally before deploying

## 🎯 Deployment URLs

After successful deployment, your application will be available at:
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **Streamlit**: `https://your-app-name.streamlit.app`
- **Replit**: `https://your-app-name.replit.co` 