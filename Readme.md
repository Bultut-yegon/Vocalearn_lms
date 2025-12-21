# 🎓 VocaLearn AI Services

**AI-Powered Learning Management System for TVET Education**

A comprehensive suite of AI services designed to revolutionize Technical and Vocational Education and Training (TVET) through intelligent recommendations, automated grading, and adaptive quiz generation. Built specifically for trades education including electrical wiring, plumbing, and other vocational skills.

---

##  Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Integration Guide](#-integration-guide)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

##  Features

###  AI-Powered Recommendation System
- **Personalized Learning Paths**: Analyzes student performance to create tailored study plans
- **Performance Trend Analysis**: Detects improving, declining, or stable performance patterns
- **Intelligent Prioritization**: Creates 3-tier study plans (urgent review, skill building, advancement)
- **Progress Tracking**: Monitors improvement over time with detailed comparisons
- **Motivational Insights**: Generates encouraging, context-aware feedback using LLM

###  Auto-Grading System
- **Dual Grading Modes**: 
  - Fast deterministic grading for MCQs and True/False questions
  - AI-powered evaluation for open-ended responses (essays, short answers, practical scenarios)
- **Partial Credit Support**: Fair scoring for partially correct answers
- **Detailed Feedback**: Per-question analysis with strengths and improvement areas
- **Rubric-Based Evaluation**: Consistent, criteria-driven assessment
- **Topic Mastery Analysis**: Identifies specific knowledge gaps
- **Batch Processing**: Grade entire class submissions efficiently

###  Quiz Generation System
- **One-Click Generation**: Create assessments instantly with sensible defaults
- **Adaptive Quizzes**: Personalized questions based on student performance
- **Multiple Question Types**: MCQ, True/False, Short Answer, Essay, Practical scenarios
- **Difficulty Levels**: Beginner, Intermediate, Advanced
- **Bulk Generation**: Create quizzes for multiple topics simultaneously
- **Curriculum Integration**: Incorporate reference materials and avoid covered topics
- **Smart Duration Estimation**: Calculates expected completion time

---

##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Application (Python)                │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │Recommendation│  │ Auto-Grading │  │Quiz Generator│ │
│  │   Service    │  │   Service    │  │   Service    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                     ┌──────▼──────┐                     │
│                     │  Groq API   │                     │
│                     │ (LLM Engine)│                     │
│                     └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │ REST API
                            ▼
              ┌──────────────────────────┐
              │   Spring Boot Backend    │
              │      (Java/Kotlin)       │
              └──────────────────────────┘
```

---

##  Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([Download](https://git-scm.com/downloads))
- **Groq API Key** (Free - [Sign up here](https://console.groq.com/))

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 500MB free space
- **OS**: Linux, macOS, or Windows

---

##  Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-organization/vocalearn_ai.git
cd vocalearn_ai
```

### Step 2: Create Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected installation time**: 2-3 minutes

---

##  Configuration

### Step 1: Create Environment File

Create a `.env` file in the project root:

```bash
touch .env  # Linux/macOS
# OR
type nul > .env  # Windows
```

### Step 2: Add Configuration

Open `.env` and add the following:

```env
# Required: Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: LLM Configuration
LLM_MODEL=llama-3.1-8b-instant

# Optional: Application Environment
ENV=dev

# Optional: CORS Configuration (for production)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Getting Your Groq API Key

1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

**Note**: Groq offers free API access with generous rate limits, perfect for development and production use.

---

##  Running the Application

### Start the Server

**Development Mode (with auto-reload):**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Production Mode:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Important: Create log directories first
```bash
mkdir -p logs cache
chmod 777 logs cache
docker-compose up -d
```

### Verify Server is Running

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Access API Documentation

Open your browser and visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "AI Learning Services"
}
```

---

##  API Documentation

### Base URL
```
http://localhost:8000/api
```

### Service Endpoints

#### 1. Recommendation System

**Analyze Performance**
```http
POST /api/recommendation/analyze
Content-Type: application/json

{
  "performance_history": [
    {
      "topic": "Basic Wiring",
      "score": 85,
      "max_score": 100
    }
  ],
  "topic_scores": {}
}
```

**Track Improvement**
```http
POST /api/recommendation/track-improvement
Content-Type: application/json

{
  "student_id": "ST001",
  "current_metrics": {
    "Basic Wiring": 0.85,
    "Pipe Fitting": 0.65
  },
  "previous_metrics": {
    "Basic Wiring": 0.75,
    "Pipe Fitting": 0.60
  }
}
```

**Generate Report**
```http
POST /api/recommendation/generate-report
Content-Type: application/json

{
  "student_id": "ST001",
  "student_name": "John Doe",
  "performance_history": [...],
  "topic_scores": {}
}
```

#### 2. Auto-Grading System

**Grade Submission**
```http
POST /api/autograde/grade
Content-Type: application/json

{
  "submission_id": "SUB001",
  "student_id": "ST001",
  "topic": "Basic Electrical Wiring",
  "closed_ended_questions": [
    {
      "question_id": "Q1",
      "question_text": "What is the standard residential voltage?",
      "question_type": "mcq",
      "correct_answer": "C",
      "student_answer": "C",
      "points": 5
    }
  ],
  "open_ended_questions": [
    {
      "question_id": "Q2",
      "question_text": "Explain series vs parallel circuits",
      "question_type": "short_answer",
      "rubric": "Should explain current flow and component arrangement",
      "student_answer": "In series, current flows through each component...",
      "points": 10,
      "keywords": ["series", "parallel", "current"]
    }
  ]
}
```

**Batch Grade**
```http
POST /api/autograde/grade-batch
Content-Type: application/json

[
  { submission_1 },
  { submission_2 },
  ...
]
```

#### 3. Quiz Generation System

**Quick Generate (Easiest)**
```http
POST /api/quiz/quick-generate?topic=Basic%20Wiring&difficulty=intermediate
```

**Standard Generation**
```http
POST /api/quiz/generate
Content-Type: application/json

{
  "topic": "Basic Electrical Wiring",
  "subtopics": ["Circuit Breakers", "Wire Gauges"],
  "difficulty_level": "intermediate",
  "num_mcq": 5,
  "num_true_false": 3,
  "num_short_answer": 2,
  "num_essay": 0
}
```

**Adaptive Quiz**
```http
POST /api/quiz/generate-adaptive
Content-Type: application/json

{
  "student_id": "ST001",
  "topic": "Pipe Fitting",
  "total_questions": 10,
  "recent_performance": {
    "Pipe Fitting": 55
  },
  "weak_areas": ["Pipe Threading", "Leak Detection"]
}
```

**Bulk Generation**
```http
POST /api/quiz/generate-bulk
Content-Type: application/json

{
  "topics": ["Basic Wiring", "Plumbing Basics", "Safety Procedures"],
  "questions_per_topic": 10
}
```

---

##  Usage Examples

### Example 1: Complete Learning Cycle

```bash
# Step 1: Generate a quiz
curl -X POST "http://localhost:8000/api/quiz/quick-generate?topic=Basic%20Wiring&difficulty=beginner"

# Step 2: Student takes quiz (frontend handles this)

# Step 3: Grade the submission
curl -X POST http://localhost:8000/api/autograde/grade \
  -H "Content-Type: application/json" \
  -d @submission.json

# Step 4: Get recommendations based on performance
curl -X POST http://localhost:8000/api/recommendation/analyze \
  -H "Content-Type: application/json" \
  -d @performance.json

# Step 5: Generate adaptive quiz for weak areas
curl -X POST http://localhost:8000/api/quiz/generate-adaptive \
  -H "Content-Type: application/json" \
  -d @adaptive_request.json
```

### Example 2: Batch Processing (Entire Class)

```bash
# Grade all student submissions
curl -X POST http://localhost:8000/api/autograde/grade-batch \
  -H "Content-Type: application/json" \
  -d @class_submissions.json

# Generate quizzes for all course topics
curl -X POST http://localhost:8000/api/quiz/generate-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["Wiring", "Plumbing", "Safety", "Tools"],
    "questions_per_topic": 10
  }'
```

### Example 3: Progress Tracking

```bash
# Week 1: Baseline assessment
curl -X POST http://localhost:8000/api/recommendation/analyze \
  -H "Content-Type: application/json" \
  -d @week1_performance.json

# Week 4: Track improvement
curl -X POST http://localhost:8000/api/recommendation/track-improvement \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "ST001",
    "current_metrics": {"Basic Wiring": 0.85},
    "previous_metrics": {"Basic Wiring": 0.65}
  }'
```

---

##  Integration Guide

### Spring Boot Integration

#### Step 1: Add WebClient Dependency

**Maven (pom.xml):**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

**Gradle (build.gradle):**
```gradle
implementation 'org.springframework.boot:spring-boot-starter-webflux'
```

#### Step 2: Configure AI Service Client

```java
@Configuration
public class AIServiceConfig {
    
    @Value("${ai-service.base-url}")
    private String baseUrl;
    
    @Bean
    public WebClient aiServiceClient() {
        return WebClient.builder()
            .baseUrl(baseUrl)
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }
}
```

#### Step 3: Create Service Class

```java
@Service
@Slf4j
public class AILearningService {
    
    private final WebClient aiClient;
    
    public AILearningService(WebClient aiServiceClient) {
        this.aiClient = aiServiceClient;
    }
    
    // Recommendation Service
    public Mono<RecommendationResponse> getRecommendations(
        List<PerformanceRecord> performanceHistory
    ) {
        return aiClient.post()
            .uri("/api/recommendation/analyze")
            .bodyValue(Map.of(
                "performance_history", performanceHistory,
                "topic_scores", Map.of()
            ))
            .retrieve()
            .bodyToMono(RecommendationResponse.class)
            .timeout(Duration.ofSeconds(30))
            .retry(2)
            .doOnError(e -> log.error("Recommendation service error: {}", e.getMessage()));
    }
    
    // Grading Service
    public Mono<GradingResult> gradeSubmission(GradingRequest request) {
        return aiClient.post()
            .uri("/api/autograde/grade")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(GradingResult.class)
            .timeout(Duration.ofSeconds(45))
            .retry(2);
    }
    
    // Quiz Generation Service
    public Mono<QuizResult> generateQuiz(QuizRequest request) {
        return aiClient.post()
            .uri("/api/quiz/generate")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(QuizResult.class)
            .timeout(Duration.ofSeconds(30))
            .retry(2);
    }
}
```

#### Step 4: Application Properties

**application.yml:**
```yaml
ai-service:
  base-url: http://localhost:8000
  timeout: 30s
  retry:
    max-attempts: 3
    backoff: 2s
```

#### Step 5: Controller Example

```java
@RestController
@RequestMapping("/api/student")
public class StudentController {
    
    private final AILearningService aiService;
    
    @PostMapping("/{id}/recommendations")
    public Mono<ResponseEntity<RecommendationResponse>> getRecommendations(
        @PathVariable String id,
        @RequestBody List<PerformanceRecord> history
    ) {
        return aiService.getRecommendations(history)
            .map(ResponseEntity::ok)
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }
    
    @PostMapping("/submissions/{id}/grade")
    public Mono<ResponseEntity<GradingResult>> gradeSubmission(
        @PathVariable String id,
        @RequestBody GradingRequest request
    ) {
        return aiService.gradeSubmission(request)
            .map(ResponseEntity::ok);
    }
    
    @PostMapping("/quiz/generate")
    public Mono<ResponseEntity<QuizResult>> generateQuiz(
        @RequestBody QuizRequest request
    ) {
        return aiService.generateQuiz(request)
            .map(ResponseEntity::ok);
    }
}
```

---

##  Testing

### Manual Testing with cURL

#### Test Recommendation System
```bash
curl -X POST http://localhost:8000/api/recommendation/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "performance_history": [
      {"topic": "Basic Wiring", "score": 85, "max_score": 100},
      {"topic": "Pipe Fitting", "score": 55, "max_score": 100}
    ],
    "topic_scores": {}
  }' | jq
```

#### Test Auto-Grading
```bash
curl -X POST http://localhost:8000/api/autograde/grade \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": "TEST001",
    "student_id": "ST001",
    "topic": "Basic Wiring",
    "closed_ended_questions": [
      {
        "question_id": "Q1",
        "question_text": "Test question",
        "question_type": "mcq",
        "correct_answer": "A",
        "student_answer": "A",
        "points": 5
      }
    ],
    "open_ended_questions": []
  }' | jq
```

#### Test Quiz Generation
```bash
curl -X POST "http://localhost:8000/api/quiz/quick-generate?topic=Basic%20Wiring&difficulty=intermediate" | jq
```

### Using Postman

1. Import the API collection from `/docs/postman_collection.json`
2. Set environment variable: `base_url = http://localhost:8000`
3. Run the collection tests

### Health Checks

```bash
# Overall health
curl http://localhost:8000/health

# Service-specific health
curl http://localhost:8000/api/recommendation/health
curl http://localhost:8000/api/autograde/health
curl http://localhost:8000/api/quiz/health
```

---

##  Troubleshooting

### Common Issues and Solutions

#### Issue 1: Server won't start - "No module named uvicorn"

**Problem**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue 2: "Missing GROQ_API_KEY"

**Problem**: Environment variable not set

**Solution**:
```bash
# Check if .env file exists
ls -la | grep .env

# Verify API key is set
cat .env | grep GROQ_API_KEY

# If missing, add to .env file
echo "GROQ_API_KEY=your_key_here" >> .env

# Restart server
```

#### Issue 3: Getting fallback messages instead of LLM responses

**Problem**: Groq API not accessible or rate limited

**Solution**:
```bash
# Test Groq API connectivity
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer your_api_key"

# Check server logs for detailed error
# Look for "LLM generation failed: ..." messages

# Verify API key has credits (Groq offers free tier)
# Visit https://console.groq.com/
```

#### Issue 4: "PydanticSchemaGenerationError: Unable to generate schema for <built-in function any>"

**Problem**: Type hint using lowercase `any` instead of `Any`

**Solution**:
```python
# In model files, change:
from typing import List, Dict, Optional, Any  # Add Any

# Change any lowercase 'any' to 'Any':
generation_metadata: Dict[str, Any]  # Not 'any'
```

#### Issue 5: Import errors or module not found

**Problem**: File structure or naming mismatch

**Solution**:
```bash
# Verify project structure
tree app/

# Should look like:
# app/
# ├── __init__.py
# ├── main.py
# ├── api/
# │   ├── __init__.py
# │   └── v1/
# │       ├── __init__.py
# │       ├── recommendation_router.py
# │       ├── grading_router.py
# │       └── quiz_router.py
# ├── models/
# │   ├── __init__.py
# │   ├── recommendation_models.py
# │   ├── grading_models.py
# │   └── quiz_models.py
# └── services/
#     ├── __init__.py
#     ├── recommendation_service.py
#     ├── grading_service.py
#     └── quiz_service.py

# Ensure all __init__.py files exist
find app -type d -exec touch {}/__init__.py \;
```

#### Issue 6: CORS errors when calling from frontend

**Problem**: CORS not properly configured

**Solution**:
```python
# In app/main.py, update CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue 7: Slow response times

**Problem**: Network latency or LLM processing

**Solutions**:
- Use `llama-3.1-8b-instant` model (fastest)
- Implement caching for repeated requests
- Use batch endpoints for multiple operations
- Consider async processing for heavy workloads

### Getting Help

If you encounter issues not covered here:

1. Check server logs for detailed error messages
2. Review the [API Documentation](http://localhost:8000/docs)
3. Open an issue on GitHub with:
   - Error message and stack trace
   - Steps to reproduce
   - System information (OS, Python version)
   - Contents of `.env` file (without API key)

---

##  Performance Metrics

### Expected Response Times

| Operation | Response Time | Notes |
|-----------|--------------|-------|
| MCQ/T-F Grading | < 100ms | Per question, deterministic |
| Open-ended Grading | 3-5 seconds | Per question, LLM-powered |
| Recommendation Analysis | 2-3 seconds | Depends on history size |
| Quiz Generation (10 questions) | 10-15 seconds | LLM generation |
| Quick Quiz Generate | 8-12 seconds | Default configuration |

### Scalability

- **Concurrent Requests**: Handles 100+ simultaneous requests
- **Batch Processing**: Grade 50+ submissions in under 3 minutes
- **Rate Limits**: Respects Groq's free tier limits (flexible)

---

##   Security Considerations

### Production Deployment

1. **API Key Management**
   - Never commit `.env` file to version control
   - Use environment variables or secret management services
   - Rotate API keys regularly

2. **CORS Configuration**
   ```python
   # Restrict origins in production
   allow_origins=["https://your-frontend-domain.com"]
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   
   limiter = Limiter(key_func=get_remote_address)
   
   @limiter.limit("10/minute")
   async def generate_quiz(...):
       ...
   ```

4. **Input Validation**
   - Pydantic models already validate inputs
   - Add custom validators for business logic

5. **Logging**
   - Enable structured logging in production
   - Monitor for suspicious patterns
   - Set up alerts for errors

---

##  Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t vocalearn-ai .
docker run -d -p 8000:8000 --env-file .env vocalearn-ai
```

### Cloud Deployment (AWS, GCP, Azure)

**Requirements:**
- Load balancer for scaling
- Environment variables configured
- Health check endpoint: `/health`
- Min 2GB RAM per instance

---

## Monitoring

### Key Metrics to Track

- Request latency (p50, p95, p99)
- Error rates by endpoint
- LLM API call success rate
- Queue depth (if using async processing)
- Memory and CPU usage

### Recommended Tools

- **Prometheus + Grafana**: Metrics visualization
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking
- **DataDog**: All-in-one monitoring

---

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Write tests** for new functionality
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Authors

**VocaLearn Development Team**
- Backend AI Services: Brian Yegon
- Integration Support: Meshllam Mwai, Solomon Ndimu

---

## Acknowledgments

- **Groq** for providing fast LLM inference
- **FastAPI** for the excellent web framework
- **Meta** for Llama 3.1 model
- **Pydantic** for data validation
- All contributors and testers

---

## Support

- **Email**: support@vocallearn.edu
- **Documentation**: [https://docs.vocallearn.edu](https://docs.vocallearn.edu)
- **GitHub Issues**: [Report a bug](https://github.com/your-org/vocalearn_ai/issues)
- **Slack Community**: [Join us](https://vocallearn.slack.com)

---

## Roadmap

### Q1 2025
- [ ] Multi-language support
- [ ] Custom Hugging Face model integration
- [ ] Image-based question generation
- [ ] Video assessment grading

### Q2 2025
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Offline mode capability

### Q3 2025
- [ ] Voice-based assessments
- [ ] AR/VR integration for practical skills
- [ ] Blockchain-based certification
- [ ] Peer review system

---

**Made with Love for TVET Education**

*Empowering trades education through intelligent automation*