from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
import uuid
import re
from dotenv import load_dotenv
import openai
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """Extract text from uploaded file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return ""

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
    """Simple skill extraction without external dependencies"""
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

def generate_ai_summary_simple(job_description, candidate_info, similarity_score):
    """Generate simple summary without OpenAI dependency"""
    try:
        # Extract skills
        job_skills = extract_skills_simple(job_description)
        candidate_skills = extract_skills_simple(candidate_info)
        
        # Find matching skills
        skill_matches = {}
        for category in job_skills:
            if category in candidate_skills:
                matches = list(set(job_skills[category]) & set(candidate_skills[category]))
                if matches:
                    skill_matches[category] = matches
        
        # Generate simple summary
        summary = f"This candidate has a similarity score of {similarity_score:.3f}. "
        
        if skill_matches:
            skill_text = []
            for category, skills in skill_matches.items():
                skill_text.append(f"{', '.join(skills)} ({category.replace('_', ' ')})")
            summary += f"Key matching skills: {'; '.join(skill_text)}. "
        
        summary += "The candidate appears to be a good match based on the provided information."
        
        return {
            'summary': summary,
            'skill_matches': skill_matches,
            'skill_summary': f"Found {sum(len(skills) for skills in skill_matches.values())} matching skills",
            'top_skills': [skill for skills in skill_matches.values() for skill in skills][:5]
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {
            'summary': f"Summary unavailable. Similarity score: {similarity_score:.3f}",
            'skill_matches': {},
            'skill_summary': "Skill extraction unavailable",
            'top_skills': []
        }

@app.route('/')
def index():
    """Main page"""
    try:
        logger.info("Serving main page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving main page: {e}")
        return f"Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'port': os.environ.get('PORT', '8080'),
        'openai_key': 'set' if os.environ.get('OPENAI_API_KEY') else 'not set',
        'secret_key': 'set' if os.environ.get('SECRET_KEY') else 'not set'
    })

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        logger.info("Upload route called")
        
        if 'resumes' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('resumes')
        candidates = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                content = extract_text_from_file(file_path)
                
                candidate = {
                    'id': str(uuid.uuid4()),
                    'name': filename.rsplit('.', 1)[0],
                    'content': content,
                    'filename': filename
                }
                candidates.append(candidate)
        
        session['candidates'] = candidates
        logger.info(f"Stored {len(candidates)} candidates in session")
        
        return jsonify({'message': f'Successfully uploaded {len(candidates)} files', 'candidates': candidates})
        
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate recommendations"""
    try:
        logger.info("Recommend route called")
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        candidates = session.get('candidates', [])
        
        if not candidates:
            return jsonify({'error': 'No candidates found. Please upload files first.'}), 400
        
        # Prepare texts for similarity calculation
        texts = [job_description] + [candidate['content'] for candidate in candidates]
        
        # Generate embeddings
        embeddings = generate_embeddings_simple(texts)
        
        # Compute similarities
        similarities = compute_similarity_simple(embeddings)
        
        # Generate recommendations
        recommendations = []
        for i, candidate in enumerate(candidates):
            similarity_score = similarities[i] if i < len(similarities) else 0.0
            
            # Generate summary
            ai_result = generate_ai_summary_simple(job_description, candidate['content'], similarity_score)
            
            recommendation = {
                'id': candidate['id'],
                'name': candidate['name'],
                'filename': candidate['filename'],
                'similarity_score': similarity_score,
                'ai_summary': ai_result['summary'],
                'skill_matches': ai_result['skill_matches'],
                'skill_summary': ai_result['skill_summary'],
                'top_skills': ai_result['top_skills']
            }
            recommendations.append(recommendation)
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"Returning {len(recommendations)} recommendations")
        
        return jsonify({
            'recommendations': recommendations,
            'total_candidates': len(candidates)
        })
        
    except Exception as e:
        logger.error(f"Error in recommend: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/manual-input', methods=['POST'])
def manual_input():
    """Handle manual candidate input"""
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        candidates_data = data.get('candidates', [])
        
        if not candidates_data:
            return jsonify({'error': 'No candidates provided'}), 400
        
        # Prepare texts for similarity calculation
        texts = [job_description] + [candidate['content'] for candidate in candidates_data]
        
        # Generate embeddings
        embeddings = generate_embeddings_simple(texts)
        
        # Compute similarities
        similarities = compute_similarity_simple(embeddings)
        
        # Generate recommendations
        recommendations = []
        for i, candidate in enumerate(candidates_data):
            similarity_score = similarities[i] if i < len(similarities) else 0.0
            
            # Generate summary
            ai_result = generate_ai_summary_simple(job_description, candidate['content'], similarity_score)
            
            recommendation = {
                'id': candidate['id'],
                'name': candidate['name'],
                'similarity_score': similarity_score,
                'ai_summary': ai_result['summary'],
                'skill_matches': ai_result['skill_matches'],
                'skill_summary': ai_result['skill_summary'],
                'top_skills': ai_result['top_skills']
            }
            recommendations.append(recommendation)
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'total_candidates': len(candidates_data)
        })
        
    except Exception as e:
        logger.error(f"Error in manual input: {e}")
        return jsonify({'error': str(e)}), 500

@app.after_request
def add_header(response):
    """Disable caching for development"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
