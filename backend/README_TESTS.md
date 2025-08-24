# 🧪 Marsiya LLM NER Backend Tests

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Categories
```bash
# Core functionality tests
python -m pytest tests/unit/core/ -v

# User management tests  
python -m pytest tests/unit/users/ -v

# Entity management tests
python -m pytest tests/unit/entities/ -v

# LLM integration tests
python -m pytest tests/unit/llm_integration/ -v
```

### Run Individual Test Files
```bash
# Core models
python -m pytest tests/unit/core/test_core_models.py -v

# User models
python -m pytest tests/unit/users/test_user_models.py -v

# Entity models
python -m pytest tests/unit/entities/test_entity_models.py -v

# LLM services
python -m pytest tests/unit/llm_integration/test_llm_services.py -v
```

### Run Specific Tests
```bash
# Specific test class
python -m pytest tests/unit/core/test_core_models.py::TestAuditLog -v

# Specific test method
python -m pytest tests/unit/core/test_core_models.py::TestAuditLog::test_audit_log_creation -v
```

## Test Coverage

### ✅ Core App (14 tests)
- TimestampedModel, SoftDeleteModel, UserStampedModel
- Complete AuditLog functionality

### ✅ Users App (Comprehensive)
- User creation, validation, and management
- UserProfile with research interests and preferences

### ✅ Entities App (Comprehensive)  
- EntityType classification and validation
- Entity creation, positioning, and verification
- EntityRelationship management

### ✅ LLM Integration (Comprehensive)
- PromptConfiguration with 4 prompt types
- LLMService with OpenAI/Anthropic support
- Entity extraction pipeline

## Test Results
All tests are currently **PASSING** ✅

## Coverage Report
Run with coverage to see detailed analysis:
```bash
python -m pytest tests/ -v --cov=. --cov-report=html
```

## Test Quality
- **Comprehensive Coverage**: All core functionality tested
- **Well Documented**: Clear test descriptions and examples  
- **Maintainable**: Easy to extend and modify
- **Fast Execution**: Efficient test runs
- **Real-world Scenarios**: Tests cover actual usage patterns
