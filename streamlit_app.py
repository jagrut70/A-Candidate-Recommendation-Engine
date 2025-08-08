import streamlit as st
import os
import json
import uuid
import re
from collections import Counter
import pandas as pd

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

# Simple skill extraction without external dependencies
def extract_skills_simple(text):
    """Simple skill extraction using keyword matching"""
    skills = {
        'programming_languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'typescript'],
        'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'express', 'spring', 'laravel', 'rails', 'asp.net', 'fastapi', 'node.js', 'bootstrap', 'jquery'],
        'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server', 'mariadb', 'cassandra', 'dynamodb'],
        'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible', 'ci/cd'],
        'tools': ['git', 'jira', 'confluence', 'slack', 'vscode', 'intellij', 'eclipse', 'postman', 'swagger', 'figma', 'adobe']
    }
    
    text_lower = text.lower()
    found_skills = {}
    
    for category, skill_list in skills.items():
        found_skills[category] = []
        for skill in skill_list:
            if skill in text_lower:
                found_skills[category].append(skill)
    
    return found_skills

def compute_similarity_simple(job_text, candidate_text):
    """Simple text similarity using word overlap"""
    # Convert to lowercase and split into words
    job_words = set(re.findall(r'\b\w+\b', job_text.lower()))
    candidate_words = set(re.findall(r'\b\w+\b', candidate_text.lower()))
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
    
    job_words = job_words - stop_words
    candidate_words = candidate_words - stop_words
    
    # Calculate Jaccard similarity
    if len(job_words) == 0 or len(candidate_words) == 0:
        return 0.0
    
    intersection = len(job_words.intersection(candidate_words))
    union = len(job_words.union(candidate_words))
    
    return intersection / union if union > 0 else 0.0

def generate_summary_simple(job_description, candidate_info, similarity_score, skill_matches):
    """Generate a simple summary without OpenAI"""
    summary = f"This candidate has a similarity score of {similarity_score:.1%}. "
    
    if skill_matches:
        skill_text = []
        for category, skills in skill_matches.items():
            if skills:
                skill_text.append(f"{', '.join(skills)} ({category.replace('_', ' ')})")
        
        if skill_text:
            summary += f"Key matching skills: {'; '.join(skill_text)}. "
    
    # Add some context based on similarity score
    if similarity_score > 0.7:
        summary += "This candidate appears to be an excellent match for the position."
    elif similarity_score > 0.5:
        summary += "This candidate shows good potential for the role."
    elif similarity_score > 0.3:
        summary += "This candidate has some relevant experience but may need additional training."
    else:
        summary += "This candidate may not be the best fit for this specific role."
    
    return summary

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
        st.markdown("### 🔧 About This App")
        st.info("""
        This app uses:
        • **Text similarity analysis**
        • **Skill keyword matching**
        • **Simple but effective algorithms**
        
        No external APIs required!
        """)
    
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
                type=['txt'],
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
            # Process candidates
            results = []
            for candidate in st.session_state.candidates:
                # Compute similarity
                similarity_score = compute_similarity_simple(job_description, candidate['content'])
                
                # Extract skills
                job_skills = extract_skills_simple(job_description)
                candidate_skills = extract_skills_simple(candidate['content'])
                
                # Find matching skills
                skill_matches = {}
                for category in job_skills:
                    if category in candidate_skills:
                        matches = list(set(job_skills[category]) & set(candidate_skills[category]))
                        if matches:
                            skill_matches[category] = matches
                
                # Generate summary
                summary = generate_summary_simple(job_description, candidate['content'], similarity_score, skill_matches)
                
                result = {
                    'id': candidate['id'],
                    'name': candidate['name'],
                    'similarity_score': similarity_score,
                    'ai_summary': summary,
                    'skill_matches': skill_matches,
                    'skill_summary': f"Found {sum(len(skills) for skills in skill_matches.values())} matching skills",
                    'top_skills': [skill for skills in skill_matches.values() for skill in skills][:5],
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
                        
                        # Summary
                        st.markdown("**🤖 Analysis:**")
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
        <p>🎯 AI Candidate Matcher | Powered by Text Analysis & Skill Matching</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
