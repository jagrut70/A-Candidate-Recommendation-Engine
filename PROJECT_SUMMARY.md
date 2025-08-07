# Candidate Recommendation Engine - Project Summary

## ✅ Requirements Fulfilled

### Core Requirements
- ✅ **Accept job description as text input** - Beautiful textarea in the web interface
- ✅ **Accept candidate resumes via file upload** - Support for TXT, PDF, DOC, DOCX files
- ✅ **Accept candidate resumes via manual input** - Tabbed interface for both methods
- ✅ **Generate embeddings** - Using sentence-transformers library (all-MiniLM-L6-v2)
- ✅ **Compute cosine similarity** - Using scikit-learn's cosine_similarity function
- ✅ **Display top 5-10 most relevant candidates** - Shows up to 10 candidates ranked by relevance
- ✅ **Show candidate name/ID** - Displays candidate names and filenames
- ✅ **Show similarity score** - Percentage-based similarity scores (0-100%)

### Bonus Requirements
- ✅ **AI-generated summary** - Uses OpenAI GPT-3.5-turbo to explain why each candidate is a good fit
- ✅ **Easy-to-interact demo** - Modern, responsive web interface with intuitive UX

## 🏗️ Architecture Overview

### Backend (Flask)
- **app.py**: Main Flask application with all routes and business logic
- **Embedding Generation**: Uses sentence-transformers for semantic understanding
- **Similarity Computation**: Cosine similarity between job and resume embeddings
- **AI Summaries**: OpenAI integration for professional candidate analysis
- **File Handling**: Secure file uploads with validation

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Modern, responsive web interface
- **static/css/style.css**: Beautiful styling with gradients and animations
- **static/js/app.js**: Interactive functionality and API communication

### Key Features
1. **Dual Input Methods**: File upload and manual text input
2. **Real-time Validation**: Form validation and user feedback
3. **Loading States**: Professional loading animations
4. **Responsive Design**: Works on desktop, tablet, and mobile
5. **Error Handling**: Comprehensive error messages and recovery
6. **AI Integration**: Optional OpenAI API for intelligent summaries

## 🚀 How to Run

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Open browser to http://localhost:5000
```

### With AI Summaries (Optional)
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Create `.env` file with your API key
3. Restart the application

## 📊 Sample Data Included

The project includes sample data for testing:
- **sample_job_description.txt**: Senior Software Engineer position
- **candidate1_resume.txt**: John Smith - Senior Software Engineer (high match)
- **candidate2_resume.txt**: Sarah Johnson - Full Stack Developer (medium match)
- **candidate3_resume.txt**: Michael Chen - Data Scientist (lower match)

## 🎯 Technical Implementation

### Embedding Process
1. **Text Preprocessing**: Clean and normalize job description and resumes
2. **Embedding Generation**: Convert text to 384-dimensional vectors using all-MiniLM-L6-v2
3. **Similarity Computation**: Calculate cosine similarity between job and each resume
4. **Ranking**: Sort candidates by similarity score (highest first)

### AI Summary Generation
- Uses OpenAI GPT-3.5-turbo with custom prompt
- Analyzes job requirements vs. candidate experience
- Generates professional 2-3 sentence summaries
- Gracefully handles API errors

### Security Features
- File type validation
- Secure filename handling
- Session management
- Input sanitization

## 🎨 User Experience

### Interface Design
- **Modern Aesthetic**: Gradient backgrounds and smooth animations
- **Intuitive Navigation**: Clear tabs and logical flow
- **Visual Feedback**: Loading states, success/error messages
- **Responsive Layout**: Adapts to different screen sizes

### User Flow
1. Enter job description
2. Choose input method (file upload or manual)
3. Upload files or enter candidate data
4. Generate recommendations
5. View ranked results with AI analysis

### Results Display
- **Similarity Scores**: Color-coded percentages (green=high, yellow=medium, red=low)
- **Top Match Highlighting**: Crown icon for best candidate
- **AI Analysis**: Professional summary for each candidate
- **File Information**: Shows original filename and processing status

## 🔧 Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: For AI summaries (optional)
- `SECRET_KEY`: Flask session security

### Model Configuration
- **Embedding Model**: all-MiniLM-L6-v2 (fast, accurate, multilingual)
- **Similarity Metric**: Cosine similarity (normalized, scale-invariant)
- **Result Limit**: Top 10 candidates (configurable)

## 📈 Performance Considerations

- **Model Loading**: Sentence transformer loaded once at startup
- **Batch Processing**: Efficient embedding generation
- **Caching**: Model embeddings cached in memory
- **Async Processing**: Non-blocking AI summary generation

## 🛠️ Extensibility

The application is designed for easy extension:
- **New File Types**: Add support for additional resume formats
- **Different Models**: Swap embedding models for different use cases
- **Additional Metrics**: Implement other similarity algorithms
- **Enhanced AI**: Add more sophisticated candidate analysis

## 🎉 Success Metrics

- ✅ **Functional Requirements**: All core requirements implemented
- ✅ **Bonus Features**: AI summaries and modern UI delivered
- ✅ **Code Quality**: Clean, well-documented, maintainable code
- ✅ **User Experience**: Intuitive, responsive, professional interface
- ✅ **Performance**: Fast processing and smooth interactions
- ✅ **Reliability**: Comprehensive error handling and validation

This Candidate Recommendation Engine successfully demonstrates modern web development practices, AI/ML integration, and user-centered design principles. 