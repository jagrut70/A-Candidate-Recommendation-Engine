import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from dotenv import load_dotenv
from skill_extractor import skill_extractor

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure OpenAI API
openai_api_key = os.getenv('OPENAI_API_KEY')
print(f"OpenAI API Key loaded: {'Yes' if openai_api_key else 'No'}")
if openai_api_key:
    print(f"API Key length: {len(openai_api_key)} characters")
    print(f"API Key starts with: {openai_api_key[:10]}...")
else:
    print("WARNING: No OpenAI API key found!")

openai.api_key = openai_api_key

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """Extract text from uploaded file (simplified version)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except:
        return "Unable to read file content"

def generate_embeddings(texts):
    """Generate embeddings for a list of texts"""
    embeddings = model.encode(texts, convert_to_tensor=True)
    return embeddings.cpu().numpy()

def compute_similarity(job_embedding, resume_embeddings):
    """Compute cosine similarity between job and resumes"""
    similarities = cosine_similarity([job_embedding], resume_embeddings)[0]
    return similarities

def generate_ai_summary(job_description, candidate_info, similarity_score):
    """Generate AI summary for why candidate is a good fit with skill extraction"""
    print(f"Generating AI summary for candidate with similarity score: {similarity_score:.3f}")
    print(f"OpenAI API Key configured: {'Yes' if openai.api_key else 'No'}")
    
    try:
        # Extract skills from job description and candidate info
        print("Extracting skills from job description and candidate info...")
        job_skills = skill_extractor.extract_skills_from_text(job_description)
        candidate_skills = skill_extractor.extract_skills_from_text(candidate_info)
        
        # Match skills between job and candidate
        skill_matches = skill_extractor.match_skills(job_skills, candidate_skills)
        print(f"Found skill matches: {skill_matches}")
        
        # Generate enhanced prompt with skill information
        enhanced_prompt = skill_extractor.enhance_ai_prompt(
            job_description, candidate_info, skill_matches, similarity_score
        )
        
        print("Sending enhanced request to OpenAI API...")
        
        # Use the new OpenAI API syntax (v1.0.0+)
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
        
        # Return both summary and skill matches
        return {
            'summary': summary,
            'skill_matches': skill_matches,
            'skill_summary': skill_extractor.get_skill_summary(skill_matches),
            'top_skills': skill_extractor.get_top_skills(skill_matches, 5)
        }
    except Exception as e:
        print(f"Error generating AI summary: {str(e)}")
        print(f"Error type: {type(e).__name__}")
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
    print("Upload route called")
    print("Request files:", request.files)
    print("Request form:", request.form)
    
    if 'resumes' not in request.files:
        print("No 'resumes' in request.files")
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('resumes')
    print(f"Found {len(files)} files")
    candidates = []
    
    for file in files:
        print(f"Processing file: {file.filename}")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"Saved file to: {file_path}")
            
            # Extract text from file
            content = extract_text_from_file(file_path)
            print(f"Extracted content length: {len(content)}")
            
            # Create candidate object
            candidate = {
                'id': str(uuid.uuid4()),
                'name': filename.rsplit('.', 1)[0],  # Remove extension
                'content': content,
                'filename': filename
            }
            candidates.append(candidate)
        else:
            print(f"File {file.filename} not allowed or empty")
    
    # Store candidates in session
    session['candidates'] = candidates
    print(f"Stored {len(candidates)} candidates in session")
    print("Session data after storing:", dict(session))
    
    return jsonify({
        'message': f'Successfully uploaded {len(candidates)} files',
        'candidates': candidates
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    print("Recommend route called")
    print("Session data:", dict(session))
    
    data = request.get_json()
    job_description = data.get('job_description', '')
    
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    candidates = session.get('candidates', [])
    print(f"Found {len(candidates)} candidates in session")
    
    if not candidates:
        return jsonify({'error': 'No candidates uploaded'}), 400
    
    # Generate embeddings
    texts = [job_description] + [candidate['content'] for candidate in candidates]
    embeddings = generate_embeddings(texts)
    
    # Compute similarities
    job_embedding = embeddings[0]
    resume_embeddings = embeddings[1:]
    similarities = compute_similarity(job_embedding, resume_embeddings)
    
    # Create results with similarity scores
    results = []
    for i, candidate in enumerate(candidates):
        similarity_score = float(similarities[i])
        
        # Generate AI summary with skill extraction
        ai_result = generate_ai_summary(job_description, candidate['content'], similarity_score)
        print(f"AI summary for {candidate['name']}: {ai_result['summary'][:100]}...")
        
        result = {
            'id': candidate['id'],
            'name': candidate['name'],
            'similarity_score': similarity_score,
            'ai_summary': ai_result['summary'],
            'skill_matches': ai_result['skill_matches'],
            'skill_summary': ai_result['skill_summary'],
            'top_skills': ai_result['top_skills'],
            'filename': candidate['filename']
        }
        results.append(result)
    
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Return top 10 results
    top_results = results[:10]
    
    print(f"Returning {len(top_results)} recommendations")
    for result in top_results:
        print(f"  - {result['name']}: {result['similarity_score']:.3f}, AI summary: {result['ai_summary'][:50]}...")
    
    return jsonify({
        'recommendations': top_results,
        'total_candidates': len(candidates)
    })

@app.route('/manual-input', methods=['POST'])
def manual_input():
    data = request.get_json()
    candidates_data = data.get('candidates', [])
    job_description = data.get('job_description', '')
    
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    if not candidates_data:
        return jsonify({'error': 'At least one candidate is required'}), 400
    
    # Process manual input candidates
    candidates = []
    for i, candidate_data in enumerate(candidates_data):
        candidate = {
            'id': str(uuid.uuid4()),
            'name': candidate_data.get('name', f'Candidate {i+1}'),
            'content': candidate_data.get('resume', ''),
            'filename': f'manual_input_{i+1}.txt'
        }
        candidates.append(candidate)
    
    # Store candidates in session
    session['candidates'] = candidates
    
    # Generate embeddings
    texts = [job_description] + [candidate['content'] for candidate in candidates]
    embeddings = generate_embeddings(texts)
    
    # Compute similarities
    job_embedding = embeddings[0]
    resume_embeddings = embeddings[1:]
    similarities = compute_similarity(job_embedding, resume_embeddings)
    
    # Create results with similarity scores
    results = []
    for i, candidate in enumerate(candidates):
        similarity_score = float(similarities[i])
        
        # Generate AI summary with skill extraction
        ai_result = generate_ai_summary(job_description, candidate['content'], similarity_score)
        
        result = {
            'id': candidate['id'],
            'name': candidate['name'],
            'similarity_score': similarity_score,
            'ai_summary': ai_result['summary'],
            'skill_matches': ai_result['skill_matches'],
            'skill_summary': ai_result['skill_summary'],
            'top_skills': ai_result['top_skills'],
            'filename': candidate['filename']
        }
        results.append(result)
    
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Return top 10 results
    top_results = results[:10]
    
    return jsonify({
        'recommendations': top_results,
        'total_candidates': len(candidates)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port) 