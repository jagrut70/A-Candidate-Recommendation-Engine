from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
import uuid
import re
from dotenv import load_dotenv
import openai
from skill_extractor import skill_extractor
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        print(f"Error reading file: {e}")
        return ""

def generate_embeddings_simple(texts):
    """Generate simple TF-IDF embeddings instead of sentence-transformers"""
    try:
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        return tfidf_matrix
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def compute_similarity_simple(embeddings, job_embedding_index=0):
    """Compute cosine similarity using TF-IDF"""
    try:
        if embeddings is None:
            return [0.0] * (len(embeddings) if embeddings else 1)
        
        # Calculate cosine similarity between job description and all candidates
        similarities = cosine_similarity(embeddings[job_embedding_index:job_embedding_index+1], embeddings[1:]).flatten()
        return similarities.tolist()
    except Exception as e:
        print(f"Error computing similarity: {e}")
        return [0.0]

def generate_ai_summary(job_description, candidate_info, similarity_score):
    """Generate AI summary using OpenAI"""
    try:
        print(f"Generating AI summary for candidate with similarity score: {similarity_score}")
        print(f"OpenAI API Key configured: {'Yes' if openai.api_key else 'No'}")
        
        # Extract skills
        print("Extracting skills from job description and candidate info...")
        job_skills = skill_extractor.extract_skills_from_text(job_description)
        candidate_skills = skill_extractor.extract_skills_from_text(candidate_info)
        skill_matches = skill_extractor.match_skills(job_skills, candidate_skills)
        
        print(f"Found skill matches: {skill_matches}")
        
        # Create enhanced prompt
        enhanced_prompt = skill_extractor.enhance_ai_prompt(
            job_description, candidate_info, skill_matches, similarity_score
        )
        
        print("Sending enhanced request to OpenAI API...")
        
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant helping to evaluate job candidates. Focus on specific skills and experience that match the job requirements."},
                {"role": "user", "content": enhanced_prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content.strip()
        print(f"AI summary generated successfully: {summary[:100]}...")
        
        return {
            'summary': summary,
            'skill_matches': skill_matches,
            'skill_summary': skill_extractor.get_skill_summary(skill_matches),
            'top_skills': skill_extractor.get_top_skills(skill_matches, 5)
        }
        
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return {
            'summary': f"AI summary unavailable. Similarity score: {similarity_score:.3f}",
            'skill_matches': {},
            'skill_summary': "Skill extraction unavailable",
            'top_skills': []
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        print("Upload route called")
        print(f"Request files: {request.files}")
        print(f"Request form: {request.form}")
        
        if 'resumes' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('resumes')
        candidates = []
        
        print(f"Found {len(files)} files")
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                print(f"Processing file: {filename}")
                print(f"Saved file to: {file_path}")
                
                content = extract_text_from_file(file_path)
                print(f"Extracted content length: {len(content)}")
                
                candidate = {
                    'id': str(uuid.uuid4()),
                    'name': filename.rsplit('.', 1)[0],
                    'content': content,
                    'filename': filename
                }
                candidates.append(candidate)
        
        # Store candidates in session
        session['candidates'] = candidates
        print(f"Stored {len(candidates)} candidates in session")
        print(f"Session data after storing: {session}")
        
        return jsonify({'message': f'Successfully uploaded {len(candidates)} files', 'candidates': candidates})
        
    except Exception as e:
        print(f"Error in upload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate recommendations"""
    try:
        print("Recommend route called")
        print(f"Session data: {session}")
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        # Get candidates from session
        candidates = session.get('candidates', [])
        print(f"Found {len(candidates)} candidates in session")
        
        if not candidates:
            return jsonify({'error': 'No candidates found. Please upload files first.'}), 400
        
        # Prepare texts for similarity calculation
        texts = [job_description] + [candidate['content'] for candidate in candidates]
        
        # Generate embeddings using simple TF-IDF
        embeddings = generate_embeddings_simple(texts)
        
        # Compute similarities
        similarities = compute_similarity_simple(embeddings)
        
        # Generate recommendations
        recommendations = []
        for i, candidate in enumerate(candidates):
            similarity_score = similarities[i] if i < len(similarities) else 0.0
            
            # Generate AI summary
            ai_result = generate_ai_summary(job_description, candidate['content'], similarity_score)
            
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
        
        # Sort by similarity score (descending)
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"Returning {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"  - {rec['name']}: {rec['similarity_score']:.3f}, AI summary: {rec['ai_summary'][:50]}...")
        
        return jsonify({
            'recommendations': recommendations,
            'total_candidates': len(candidates)
        })
        
    except Exception as e:
        print(f"Error in recommend: {e}")
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
        
        # Generate embeddings using simple TF-IDF
        embeddings = generate_embeddings_simple(texts)
        
        # Compute similarities
        similarities = compute_similarity_simple(embeddings)
        
        # Generate recommendations
        recommendations = []
        for i, candidate in enumerate(candidates_data):
            similarity_score = similarities[i] if i < len(similarities) else 0.0
            
            # Generate AI summary
            ai_result = generate_ai_summary(job_description, candidate['content'], similarity_score)
            
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
        
        # Sort by similarity score (descending)
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'total_candidates': len(candidates_data)
        })
        
    except Exception as e:
        print(f"Error in manual input: {e}")
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
    app.run(host='0.0.0.0', port=port, debug=False)
