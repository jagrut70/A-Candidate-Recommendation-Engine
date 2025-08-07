# AI Candidate Recommendation Engine

A sophisticated web application that uses AI and machine learning to match job candidates with job descriptions. The application generates embeddings for both job descriptions and candidate resumes, computes similarity scores, and provides AI-generated summaries explaining why each candidate is a great fit for the role.

## 🌟 Features

- **Job Description Input**: Rich text input with character counting and validation
- **Dual Resume Input Methods**: 
  - File upload (TXT, PDF, DOC, DOCX) with drag & drop
  - Manual text input for multiple candidates
- **AI-Powered Matching**: Uses state-of-the-art sentence transformers for semantic matching
- **Cosine Similarity Scoring**: Accurate ranking algorithm with 0-100% match scores
- **AI-Generated Summaries**: GPT-3.5-turbo powered analysis explaining candidate fit
- **Modern UI/UX**: Professional, responsive design with smooth animations
- **Real-time Processing**: Live feedback and progress indicators

## 🏗️ Technical Approach

### Architecture
- **Backend**: Flask (Python) web framework
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML Stack**: 
  - `sentence-transformers` with `all-MiniLM-L6-v2` for embeddings
  - `scikit-learn` for cosine similarity computation
  - OpenAI GPT-3.5-turbo for AI summaries
- **Styling**: Custom CSS with modern design system, animations, and responsive layout

### Core Algorithm
1. **Text Processing**: Extract and clean text from job descriptions and resumes
2. **Embedding Generation**: Convert text to high-dimensional vectors using transformer model
3. **Similarity Computation**: Calculate cosine similarity between job and candidate embeddings
4. **Ranking**: Sort candidates by similarity score (highest first)
5. **AI Analysis**: Generate contextual summaries using GPT-3.5-turbo
6. **Results Display**: Present top 5-10 candidates with scores and analysis

### Key Implementation Decisions
- **Embedding Model**: Chose `all-MiniLM-L6-v2` for its balance of performance and speed
- **Similarity Metric**: Cosine similarity for its effectiveness with high-dimensional vectors
- **AI Summary Length**: Limited to 150 tokens for concise, actionable insights
- **Session Management**: Flask sessions for data persistence during user interaction
- **Error Handling**: Comprehensive error handling with user-friendly messages

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for AI summaries)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Home-Assignment
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:8080`
   - The application will be ready to use!

### Environment Variables
Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

## 📁 Project Structure

```
Home-Assignment/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── run.py                # Application entry point
├── env_example.txt       # Environment variables template
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Main application template
├── static/
│   ├── css/
│   │   └── style.css    # Application styles
│   └── js/
│       └── app.js       # Frontend JavaScript
├── uploads/             # Temporary file storage
└── sample_data/         # Sample job descriptions and resumes
    ├── sample_job_description.txt
    ├── candidate1_resume.txt
    ├── candidate2_resume.txt
    └── candidate3_resume.txt
```

## 🎯 Usage Instructions

### 1. Enter Job Description
- Type or paste a detailed job description in the left panel
- Include required skills, experience, and responsibilities
- The more specific you are, the better the matches

### 2. Upload Candidate Resumes
**Option A: File Upload**
- Click the "File Upload" tab
- Drag and drop resume files or click to browse
- Supported formats: TXT, PDF, DOC, DOCX
- Click "Upload Files" to process

**Option B: Manual Input**
- Click the "Manual Input" tab
- Enter candidate name and resume content
- Click "Add Candidate" for each candidate
- Click "Process Input" when done

### 3. Generate Recommendations
- Click "Generate Recommendations"
- Wait for AI processing (typically 10-30 seconds)
- View results with similarity scores and AI analysis

### 4. Review Results
- Top candidates are ranked by similarity score
- Each result shows:
  - Candidate name and ID
  - Match percentage (0-100%)
  - AI-generated summary explaining the fit

## 🔧 Configuration

### OpenAI API Setup
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Generate an API key
3. Add the key to your `.env` file
4. The AI summary feature will be enabled

### Customization Options
- **Model Selection**: Change embedding model in `app.py`
- **Summary Length**: Adjust token limit in AI summary generation
- **UI Styling**: Modify `static/css/style.css` for custom appearance
- **Port Configuration**: Change port in `app.py` if needed

## 🧪 Testing

### Sample Data
The application includes sample data for testing:
- `sample_job_description.txt`: Example job posting
- `candidate1_resume.txt`: Senior Software Engineer resume
- `candidate2_resume.txt`: Full Stack Developer resume  
- `candidate3_resume.txt`: Data Scientist resume

### Test Workflow
1. Load the sample job description
2. Upload the sample candidate resumes
3. Generate recommendations
4. Verify similarity scores and AI summaries

## 🚨 Important Assumptions

### Technical Assumptions
- **Text Quality**: Assumes job descriptions and resumes contain meaningful text content
- **Language**: Optimized for English text (embedding model is English-based)
- **File Size**: Assumes reasonable file sizes for processing (typically < 5MB)
- **API Limits**: Assumes OpenAI API has sufficient quota for AI summaries

### Business Assumptions
- **Relevance**: Assumes that semantic similarity correlates with job fit
- **Completeness**: Assumes resumes contain sufficient information for meaningful analysis
- **Accuracy**: Assumes job descriptions accurately reflect position requirements

## ⚠️ Limitations & Considerations

### Technical Limitations
- **Language Support**: Currently optimized for English text only
- **File Formats**: Limited to common text-based formats
- **Processing Time**: AI summary generation depends on OpenAI API response times
- **API Dependencies**: Requires active internet connection for AI features

### Security Considerations
- **File Upload**: Basic file validation implemented
- **API Keys**: Store securely and never commit to version control
- **Session Data**: Temporary storage, not persistent across server restarts

### Performance Notes
- **Embedding Generation**: First-time model loading may take 10-30 seconds
- **Batch Processing**: Multiple candidates processed sequentially
- **Memory Usage**: Embedding model requires ~100MB RAM

## 🐛 Troubleshooting

### Common Issues

**"AI summary unavailable"**
- Check OpenAI API key is set correctly
- Verify internet connection
- Ensure API quota is available

**"No candidates found"**
- Verify files uploaded successfully
- Check file format is supported
- Ensure resume content is text-based

**"Port already in use"**
- Change port in `app.py` (line with `app.run()`)
- Or stop other applications using port 8080

**"Module not found"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version compatibility

### Debug Mode
Enable debug mode by setting `debug=True` in `app.py` for detailed error messages.

## 📊 Performance Metrics

### Typical Processing Times
- **Embedding Generation**: 2-5 seconds per document
- **Similarity Computation**: < 1 second for 10 candidates
- **AI Summary Generation**: 5-15 seconds per candidate
- **Total Processing**: 15-60 seconds for 3-5 candidates

### Accuracy Considerations
- **Semantic Matching**: Based on meaning, not exact keyword matching
- **Context Awareness**: Embeddings capture contextual relationships
- **Score Interpretation**: Higher scores indicate better semantic similarity

## 🔮 Future Enhancements

### Potential Improvements
- **Multi-language Support**: Add support for other languages
- **Advanced Filtering**: Add filters for experience level, location, etc.
- **Batch Processing**: Optimize for larger candidate pools
- **Custom Models**: Fine-tune embedding models for specific domains
- **Analytics Dashboard**: Add detailed matching analytics
- **Export Features**: Allow exporting results to various formats

### Scalability Considerations
- **Database Integration**: Add persistent storage for large datasets
- **Caching**: Implement caching for repeated queries
- **Async Processing**: Move to async processing for better performance
- **Microservices**: Split into separate services for better scaling

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Test with sample data to verify functionality
4. Check system requirements and dependencies

## 📄 License

This project is created for educational and demonstration purposes. Please ensure compliance with OpenAI's usage policies and any applicable data protection regulations when using this application.

---

**Built with ❤️ using Flask, Python, and modern web technologies** 