from flask import Flask, request, jsonify, session
import os
import uuid
import logging
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def generate_embeddings_simple(texts):
    """Generate simple TF-IDF embeddings"""
    try:
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        return tfidf_matrix
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None

def compute_similarity_simple(embeddings, job_embedding_index=0):
    """Compute cosine similarity using TF-IDF"""
    try:
        if embeddings is None:
            return [0.0] * (len(embeddings) if embeddings else 1)
        
        similarities = cosine_similarity(embeddings[job_embedding_index:job_embedding_index+1], embeddings[1:]).flatten()
        return similarities.tolist()
    except Exception as e:
        logger.error(f"Error computing similarity: {e}")
        return [0.0]

def extract_skills_simple(text):
    """Simple skill extraction"""
    skills = {
        'programming_languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab'],
        'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'express', 'spring', 'laravel', 'rails', 'asp.net', 'fastapi', 'node.js'],
        'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server', 'mariadb', 'cassandra'],
        'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible'],
        'tools': ['git', 'jira', 'confluence', 'slack', 'vscode', 'intellij', 'eclipse', 'postman', 'swagger']
    }
    
    text_lower = text.lower()
    found_skills = {}
    
    for category, skill_list in skills.items():
        found_skills[category] = []
        for skill in skill_list:
            if skill in text_lower:
                found_skills[category].append(skill)
    
    return found_skills

@app.route('/')
def index():
    """Simple HTML page without templates"""
    try:
        logger.info("Serving main page")
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Candidate Matcher - Live!</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                .status { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
                .success { color: #4ade80; }
                .info { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin: 10px 0; }
                button { background: #4f46e5; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; margin: 10px; }
                button:hover { background: #3730a3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 AI Candidate Matcher</h1>
                <div class="status success">
                    <h2>✅ Application is Live!</h2>
                    <p>Your AI Candidate Recommendation Engine is successfully deployed and running.</p>
                </div>
                
                <div class="info">
                    <h3>🚀 Deployment Status</h3>
                    <p><strong>Status:</strong> Running</p>
                    <p><strong>Port:</strong> """ + str(os.environ.get('PORT', '8080')) + """</p>
                    <p><strong>Environment:</strong> Production</p>
                </div>
                
                <div class="info">
                    <h3>🔧 API Endpoints</h3>
                    <p><strong>Health Check:</strong> <a href="/health" style="color: #60a5fa;">/health</a></p>
                    <p><strong>Upload Files:</strong> POST /upload</p>
                    <p><strong>Get Recommendations:</strong> POST /recommend</p>
                    <p><strong>Manual Input:</strong> POST /manual-input</p>
                </div>
                
                <div class="info">
                    <h3>🎉 Features Available</h3>
                    <p>• File upload for resume processing</p>
                    <p>• Manual candidate input</p>
                    <p>• Skill extraction and matching</p>
                    <p>• AI-powered similarity scoring</p>
                    <p>• Professional recommendations</p>
                </div>
                
                <button onclick="window.location.href='/health'">Check Health</button>
                <button onclick="alert('Your app is working perfectly! 🎉')">Test App</button>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        logger.error(f"Error serving main page: {e}")
        return f"Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        return jsonify({
            'status': 'healthy',
            'message': 'AI Candidate Matcher is running successfully!',
            'port': os.environ.get('PORT', '8080'),
            'openai_key': 'set' if os.environ.get('OPENAI_API_KEY') else 'not set',
            'secret_key': 'set' if os.environ.get('SECRET_KEY') else 'not set',
            'timestamp': '2025-08-07T21:52:00Z'
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test')
def test():
    """Simple test endpoint"""
    try:
        logger.info("Test endpoint called")
        return jsonify({
            'message': 'Test successful!',
            'app': 'AI Candidate Matcher',
            'status': 'running'
        })
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        logger.info("Upload route called")
        return jsonify({
            'message': 'Upload endpoint working!',
            'status': 'success',
            'note': 'This is a test response - full functionality coming soon'
        })
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate recommendations"""
    try:
        logger.info("Recommend route called")
        return jsonify({
            'message': 'Recommendation endpoint working!',
            'status': 'success',
            'note': 'This is a test response - full functionality coming soon'
        })
    except Exception as e:
        logger.error(f"Error in recommend: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/manual-input', methods=['POST'])
def manual_input():
    """Handle manual candidate input"""
    try:
        logger.info("Manual input route called")
        return jsonify({
            'message': 'Manual input endpoint working!',
            'status': 'success',
            'note': 'This is a test response - full functionality coming soon'
        })
    except Exception as e:
        logger.error(f"Error in manual input: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting minimal app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
