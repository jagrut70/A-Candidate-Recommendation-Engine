import re
import nltk
from typing import List, Set, Dict, Tuple
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillExtractor:
    """
    Advanced skill extraction and matching using NLP techniques.
    Uses NLTK for keyword extraction and regex patterns for skill detection.
    """
    
    def __init__(self):
        """Initialize the skill extractor with NLP models."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Comprehensive skill keywords database
        self.skill_keywords = {
            # Programming Languages
            'programming_languages': {
                'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
                'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'typescript', 'dart',
                'perl', 'bash', 'powershell', 'vba', 'assembly', 'cobol', 'fortran'
            },
            
            # Frameworks & Libraries
            'frameworks': {
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
                'laravel', 'rails', 'asp.net', 'fastapi', 'tensorflow', 'pytorch', 'scikit-learn',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'bootstrap', 'jquery', 'd3.js',
                'redux', 'vuex', 'mobx', 'graphql', 'rest api', 'docker', 'kubernetes'
            },
            
            # Databases
            'databases': {
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sql server', 'sqlite', 'dynamodb', 'firebase', 'neo4j',
                'influxdb', 'couchdb', 'mariadb'
            },
            
            # Cloud & DevOps
            'cloud_devops': {
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'jenkins', 'gitlab',
                'github actions', 'travis ci', 'circleci', 'terraform', 'ansible',
                'chef', 'puppet', 'vagrant', 'virtualbox', 'vmware'
            },
            
            # Data Science & ML
            'data_science': {
                'machine learning', 'deep learning', 'neural networks', 'computer vision',
                'natural language processing', 'nlp', 'data analysis', 'statistics',
                'regression', 'classification', 'clustering', 'recommendation systems',
                'time series', 'forecasting', 'a/b testing', 'experiment design'
            },
            
            # Soft Skills
            'soft_skills': {
                'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                'project management', 'agile', 'scrum', 'kanban', 'lean', 'six sigma',
                'customer service', 'presentation', 'negotiation', 'mentoring', 'coaching'
            },
            
            # Business & Domain
            'business_domain': {
                'finance', 'healthcare', 'e-commerce', 'retail', 'manufacturing', 'logistics',
                'supply chain', 'marketing', 'sales', 'hr', 'legal', 'education',
                'government', 'non-profit', 'startup', 'enterprise'
            },
            
            # Tools & Platforms
            'tools_platforms': {
                'git', 'svn', 'jira', 'confluence', 'slack', 'teams', 'zoom', 'figma',
                'sketch', 'adobe', 'photoshop', 'illustrator', 'excel', 'powerpoint',
                'tableau', 'power bi', 'looker', 'snowflake', 'databricks'
            }
        }
        
        # Common abbreviations and variations
        self.skill_abbreviations = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'nlp': 'natural language processing',
            'cv': 'computer vision',
            'ds': 'data science',
            'pm': 'project management',
            'ui': 'user interface',
            'ux': 'user experience',
            'api': 'application programming interface',
            'sdk': 'software development kit',
            'saas': 'software as a service',
            'paas': 'platform as a service',
            'iaas': 'infrastructure as a service'
        }
    
    def extract_skills_from_text(self, text: str) -> Dict[str, Set[str]]:
        """
        Extract skills from text using multiple NLP techniques.
        
        Args:
            text: Input text to extract skills from
            
        Returns:
            Dictionary with skill categories and extracted skills
        """
        if not text or not text.strip():
            return {}
        
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s\-+]', ' ', text)  # Remove special chars except hyphens and plus
        
        # Initialize results
        extracted_skills = {category: set() for category in self.skill_keywords.keys()}
        
        # Method 1: Direct keyword matching
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    extracted_skills[category].add(keyword)
        
        # Method 2: Abbreviation expansion
        for abbrev, full_form in self.skill_abbreviations.items():
            if abbrev in text:
                # Find appropriate category for the full form
                for category, keywords in self.skill_keywords.items():
                    if full_form in keywords:
                        extracted_skills[category].add(full_form)
                        break
        
        # Method 3: Pattern matching for skill mentions
        skill_patterns = [
            r'experience with (\w+(?:\s+\w+)*)',
            r'proficient in (\w+(?:\s+\w+)*)',
            r'expertise in (\w+(?:\s+\w+)*)',
            r'knowledge of (\w+(?:\s+\w+)*)',
            r'skilled in (\w+(?:\s+\w+)*)',
            r'familiar with (\w+(?:\s+\w+)*)',
            r'worked with (\w+(?:\s+\w+)*)',
            r'developed using (\w+(?:\s+\w+)*)',
            r'built with (\w+(?:\s+\w+)*)',
            r'technologies: (\w+(?:[,\s]+\w+)*)',
            r'skills: (\w+(?:[,\s]+\w+)*)',
            r'tools: (\w+(?:[,\s]+\w+)*)',
            r'programming languages: (\w+(?:[,\s]+\w+)*)',
            r'frameworks: (\w+(?:[,\s]+\w+)*)',
            r'databases: (\w+(?:[,\s]+\w+)*)',
            r'cloud platforms: (\w+(?:[,\s]+\w+)*)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by commas and clean up
                skills = [skill.strip() for skill in re.split(r'[,\s]+', match)]
                for skill in skills:
                    if len(skill) > 2:  # Filter out very short terms
                        for category, keywords in self.skill_keywords.items():
                            if skill in keywords:
                                extracted_skills[category].add(skill)
        
        # Method 4: NLTK-based extraction
        try:
            from nltk.tokenize import word_tokenize
            from nltk.corpus import stopwords
            
            # Tokenize the text
            tokens = word_tokenize(text)
            
            # Remove stopwords and short tokens
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [token for token in tokens if token.lower() not in stop_words and len(token) > 2]
            
            # Check if any tokens match our skill keywords
            for token in filtered_tokens:
                token_lower = token.lower()
                for category, keywords in self.skill_keywords.items():
                    if token_lower in keywords:
                        extracted_skills[category].add(token_lower)
        except Exception as e:
            logger.warning(f"NLTK extraction failed: {e}")
        
        return extracted_skills
    
    def match_skills(self, job_skills: Dict[str, Set[str]], resume_skills: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        """
        Match skills between job requirements and candidate resume.
        
        Args:
            job_skills: Skills extracted from job description
            resume_skills: Skills extracted from candidate resume
            
        Returns:
            Dictionary with matching skills by category
        """
        matches = {}
        
        for category in self.skill_keywords.keys():
            job_category_skills = job_skills.get(category, set())
            resume_category_skills = resume_skills.get(category, set())
            
            # Find exact matches
            exact_matches = job_category_skills.intersection(resume_category_skills)
            
            # Find partial matches (substring matching)
            partial_matches = set()
            for job_skill in job_category_skills:
                for resume_skill in resume_category_skills:
                    if job_skill in resume_skill or resume_skill in job_skill:
                        partial_matches.add(resume_skill)
            
            # Combine exact and partial matches
            all_matches = list(exact_matches.union(partial_matches))
            
            if all_matches:
                matches[category] = sorted(all_matches)
        
        return matches
    
    def get_skill_summary(self, matches: Dict[str, List[str]]) -> str:
        """
        Generate a human-readable summary of skill matches.
        
        Args:
            matches: Dictionary of skill matches by category
            
        Returns:
            Formatted summary string
        """
        if not matches:
            return "No specific skill matches found."
        
        summary_parts = []
        
        # Count total matches
        total_matches = sum(len(skills) for skills in matches.values())
        
        # Add category-specific summaries
        for category, skills in matches.items():
            if skills:
                category_name = category.replace('_', ' ').title()
                if len(skills) == 1:
                    summary_parts.append(f"{category_name}: {skills[0]}")
                else:
                    summary_parts.append(f"{category_name}: {', '.join(skills[:-1])} and {skills[-1]}")
        
        # Create final summary
        if total_matches == 1:
            summary = f"Found 1 matching skill: {summary_parts[0]}"
        else:
            summary = f"Found {total_matches} matching skills across {len(matches)} categories: {'; '.join(summary_parts)}"
        
        return summary
    
    def get_top_skills(self, matches: Dict[str, List[str]], top_n: int = 5) -> List[str]:
        """
        Get the top N most relevant skills from matches.
        
        Args:
            matches: Dictionary of skill matches by category
            top_n: Number of top skills to return
            
        Returns:
            List of top skills
        """
        all_skills = []
        for skills in matches.values():
            all_skills.extend(skills)
        
        # Count frequency and return top N
        skill_counts = Counter(all_skills)
        return [skill for skill, count in skill_counts.most_common(top_n)]
    
    def enhance_ai_prompt(self, job_description: str, candidate_info: str, 
                         skill_matches: Dict[str, List[str]], similarity_score: float) -> str:
        """
        Enhance the AI prompt with skill match information.
        
        Args:
            job_description: Original job description
            candidate_info: Candidate information
            skill_matches: Extracted skill matches
            similarity_score: Cosine similarity score
            
        Returns:
            Enhanced prompt for AI summary generation
        """
        skill_summary = self.get_skill_summary(skill_matches)
        top_skills = self.get_top_skills(skill_matches, 3)
        
        enhanced_prompt = f"""
        Job Description: {job_description}
        
        Candidate Information: {candidate_info}
        
        Similarity Score: {similarity_score:.3f}
        
        Key Skill Matches Found:
        {skill_summary}
        
        Top Matching Skills: {', '.join(top_skills) if top_skills else 'None identified'}
        
        Please provide a concise summary (max 150 words) explaining why this candidate is a good fit for the role. 
        Focus on the specific skills that match the job requirements and how their experience aligns with the position. 
        Be specific about the skill matches found and how they relate to the job responsibilities.
        """
        
        return enhanced_prompt.strip()

# Global instance for reuse
skill_extractor = SkillExtractor()
