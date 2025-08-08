import streamlit as st
import os
import json
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from dotenv import load_dotenv
from skill_extractor import skill_extractor
import pandas as pd

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Candidate Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'candidates' not in st.session_state:
    st.session_state.candidates = []

# Initialize the sentence transformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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
    try:
        # Extract skills from job description and candidate info
        job_skills = skill_extractor.extract_skills_from_text(job_description)
        candidate_skills = skill_extractor.extract_skills_from_text(candidate_info)
        
        # Match skills between job and candidate
        skill_matches = skill_extractor.match_skills(job_skills, candidate_skills)
        
        # Generate enhanced prompt with skill information
        enhanced_prompt = skill_extractor.enhance_ai_prompt(
            job_description, candidate_info, skill_matches, similarity_score
        )
        
        # Use the new OpenAI API syntax
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
        
        return {
            'summary': summary,
            'skill_matches': skill_matches,
            'skill_summary': skill_extractor.get_skill_summary(skill_matches),
            'top_skills': skill_extractor.get_top_skills(skill_matches, 5)
        }
        
    except Exception as e:
        st.error(f"Error generating AI summary: {e}")
        return {
            'summary': f"AI summary unavailable. Similarity score: {similarity_score:.3f}",
            'skill_matches': {},
            'skill_summary': "Skill extraction unavailable",
            'top_skills': []
        }

def main():
    # Header
    st.title("🎯 AI Candidate Matcher")
    st.markdown("### Find the Perfect Talent for Your Organization")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Input Methods")
        input_method = st.radio(
            "Choose input method:",
            ["Manual Input", "File Upload"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 🔧 Settings")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key (for AI summaries)",
            type="password",
            value=os.getenv('OPENAI_API_KEY', ''),
            help="Enter your OpenAI API key to enable AI-powered summaries"
        )
        
        if api_key:
            openai.api_key = api_key
            st.success("✅ OpenAI API key configured")
        else:
            st.warning("⚠️ OpenAI API key not provided - AI summaries will be disabled")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Job Description")
        job_description = st.text_area(
            "Enter the job description:",
            height=200,
            placeholder="e.g., Python developer with experience in Django, React, and AWS. Must have knowledge of PostgreSQL, Docker, and Git."
        )
    
    with col2:
        st.header("👥 Candidates")
        
        if input_method == "Manual Input":
            # Manual input
            num_candidates = st.number_input("Number of candidates:", min_value=1, max_value=10, value=1)
            
            candidates = []
            for i in range(num_candidates):
                with st.expander(f"Candidate {i+1}", expanded=True):
                    name = st.text_input(f"Name {i+1}:", key=f"name_{i}")
                    resume = st.text_area(f"Resume/Experience {i+1}:", height=150, key=f"resume_{i}")
                    
                    if name and resume:
                        candidates.append({
                            'id': str(uuid.uuid4()),
                            'name': name,
                            'content': resume,
                            'filename': f'manual_input_{i+1}.txt'
                        })
            
            st.session_state.candidates = candidates
            
        else:
            # File upload
            uploaded_files = st.file_uploader(
                "Upload candidate resumes:",
                type=['txt', 'pdf', 'doc', 'docx'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                candidates = []
                for file in uploaded_files:
                    content = file.read().decode('utf-8')
                    candidates.append({
                        'id': str(uuid.uuid4()),
                        'name': file.name.split('.')[0],
                        'content': content,
                        'filename': file.name
                    })
                
                st.session_state.candidates = candidates
                st.success(f"✅ Uploaded {len(candidates)} files")
    
    # Generate recommendations button
    if st.button("🚀 Generate Recommendations", type="primary", use_container_width=True):
        if not job_description:
            st.error("Please enter a job description")
            return
        
        if not st.session_state.candidates:
            st.error("Please add at least one candidate")
            return
        
        with st.spinner("Analyzing candidates..."):
            # Generate embeddings
            texts = [job_description] + [candidate['content'] for candidate in st.session_state.candidates]
            embeddings = generate_embeddings(texts)
            
            # Compute similarities
            job_embedding = embeddings[0]
            resume_embeddings = embeddings[1:]
            similarities = compute_similarity(job_embedding, resume_embeddings)
            
            # Create results
            results = []
            for i, candidate in enumerate(st.session_state.candidates):
                similarity_score = float(similarities[i])
                
                # Generate AI summary
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
            
            # Sort by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Display results
            st.header("🎯 AI Recommendations")
            st.success(f"Analyzed {len(results)} candidates, showing top matches")
            
            for i, result in enumerate(results):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(f"#{i+1} - {result['name']}")
                        
                        # Similarity score
                        score = result['similarity_score']
                        st.metric("Match Score", f"{score:.1%}")
                        
                        # Skill matches
                        if result['skill_matches']:
                            st.markdown("**🔧 Key Skill Matches:**")
                            for category, skills in result['skill_matches'].items():
                                st.markdown(f"- **{category.replace('_', ' ').title()}**: {', '.join(skills)}")
                        
                        # Top skills
                        if result['top_skills']:
                            st.markdown("**⭐ Top Matching Skills:**")
                            skills_text = " • ".join(result['top_skills'])
                            st.markdown(f"`{skills_text}`")
                        
                        # AI Summary
                        st.markdown("**🤖 AI Analysis:**")
                        st.write(result['ai_summary'])
                    
                    with col2:
                        # Progress bar for similarity
                        st.progress(score)
                        
                        # File info
                        st.caption(f"Source: {result['filename']}")
                    
                    st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>🎯 AI Candidate Matcher | Powered by Sentence Transformers & OpenAI</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
