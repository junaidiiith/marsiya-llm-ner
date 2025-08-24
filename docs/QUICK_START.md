# Quick Start Guide - Marsiya LLM NER

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd marsiya-llm-ner/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# At minimum, set a SECRET_KEY
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 3. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py setup_initial_data
```

### 4. Run Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Admin Interface**: http://localhost:8000/admin/
- **API Base**: http://localhost:8000/api/

## 🏗️ What's Available

### Admin Interface

- **Users**: Manage researchers and administrators
- **Projects**: Create and manage research projects
- **Documents**: Upload and manage text documents
- **Entities**: View and manage extracted entities
- **LLM Models**: Configure AI model providers
- **Processing Jobs**: Monitor background tasks

### Database Models

- **User Management**: Custom user model with research fields
- **Project System**: Multi-user project collaboration
- **Document Processing**: Text upload and version control
- **Entity Extraction**: Named entity storage and relationships
- **LLM Integration**: Multi-provider AI model support
- **Audit System**: Complete activity logging

### Initial Data

- **7 Entity Types**: PERSON, LOCATION, DATE, TIME, ORGANIZATION, DESIGNATION, NUMBER
- **2 LLM Models**: OpenAI GPT-4 and Anthropic Claude configurations
- **2 Processing Configs**: Marsiya NER and General NER setups

## 🔧 Development Workflow

### 1. Model Changes

```bash
# After modifying models
python manage.py makemigrations
python manage.py migrate
```

### 2. Admin Updates

```bash
# After adding new models to admin.py
python manage.py collectstatic  # If needed
```

### 3. Testing

```bash
# Run Django tests
python manage.py test

# Check for issues
python manage.py check
```

## 📁 Project Structure

```
backend/
├── marsiya_ner/          # Main project settings
├── core/                 # Base models and audit
├── users/                # User management
├── projects/             # Project system
├── documents/            # Document handling
├── entities/             # Entity management
├── llm_integration/      # AI integration
├── processing/           # Background jobs
├── manage.py            # Django management
└── requirements.txt     # Dependencies
```

## 🎯 Next Steps

### Immediate (This Week)

1. **API Development**: Implement REST endpoints
2. **Serializers**: Create data serialization
3. **Permissions**: Add access control

### Short Term (Next 2 Weeks)

1. **LLM Integration**: Implement provider system
2. **Text Processing**: Add entity extraction
3. **Background Tasks**: Set up Celery workers

### Medium Term (Next Month)

1. **Frontend Development**: React application
2. **Real-time Features**: WebSocket integration
3. **Advanced UI**: Entity viewer and editor

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**: Delete migrations folder and recreate
2. **Import Errors**: Check circular imports in models
3. **Admin Issues**: Ensure models are registered in admin.py

### Debug Mode

```bash
# Enable debug logging
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver
```

## 📚 Documentation

- **Design Plan**: `docs/design-plan.md`
- **API Documentation**: `docs/api-documentation.md`
- **Database Schema**: `docs/database-schema.md`
- **User Guide**: `docs/user-guide.md`

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## 📞 Support

- Check the documentation in the `docs/` folder
- Review the project status in `PROJECT_STATUS.md`
- Create issues for bugs or feature requests

