# VocaLearn AI Services

**AI-Powered Learning Management System for TVET Education**

A comprehensive suite of AI services designed to revolutionize Technical and Vocational Education and Training (TVET) through intelligent quiz generation, automated grading, and personalized recommendations. Built specifically for trades education including electrical wiring, plumbing, HVAC, and other vocational skills.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

##  Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Services Overview](#-services-overview)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Integration Guide](#-integration-guide)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

##  Features

###  AI-Powered Quiz Generation
- **Instant Quiz Creation**: Generate comprehensive assessments from course content in seconds
- **Multiple Question Types**: MCQ, True/False, Short Answer
- **Difficulty Levels**: Beginner, Intermediate, Advanced
- **Content-Based Generation**: Questions derived directly from learning materials
- **Smart Distractors**: AI-generated plausible wrong answers for MCQs
- **Rubric Creation**: Automatic grading criteria for open-ended questions

###  Intelligent Auto-Grading System
- **Dual Grading Modes**: 
  - **Deterministic**: Instant grading for MCQs and True/False (< 100ms)
  - **AI-Powered**: LLM evaluation for short answers and essays (3-5 seconds)
- **Fair Partial Credit**: Rewards partially correct answers appropriately
- **Detailed Feedback**: Specific strengths and improvement areas per question
- **Keyword Fallback**: Ensures grading works even without LLM access
- **Batch Processing**: Grade entire class submissions efficiently
- **Letter Grades**: Automatic A-F grade assignment

### 🎓 Content-Aware Recommendation System
- **Module-Level Analysis**: Individual feedback for each learning module
- **Specific Content References**: No generic "review module 1" - tells students exactly what topics to study
- **Actionable Study Plans**: Concrete steps like "memorize AWG/ampacity pairs, practice RMS calculations"
- **Question-Level Insights**: Shows actual questions missed for targeted review
- **Performance Tracking**: Overall scores and weak question type identification
- **AI-Generated Feedback**: Personalized, encouraging insights using LLM
- **No Redundancy**: Clean output focused on what matters

---

##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Application (Python 3.11+)         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Quiz      │  │   Grading    │  │Recommendation│ │
│  │  Generation  │  │   Service    │  │   Service    │ │
│  │   Service    │  │              │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                     ┌──────▼──────┐                     │
│                     │  Groq API   │                     │
│                     │(Llama 3.1/  │                     │
│                     │  3.3 LLMs)  │                     │
│                     └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │ REST API
                            ▼
              ┌──────────────────────────┐
              │   Spring Boot Backend    │
              │        (LMS Backend)     │
              └──────────────────────────┘
```

**Technology Stack:**
- **Framework**: FastAPI (async, high-performance)
- **LLM Provider**: Groq (fast inference, free tier available)
- **Models**: Llama 3.1 (8B) for recommendations/grading, Llama 3.3 (70B) for quiz generation
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async)
- **Environment**: python-dotenv

---

##  Prerequisites

### Required Software
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([Download](https://git-scm.com/downloads))
- **Groq API Key** ([Free Sign-up](https://console.groq.com/))

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **OS**: Linux, macOS, or Windows 10+
- **Internet**: Required for LLM API calls

---

##  Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-organization/vocalearn_ai.git
cd vocalearn_ai
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Installation time**: ~2-3 minutes

**Verify installation:**
```bash
pip list | grep -E "fastapi|uvicorn|groq|pydantic|httpx"
```

---

##  Configuration

### Step 1: Create Environment File

```bash
# Linux/macOS
touch .env

# Windows
type nul > .env
```

### Step 2: Configure Settings

Add to `.env`:

```env
# Required: Groq API Configuration
GROQAPI_KEY=your_groq_api_key_here

# Optional: Model Configuration
LLM_MODEL=llama-3.1-8b-instant

# Optional: Environment
ENV=dev

# Optional: CORS (for production)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Getting Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Create free account
3. Navigate to "API Keys"
4. Generate new key
5. Copy to `.env` file

**Note**: Groq offers generous free tier - perfect for development and production.

---

##  Running the Application

### Development Mode (with auto-reload)

```bash
python main.py
```

Or:

```bash
uvicorn app.main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Recommended for Production)

```bash
# Build image
docker build -t vocalearn-ai .

# Run container
docker run -d -p 8000:8000 --env-file .env vocalearn-ai
```

### Verify Server is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Learning Services",
  "version": "1.0.0"
}
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/

---

##  Services Overview

### 1. Quiz Generation Service

**Purpose**: Generate educational assessments from course content

**Features**:
- Multiple choice questions with 4 options
- True/False statements with explanations
- Short answer questions with rubrics
- Content-aware generation (questions based on actual material)
- Difficulty level control
- JSON output format

**Models Used**: Llama 3.3 70B Versatile (high quality generation)

**Sample Output**:
```json
{
  "quiz_id": "quiz_abc123def456",
  "difficulty_level": "intermediate",
  "multiple_choice": [
    {
      "question": "What is the primary function of a circuit breaker?",
      "options": {
        "A": "Store electricity",
        "B": "Protect from overcurrent",
        "C": "Convert voltage",
        "D": "Generate power"
      },
      "correct_answer": "B",
      "explanation": "Circuit breakers protect circuits from overcurrent..."
    }
  ],
  "true_false": [...],
  "short_answer": [...],
  "total_questions": 10
}
```

### 2. Grading Service

**Purpose**: Automatically grade student quiz submissions

**Features**:
- **Closed-ended grading**: MCQ and True/False (instant)
- **Open-ended grading**: Short answers using LLM evaluation
- **Partial credit**: Fair scoring for partially correct answers
- **Detailed feedback**: Per-question strengths and improvements
- **Fallback grading**: Keyword matching when LLM unavailable
- **Letter grades**: Automatic A-F assignment

**Models Used**: Llama 3.1 8B Instant (fast, accurate evaluation)

**Grading Scale**:
- A: 90-100%
- B: 80-89%
- C: 70-79%
- D: 60-69%
- F: Below 60%

**Sample Output**:
```json
{
  "submission_id": "sub_001",
  "student_id": "student_123",
  "total_points": 85.5,
  "max_points": 100,
  "percentage": 85.5,
  "grade_letter": "B",
  "question_results": [
    {
      "question_id": "q1",
      "awarded_points": 5,
      "max_points": 5,
      "is_correct": true,
      "feedback": "Correct! Well done."
    }
  ]
}
```

### 3. Recommendation Service

**Purpose**: Provide personalized, content-specific learning recommendations

**Features**:
- **Module-level analysis**: Individual feedback per module
- **Content-specific gaps**: Identifies exact topics needing review (e.g., "AWG wire sizing", "RMS calculations")
- **Actionable recommendations**: Concrete study steps, not generic advice
- **Question review**: Shows actual failed questions for targeted practice
- **AI-generated insights**: Personalized feedback and encouragement
- **Performance tracking**: Overall scores and weak question types

**Models Used**: Llama 3.1 8B Instant (personalized feedback generation)

**Key Difference**: Unlike generic systems, this tells students EXACTLY what content to study:
-  Generic: "Review Module 1 and Module 2"
-  Specific: "Master the AWG wire numbering system (smaller numbers = larger wires), ampacity ratings (14 AWG = 15A, 12 AWG = 20A), and I²R heating physics"

**Sample Output**:
```json
{
  "student_id": "student_123",
  "individual_module_reviews": [
    {
      "module_id": "wire_101",
      "module_name": "Wire Sizing",
      "score": "15/30",
      "percentage": 50.0,
      "performance_level": "Needs Improvement",
      "feedback": "You're struggling with AWG numbering...",
      "concepts_to_review": [
        "In the AWG system, does a smaller number indicate...",
        "What is the ampacity rating for 14 AWG..."
      ]
    }
  ],
  "collective_feedback": {
    "overall_performance": {
      "total_score": 45,
      "total_max": 100,
      "percentage": 45.0,
      "level": "Needs Improvement"
    },
    "critical_gaps": "You need to master the AWG wire numbering system (smaller numbers = larger wires), ampacity ratings (14 AWG = 15A, 12 AWG = 20A), the physics of why undersized wires create fire hazards through I²R heating...",
    "recommendations": "Create flashcards for AWG/ampacity pairs. Draw diagrams showing wire sizing relationships. Practice I²R power loss calculations...",
    "weak_question_types": [
      {"type": "short_answer", "percentage": 40.0, "attempted": 10}
    ]
  }
}
```

---

##  API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

---

### Quiz Generation Endpoints

#### Generate Weekly Quiz

**Endpoint**: `POST /api/v1/quiz/generate-weekly`

**Request**:
```json
{
  "combined_content": "Electrical Safety: PPE includes insulated gloves, safety glasses...",
  "difficulty_level": "intermediate",
  "num_mcq": 5,
  "num_true_false": 3,
  "num_short_answer": 2
}
```

**Response**: Quiz with MCQ, T/F, and short answer questions

**Use Case**: Generate a complete weekly assessment from module content

---

### Grading Endpoints

#### Grade Quiz Submission

**Endpoint**: `POST /api/v1/grading/grade`

**Request**:
```json
{
  "submission_id": "sub_001",
  "student_id": "student_123",
  "quiz_data": {
    "quiz_id": "quiz_001",
    "multiple_choice": [...],
    "true_false": [...],
    "short_answer": [...]
  },
  "student_answers": {
    "mcq_0": "B",
    "tf_0": "true",
    "sa_0": "Circuit breakers protect from overcurrent..."
  }
}
```

**Response**: Graded results with scores, feedback, and letter grade

**Use Case**: Grade a student's quiz submission automatically

---

### Recommendation Endpoints

#### Analyze Student Performance

**Endpoint**: `POST /api/v1/recommendations/analyze`

**Request**:
```json
{
  "student_id": "student_123",
  "modules": [
    {
      "module_id": "safety_101",
      "module_name": "Electrical Safety",
      "module_content": "Working with electricity requires strict adherence...",
      "max_score": 25,
      "question_results": [
        {
          "question_text": "What is LOTO?",
          "student_answer": "Lockout Tagout",
          "correct_answer": "Lockout/Tagout - ensures energy sources are isolated",
          "awarded_marks": 4,
          "max_marks": 5,
          "question_type": "short_answer",
          "is_correct": true
        }
      ]
    }
  ]
}
```

**Response**: Individual module reviews + collective feedback with specific study recommendations

**Use Case**: Get personalized learning recommendations after quiz completion

---

##  Usage Examples

### Complete Learning Workflow

```bash
# 1. Generate Quiz from Content
curl -X POST http://localhost:8000/api/v1/quiz/generate-weekly \
  -H "Content-Type: application/json" \
  -d '{
    "combined_content": "Your module content here...",
    "difficulty_level": "intermediate",
    "num_mcq": 5,
    "num_true_false": 3,
    "num_short_answer": 2
  }'

# 2. Student Takes Quiz (Frontend handles this)

# 3. Grade Submission
curl -X POST http://localhost:8000/api/v1/grading/grade \
  -H "Content-Type: application/json" \
  -d @submission.json

# 4. Get Personalized Recommendations
curl -X POST http://localhost:8000/api/v1/recommendations/analyze \
  -H "Content-Type: application/json" \
  -d @recommendation_request.json
```

### Python Client Example

```python
import httpx
import asyncio

async def complete_assessment_cycle():
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. Generate Quiz
        quiz_response = await client.post(
            f"{base_url}/quiz/generate-weekly",
            json={
                "combined_content": "Module content...",
                "difficulty_level": "intermediate",
                "num_mcq": 5,
                "num_true_false": 3,
                "num_short_answer": 2
            }
        )
        quiz_data = quiz_response.json()
        
        # 2. Student submits answers (simulated)
        student_answers = {
            "mcq_0": "B",
            "tf_0": "true",
            "sa_0": "My answer..."
        }
        
        # 3. Grade submission
        grading_response = await client.post(
            f"{base_url}/grading/grade",
            json={
                "submission_id": "sub_001",
                "student_id": "student_123",
                "quiz_data": quiz_data,
                "student_answers": student_answers
            }
        )
        grading_result = grading_response.json()
        
        # 4. Get recommendations
        recommendation_response = await client.post(
            f"{base_url}/recommendations/analyze",
            json={
                "student_id": "student_123",
                "modules": [{
                    "module_id": "mod_001",
                    "module_name": "Electrical Safety",
                    "module_content": "Full content...",
                    "max_score": 31,
                    "question_results": [...]
                }]
            }
        )
        recommendations = recommendation_response.json()
        
        return {
            "quiz": quiz_data,
            "grading": grading_result,
            "recommendations": recommendations
        }

# Run
results = asyncio.run(complete_assessment_cycle())
```

---

##  Integration Guide

### Spring Boot Integration

#### 1. Add Dependencies

**Maven (pom.xml)**:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

#### 2. Configure WebClient

```java
@Configuration
public class AIServiceConfig {
    
    @Value("${ai.service.base-url:http://localhost:8000}")
    private String baseUrl;
    
    @Bean
    public WebClient aiServiceClient() {
        return WebClient.builder()
            .baseUrl(baseUrl + "/api/v1")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }
}
```

#### 3. Create Service Class

```java
@Service
@Slf4j
public class VocaLearnAIService {
    
    private final WebClient aiClient;
    
    public VocaLearnAIService(WebClient aiServiceClient) {
        this.aiClient = aiServiceClient;
    }
    
    // Quiz Generation
    public Mono<QuizResponse> generateQuiz(QuizRequest request) {
        return aiClient.post()
            .uri("/quiz/generate-weekly")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(QuizResponse.class)
            .timeout(Duration.ofSeconds(30))
            .retry(2);
    }
    
    // Grading
    public Mono<GradingResult> gradeSubmission(GradingRequest request) {
        return aiClient.post()
            .uri("/grading/grade")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(GradingResult.class)
            .timeout(Duration.ofSeconds(45));
    }
    
    // Recommendations
    public Mono<RecommendationResponse> getRecommendations(
        RecommendationRequest request
    ) {
        return aiClient.post()
            .uri("/recommendations/analyze")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(RecommendationResponse.class)
            .timeout(Duration.ofSeconds(30));
    }
}
```

#### 4. Controller Example

```java
@RestController
@RequestMapping("/api/assessments")
public class AssessmentController {
    
    private final VocaLearnAIService aiService;
    
    @PostMapping("/generate-quiz")
    public Mono<ResponseEntity<QuizResponse>> generateQuiz(
        @RequestBody QuizRequest request
    ) {
        return aiService.generateQuiz(request)
            .map(ResponseEntity::ok)
            .onErrorResume(e -> {
                log.error("Quiz generation failed", e);
                return Mono.just(ResponseEntity.status(500).build());
            });
    }
    
    @PostMapping("/submissions/{id}/grade")
    public Mono<ResponseEntity<GradingResult>> gradeSubmission(
        @PathVariable String id,
        @RequestBody GradingRequest request
    ) {
        return aiService.gradeSubmission(request)
            .map(ResponseEntity::ok);
    }
    
    @PostMapping("/students/{id}/recommendations")
    public Mono<ResponseEntity<RecommendationResponse>> getRecommendations(
        @PathVariable String id,
        @RequestBody RecommendationRequest request
    ) {
        return aiService.getRecommendations(request)
            .map(ResponseEntity::ok);
    }
}
```

---

##  Testing

### Health Checks

```bash
# Overall system health
curl http://localhost:8000/health

# Service-specific health
curl http://localhost:8000/api/v1/recommendations/health
curl http://localhost:8000/api/v1/grading/health
curl http://localhost:8000/api/v1/quiz/health
```

### Test Quiz Generation

```bash
curl -X POST http://localhost:8000/api/v1/quiz/generate-weekly \
  -H "Content-Type: application/json" \
  -d '{
    "combined_content": "Test content about electrical safety",
    "difficulty_level": "beginner",
    "num_mcq": 2,
    "num_true_false": 1,
    "num_short_answer": 1
  }' | jq
```

### Test Grading

See test payload in `/docs` → POST `/api/v1/grading/grade` → "Try it out"

### Test Recommendations

See test payload in `/docs` → POST `/api/v1/recommendations/analyze` → "Try it out"

---

##  Troubleshooting

### Issue: "GROQAPI_KEY not found"

**Solution**:
```bash
# Check .env file exists
ls -la | grep .env

# Verify key is set
cat .env | grep GROQAPI_KEY

# Add if missing
echo "GROQAPI_KEY=your_key_here" >> .env

# Restart server
```

### Issue: LLM responses are slow

**Solutions**:
- Use `llama-3.1-8b-instant` for faster responses
- Check Groq API status: https://status.groq.com/
- Implement request caching for repeated content
- Consider batch processing for multiple requests

### Issue: Grading falls back to keywords

**Cause**: Groq API unreachable or rate limited

**Solution**:
```bash
# Test Groq connectivity
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQAPI_KEY"

# Check API usage: https://console.groq.com/
```

### Issue: Recommendation output has section references

**Solution**: This is fixed in the latest version. If you see section references like "(section 3.2)", update to the latest code from artifacts #2 and #3.

### Issue: Import errors

**Solution**:
```bash
# Verify structure
tree app/

# Ensure all __init__.py exist
find app -type d -exec touch {}/__init__.py \;

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

##  Deployment

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  vocalearn-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQAPI_KEY=${GROQAPI_KEY}
      - ENV=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

**Deploy**:
```bash
docker-compose up -d
```

### Cloud Deployment (AWS/GCP/Azure)

**Requirements**:
- Load balancer for horizontal scaling
- Environment variables configured securely
- Health check endpoint: `/health`
- Minimum 2GB RAM per instance
- Auto-scaling based on request rate

---

## Performance Metrics

| Operation | Response Time | Notes |
|-----------|---------------|-------|
| Quiz Generation (10 questions) | 10-15s | LLM generation |
| MCQ/T-F Grading (per question) | < 100ms | Deterministic |
| Open-ended Grading (per question) | 3-5s | LLM evaluation |
| Recommendation Analysis | 2-3s | Depends on data size |
| Health Check | < 50ms | No external calls |

**Throughput**:
- Concurrent requests: 100+
- Quiz generation: 6-8 per minute
- Grading: 50+ submissions per minute

---

##  Contributing

We welcome contributions!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

**Development Guidelines**:
- Follow PEP 8
- Add docstrings
- Write unit tests
- Update documentation

---

##  License

MIT License - see [LICENSE](LICENSE) file

---

##  Authors

**VocaLearn Development Team**
- AI Services: Brian Yegon
- Integration: Meshllam Mwai, Solomon Ndimu

---

##  Acknowledgments

- **Groq** - Fast LLM inference
- **Meta** - Llama 3.1 & 3.3 models
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- All contributors and testers

---

## Support

- **Email**: bultutyegonn@gmail.com
- **GitHub Issues**: [Report a bug](https://github.com/your-org/vocalearn_ai/issues)

---

##  Roadmap

### Q1 2025
- [ ] Support for image-based questions
- [ ] Multi-language support
- [ ] Enhanced analytics dashboard
- [ ] Batch recommendation processing

### Q2 2025
- [ ] Video-based assessments
- [ ] Real-time collaboration
- [ ] Mobile app support
- [ ] Offline mode

### Q3 2025
- [ ] Voice assessments
- [ ] AR/VR practical skill evaluation
- [ ] Advanced plagiarism detection
- [ ] Peer review system

---

**Made with  for TVET Education**

*Empowering trades education through intelligent automation*