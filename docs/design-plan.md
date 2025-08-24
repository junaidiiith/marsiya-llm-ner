# Design Plan - Urdu Marsiya NER Web Application

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend Design (Django)](#backend-design-django)
4. [Frontend Design (React)](#frontend-design-react)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [LLM Integration](#llm-integration)
8. [Security Considerations](#security-considerations)
9. [Performance & Scalability](#performance--scalability)
10. [Implementation Phases](#implementation-phases)

## Project Overview

This application helps researchers, particularly in digital humanities, to identify, annotate, and verify named entities in Urdu Marsiya poetry. The tool combines AI-powered entity recognition with human verification to ensure accuracy in identifying entities such as people, locations, dates, and more within historical and religious texts.

### Core Features

1. **Text Upload and Automated NER Tagging**

   - File upload and text paste functionality
   - LLM-based entity recognition
   - Configurable processing parameters

2. **Manual Review and Correction**

   - Interactive tagged text viewing
   - Line-by-line navigation
   - Tag verification and correction
   - Manual entity tagging

3. **Data Export and Statistics**
   - Excel export functionality
   - Statistical dashboard
   - Email integration

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend │    │  LLM APIs      │
│                 │◄──►│                 │◄──►│  (OpenAI, etc.)│
│   - Text Viewer │    │   - API Layer   │    │                 │
│   - Entity Edit │    │   - Business    │    │                 │
│   - Dashboard   │    │     Logic       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       │                 │
                       └─────────────────┘
```

### Technology Stack

- **Backend**: Django 4.2+, Django REST Framework, Celery
- **Frontend**: React 18+, Redux Toolkit, Material-UI
- **Database**: PostgreSQL (production), SQLite (development)
- **AI Integration**: OpenAI API, Anthropic API, Local LLM support
- **Deployment**: Docker, Nginx, Gunicorn
- **Task Queue**: Redis + Celery for async processing

## Backend Design (Django)

### Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── marsiya_ner/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── admin.py
│   ├── documents/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── admin.py
│   ├── entities/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── admin.py
│   ├── llm_integration/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── services.py
│   │   ├── providers/
│   │   └── admin.py
│   ├── projects/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   └── users/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       └── admin.py
├── static/
├── media/
├── templates/
└── utils/
    ├── __init__.py
    ├── text_processing.py
    ├── export_utils.py
    └── email_utils.py
```

### Django Apps Overview

#### 1. Core App

- Base models and common functionality
- User authentication and permissions
- System configuration

#### 2. Documents App

- Text file management
- Document processing pipeline
- File upload and storage

#### 3. Entities App

- Named entity storage and management
- Entity type definitions
- Entity verification workflow

#### 4. LLM Integration App

- AI model integration
- Text processing services
- Async job management

#### 5. Projects App

- Research project organization
- User collaboration features
- Project-level statistics

#### 6. Users App

- Extended user profiles
- User preferences and settings
- Activity tracking

## Frontend Design (React)

### Project Structure

```
frontend/
├── package.json
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── index.js
│   ├── App.js
│   ├── store/
│   │   ├── index.js
│   │   ├── slices/
│   │   │   ├── authSlice.js
│   │   │   ├── documentsSlice.js
│   │   │   ├── entitiesSlice.js
│   │   │   └── settingsSlice.js
│   │   └── middleware/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.js
│   │   │   ├── Sidebar.js
│   │   │   ├── Loading.js
│   │   │   └── ErrorBoundary.js
│   │   ├── documents/
│   │   │   ├── DocumentUpload.js
│   │   │   ├── DocumentList.js
│   │   │   └── DocumentCard.js
│   │   ├── entities/
│   │   │   ├── EntityTag.js
│   │   │   ├── EntityEditor.js
│   │   │   └── EntityTypeSelector.js
│   │   ├── viewer/
│   │   │   ├── TextViewer.js
│   │   │   ├── TextLine.js
│   │   │   └── NavigationControls.js
│   │   └── dashboard/
│   │       ├── StatisticsChart.js
│   │       ├── ExportModal.js
│   │       └── ProcessingStatus.js
│   ├── pages/
│   │   ├── Dashboard.js
│   │   ├── DocumentViewer.js
│   │   ├── DocumentUpload.js
│   │   ├── Settings.js
│   │   └── Login.js
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── documents.js
│   │   └── entities.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── helpers.js
│   │   └── urdu.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useDocuments.js
│   │   └── useEntities.js
│   └── styles/
│       ├── index.css
│       ├── components.css
│       └── themes.js
├── build/
└── README.md
```

### Component Architecture

#### 1. Layout Components

- **App**: Main application wrapper with routing
- **Header**: Navigation bar with user info and actions
- **Sidebar**: Project and document navigation
- **MainContent**: Dynamic content area with routing

#### 2. Page Components

- **Dashboard**: Overview with statistics and recent documents
- **DocumentUpload**: File upload and text input interface
- **DocumentViewer**: Interactive text viewing with entity editing
- **Settings**: User preferences and LLM configuration

#### 3. Feature Components

- **TextViewer**: Main text display with entity highlighting
- **EntityEditor**: Inline entity editing interface
- **ProcessingStatus**: Job progress and status indicators
- **ExportModal**: Data export options and configuration

### State Management

#### Redux Store Structure

```javascript
{
  auth: {
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  },
  documents: {
    list: [],
    current: null,
    loading: false,
    error: null,
    filters: {},
    pagination: {}
  },
  entities: {
    list: [],
    selected: null,
    editing: null,
    loading: false,
    filters: {}
  },
  processing: {
    jobs: [],
    current: null,
    progress: 0,
    status: 'idle'
  },
  settings: {
    llmModels: [],
    selectedModel: null,
    preferences: {},
    theme: 'light'
  },
  ui: {
    sidebarOpen: true,
    modals: {},
    notifications: []
  }
}
```

#### Key Actions

- **Documents**: CRUD operations, processing, export
- **Entities**: CRUD operations, verification, bulk operations
- **Processing**: Job management, progress tracking
- **Settings**: User preferences, LLM configuration

## Database Design

### Core Models

#### User Model

```python
class User(AbstractUser):
    bio = models.TextField(blank=True)
    research_interests = models.JSONField(default=list)
    preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Project Model

```python
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Document Model

```python
class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    file_path = models.FileField(upload_to='documents/', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Entity Model

```python
class Entity(models.Model):
    text = models.CharField(max_length=500)
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    start_position = models.IntegerField()
    end_position = models.IntegerField()
    confidence_score = models.FloatField()
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### EntityType Model

```python
class EntityType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    color_code = models.CharField(max_length=7)  # Hex color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### LLMModel Model

```python
class LLMModel(models.Model):
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50)
    api_key = models.CharField(max_length=500)
    model_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### ProcessingJob Model

```python
class ProcessingJob(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    llm_model = models.ForeignKey(LLMModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES)
    progress = models.IntegerField(default=0)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### Database Relationships

- **User ↔ Project**: Many-to-Many (users can work on multiple projects)
- **Project → Document**: One-to-Many (each project has multiple documents)
- **Document → Entity**: One-to-Many (each document has multiple entities)
- **Entity → EntityType**: Many-to-One (each entity has one type)
- **Document → ProcessingJob**: One-to-Many (each document can have multiple processing jobs)

## API Design

### Authentication Endpoints

```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/logout/         # User logout
POST /api/auth/refresh/        # Refresh JWT token
GET  /api/auth/profile/        # Get user profile
PUT  /api/auth/profile/        # Update user profile
```

### Document Endpoints

```
GET    /api/documents/                    # List documents
POST   /api/documents/                    # Create document
GET    /api/documents/{id}/               # Get document details
PUT    /api/documents/{id}/               # Update document
DELETE /api/documents/{id}/               # Delete document
POST   /api/documents/{id}/process/       # Start NER processing
GET    /api/documents/{id}/entities/      # Get document entities
GET    /api/documents/{id}/stats/         # Get document statistics
GET    /api/documents/{id}/export/excel/  # Export to Excel
POST   /api/documents/{id}/export/email/  # Send via email
```

### Entity Endpoints

```
GET    /api/entities/                     # List entities
POST   /api/entities/                     # Create entity
GET    /api/entities/{id}/                # Get entity details
PUT    /api/entities/{id}/                # Update entity
DELETE /api/entities/{id}/                # Delete entity
POST   /api/entities/{id}/verify/         # Mark entity as verified
POST   /api/entities/bulk-verify/         # Bulk verify entities
POST   /api/entities/bulk-update/         # Bulk update entities
```

### Project Endpoints

```
GET    /api/projects/                     # List projects
POST   /api/projects/                     # Create project
GET    /api/projects/{id}/                # Get project details
PUT    /api/projects/{id}/                # Update project
DELETE /api/projects/{id}/                # Delete project
GET    /api/projects/{id}/stats/          # Get project statistics
POST   /api/projects/{id}/users/          # Add user to project
DELETE /api/projects/{id}/users/{user_id}/ # Remove user from project
```

### LLM Integration Endpoints

```
GET    /api/llm-models/                   # List available LLM models
POST   /api/llm-models/                   # Create LLM model
GET    /api/llm-models/{id}/              # Get LLM model details
PUT    /api/llm-models/{id}/              # Update LLM model
DELETE /api/llm-models/{id}/              # Delete LLM model
POST   /api/llm-models/{id}/test/         # Test LLM model connection
```

### Processing Endpoints

```
GET    /api/processing/jobs/              # List processing jobs
GET    /api/processing/jobs/{id}/         # Get job details
GET    /api/processing/jobs/{id}/status/  # Get job status
DELETE /api/processing/jobs/{id}/         # Cancel job
```

## LLM Integration

### Provider Architecture

```
LLMIntegrationService
├── BaseProvider (abstract)
├── OpenAIProvider
├── AnthropicProvider
├── LocalLLMProvider
└── ProviderFactory
```

### Text Processing Pipeline

1. **Text Preprocessing**

   - Clean and normalize Urdu text
   - Split into manageable chunks
   - Preserve line breaks and formatting

2. **Entity Extraction**

   - Send chunks to LLM API
   - Parse entity responses
   - Calculate confidence scores
   - Handle API rate limits and errors

3. **Post-processing**
   - Merge overlapping entities
   - Validate entity boundaries
   - Apply business rules
   - Store results in database

### Async Processing

- **Celery Tasks**: Handle long-running NER processing
- **Progress Tracking**: Real-time updates via WebSockets
- **Error Handling**: Graceful fallbacks and retry mechanisms
- **Queue Management**: Prioritize jobs and handle failures

## Security Considerations

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: User, researcher, admin roles
- **Project-level Permissions**: Control access to research data
- **Session Management**: Secure session handling

### Data Protection

- **Input Validation**: Sanitize all user inputs
- **File Upload Security**: Validate file types and sizes
- **SQL Injection Prevention**: Use Django ORM safely
- **XSS Protection**: Sanitize output data

### API Security

- **Rate Limiting**: Prevent API abuse
- **CORS Configuration**: Control cross-origin requests
- **HTTPS Enforcement**: Secure data transmission
- **API Key Management**: Secure LLM API credentials

## Performance & Scalability

### Database Optimization

- **Indexing**: Strategic database indexes
- **Query Optimization**: Efficient database queries
- **Connection Pooling**: Database connection management
- **Caching**: Redis-based caching strategy

### Frontend Performance

- **Virtual Scrolling**: Handle large text documents
- **Lazy Loading**: Load components on demand
- **Memoization**: Optimize React component rendering
- **Bundle Optimization**: Code splitting and tree shaking

### Backend Performance

- **Async Processing**: Non-blocking operations
- **Caching Layers**: Multiple caching strategies
- **Database Optimization**: Efficient data access patterns
- **Load Balancing**: Horizontal scaling preparation

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

- [ ] Django project setup
- [ ] Basic models and database
- [ ] User authentication system
- [ ] Simple API endpoints
- [ ] Basic React frontend setup

### Phase 2: Core Features (Weeks 3-4)

- [ ] Document upload and storage
- [ ] Basic entity management
- [ ] LLM integration service
- [ ] Text processing pipeline
- [ ] Frontend document viewer

### Phase 3: Interactive Features (Weeks 5-6)

- [ ] Entity editing interface
- [ ] Line-by-line navigation
- [ ] Real-time updates
- [ ] Processing status tracking
- [ ] Basic statistics

### Phase 4: Advanced Features (Weeks 7-8)

- [ ] Export functionality
- [ ] Email integration
- [ ] Advanced statistics dashboard
- [ ] User collaboration features
- [ ] Performance optimization

### Phase 5: Polish & Testing (Weeks 9-10)

- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Testing and bug fixes
- [ ] Documentation
- [ ] Deployment preparation

### Phase 6: Deployment & Launch (Weeks 11-12)

- [ ] Production deployment
- [ ] Performance monitoring
- [ ] User training materials
- [ ] Launch and support

## Success Metrics

### Technical Metrics

- **Response Time**: API endpoints < 200ms
- **Processing Speed**: NER processing < 30 seconds per document
- **Uptime**: 99.9% availability
- **Error Rate**: < 1% API errors

### User Experience Metrics

- **Task Completion**: 90% success rate for entity tagging
- **User Satisfaction**: > 4.5/5 rating
- **Adoption Rate**: 80% of target users within 3 months
- **Training Time**: New users productive within 30 minutes

## Risk Assessment

### Technical Risks

- **LLM API Limitations**: Rate limits and cost management
- **Performance Issues**: Large document processing
- **Data Security**: Sensitive research data protection

### Mitigation Strategies

- **Multiple LLM Providers**: Fallback options
- **Progressive Enhancement**: Graceful degradation
- **Security Audits**: Regular security reviews
- **Performance Monitoring**: Continuous optimization

## Conclusion

This design plan provides a comprehensive foundation for building the Urdu Marsiya NER web application. The modular architecture ensures scalability and maintainability, while the phased implementation approach allows for iterative development and testing.

The combination of Django backend and React frontend provides a robust, modern web application framework that can handle the complex requirements of text processing, entity management, and user collaboration.

Next steps involve reviewing this plan, gathering feedback, and beginning implementation according to the outlined phases.
