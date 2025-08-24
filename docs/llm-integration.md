# LLM Integration - Urdu Marsiya NER Web Application

## Overview

The LLM Integration module provides a flexible, extensible system for integrating multiple AI language models to perform Named Entity Recognition (NER) on Urdu Marsiya poetry texts.

## Architecture

### Provider Pattern

```
LLMIntegrationService
├── BaseProvider (abstract)
├── OpenAIProvider
├── AnthropicProvider
├── LocalLLMProvider
└── ProviderFactory
```

### Core Components

#### BaseProvider

```python
class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def extract_entities(self, text: str, config: ProcessingConfig) -> List[Entity]:
        """Extract entities from text."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test provider connection."""
        pass
```

#### OpenAI Provider

```python
class OpenAIProvider(BaseProvider):
    """OpenAI GPT model integration."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def extract_entities(self, text: str, config: ProcessingConfig) -> List[Entity]:
        prompt = self._build_prompt(text, config)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return self._parse_response(response.choices[0].message.content)
```

## Text Processing Pipeline

### 1. Text Preprocessing

- Clean and normalize Urdu text
- Split into manageable chunks
- Preserve line breaks and formatting

### 2. Entity Extraction

- Send chunks to LLM API
- Parse entity responses
- Calculate confidence scores
- Handle API rate limits and errors

### 3. Post-processing

- Merge overlapping entities
- Validate entity boundaries
- Apply business rules
- Store results in database

## Configuration

### Processing Options

```python
@dataclass
class ProcessingConfig:
    chunk_size: int = 1000
    overlap_size: int = 100
    confidence_threshold: float = 0.7
    entity_types: List[str] = field(default_factory=list)
    enable_post_processing: bool = True
```

### Prompt Templates

The system provides four different types of prompts for entity extraction, each optimized for different use cases:

#### 1. General NER Prompt

```python
GENERAL_NER_PROMPT = """
You are an expert in Named Entity Recognition (NER).
Extract named entities from the given text in a generic way without domain-specific knowledge.

Text: {text}

Entity types to extract:
- PERSON: Names of people, individuals, characters
- LOCATION: Places, landmarks, geographical features
- DATE: Dates, time periods, specific days
- TIME: Time references and periods
- ORGANIZATION: Groups, companies, institutions, teams
- DESIGNATION: Titles, roles, positions, occupations
- NUMBER: Numerically significant values, quantities

Return entities in JSON format with: text, entity_type, start_position, end_position, confidence
"""
```

#### 2. Urdu NER Prompt

```python
URDU_NER_PROMPT = """
You are an expert in Urdu language and literature with deep knowledge of Urdu linguistic rules and cultural context.
Extract named entities from the given Urdu text using Urdu-specific knowledge and rules.

Text: {text}

Entity types to extract:
- PERSON: Names of people, historical figures, characters (حسین، علی، فاطمہ)
- LOCATION: Places, landmarks, geographical features (کربلا، مدینہ، مکہ)
- DATE: Dates, Islamic months, specific days (عاشورا، محرم، 10)
- TIME: Time references and periods (صبح، شام، رات)
- ORGANIZATION: Groups, tribes, armies, institutions (بنی ہاشم، اہل بیت)
- DESIGNATION: Titles, honorifics, roles (امام، خلیفہ، شہید)
- NUMBER: Numerically significant values (72، 40، 1000)

Urdu-specific considerations:
- Handle right-to-left (RTL) text properly
- Consider Urdu honorifics and titles
- Understand Islamic and cultural references
- Recognize Urdu naming conventions
- Handle diacritical marks and variations

Return entities in JSON format with: text, entity_type, start_position, end_position, confidence
"""
```

#### 3. Marsiya NER Prompt

```python
MARSIYA_NER_PROMPT = """
You are an expert in Urdu Marsiya poetry, Islamic history, and the Karbala tradition.
Extract named entities from the given Marsiya text using specialized knowledge of this poetic form and its historical context.

Text: {text}

Entity types to extract:
- PERSON: Names of people, prophets, Imams, historical figures (حسین ابن علی، عباس، زینب)
- LOCATION: Sacred places, battlefields, historical sites (کربلا، مدینہ، مکہ، طف)
- DATE: Islamic dates, historical events, specific days (عاشورا، محرم، 10 محرم)
- TIME: Time references, periods, historical moments (صبح عاشورا، شام، رات)
- ORGANIZATION: Groups, tribes, armies, institutions (بنی ہاشم، اہل بیت، یزیدی لشکر)
- DESIGNATION: Titles, honorifics, roles (امام، خلیفہ، شہید، سردار)
- NUMBER: Numerically significant values (72 شہید، 40 دن، 1000 سپاہی)

Marsiya-specific considerations:
- Focus on Karbala narrative and related events
- Recognize poetic language and metaphors
- Understand Islamic historical context
- Identify battle participants and locations
- Handle Urdu poetic conventions and vocabulary
- Consider religious and cultural significance

Return entities in JSON format with: text, entity_type, start_position, end_position, confidence
"""
```

#### 4. Custom Prompt

```python
CUSTOM_PROMPT_TEMPLATE = """
{user_defined_prompt}

Text: {text}

Entity types to extract:
{user_defined_entity_types}

Additional instructions:
{user_defined_instructions}

Return entities in JSON format with: text, entity_type, start_position, end_position, confidence
"""
```

#### Prompt Selection and Configuration

```python
@dataclass
class PromptConfiguration:
    prompt_type: str = "marsiya_ner"  # Default to Marsiya NER
    custom_prompt: Optional[str] = None
    custom_entity_types: Optional[List[str]] = None
    custom_instructions: Optional[str] = None

    def get_prompt(self, text: str) -> str:
        """Get the appropriate prompt based on configuration."""
        if self.prompt_type == "general_ner":
            return GENERAL_NER_PROMPT.format(text=text)
        elif self.prompt_type == "urdu_ner":
            return URDU_NER_PROMPT.format(text=text)
        elif self.prompt_type == "marsiya_ner":
            return MARSIYA_NER_PROMPT.format(text=text)
        elif self.prompt_type == "custom" and self.custom_prompt:
            return CUSTOM_PROMPT_TEMPLATE.format(
                user_defined_prompt=self.custom_prompt,
                text=text,
                user_defined_entity_types=self._format_entity_types(),
                user_defined_instructions=self.custom_instructions or ""
            )
        else:
            # Fallback to Marsiya NER
            return MARSIYA_NER_PROMPT.format(text=text)

    def _format_entity_types(self) -> str:
        """Format custom entity types for prompt."""
        if not self.custom_entity_types:
            return "- PERSON, LOCATION, DATE, TIME, ORGANIZATION, DESIGNATION, NUMBER"

        formatted_types = []
        for entity_type in self.custom_entity_types:
            formatted_types.append(f"- {entity_type.upper()}")

        return "\n".join(formatted_types)
```

## Async Processing

### Celery Tasks

```python
@celery_app.task(bind=True)
def process_document_ner(self, document_id: int, llm_model_id: int):
    """Process document with NER using Celery."""
    try:
        document = Document.objects.get(id=document_id)
        llm_model = LLMModel.objects.get(id=llm_model_id)

        provider = ProviderFactory.create_provider(llm_model)
        entities = provider.extract_entities(document.content)

        # Store entities
        for entity_data in entities:
            Entity.objects.create(
                document=document,
                **entity_data
            )

        return {"status": "success", "entities_count": len(entities)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Progress Tracking

```python
class ProgressTracker:
    """Track processing progress for real-time updates."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.redis_client = redis.Redis()

    def update_progress(self, progress: int, step: str):
        """Update processing progress."""
        data = {
            "progress": progress,
            "step": step,
            "timestamp": timezone.now().isoformat()
        }
        self.redis_client.publish(f"progress:{self.job_id}", json.dumps(data))
```

## Error Handling

### Retry Mechanisms

```python
class RetryHandler:
    """Handle API failures with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e

                delay = self.base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
```

### Fallback Strategies

```python
class FallbackStrategy:
    """Implement fallback strategies for LLM failures."""

    def __init__(self, providers: List[BaseProvider]):
        self.providers = providers

    async def extract_entities_with_fallback(self, text: str, config: ProcessingConfig):
        """Try multiple providers in sequence."""
        for provider in self.providers:
            try:
                return await provider.extract_entities(text, config)
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed: {e}")
                continue

        raise Exception("All providers failed")
```

## Performance Optimization

### Caching

```python
class EntityCache:
    """Cache extracted entities to avoid reprocessing."""

    def __init__(self):
        self.redis_client = redis.Redis()
        self.ttl = 3600  # 1 hour

    def get_cached_entities(self, text_hash: str) -> Optional[List[Entity]]:
        """Get cached entities for text."""
        cached = self.redis_client.get(f"entities:{text_hash}")
        return json.loads(cached) if cached else None

    def cache_entities(self, text_hash: str, entities: List[Entity]):
        """Cache entities for future use."""
        self.redis_client.setex(
            f"entities:{text_hash}",
            self.ttl,
            json.dumps([e.dict() for e in entities])
        )
```

### Batch Processing

```python
class BatchProcessor:
    """Process multiple text chunks in batches."""

    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size

    async def process_batch(self, chunks: List[str], provider: BaseProvider):
        """Process chunks in parallel batches."""
        results = []

        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            tasks = [provider.extract_entities(chunk) for chunk in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

        return results
```

## Monitoring and Analytics

### Metrics Collection

```python
class MetricsCollector:
    """Collect performance and usage metrics."""

    def __init__(self):
        self.stats = defaultdict(int)

    def record_request(self, provider: str, success: bool, response_time: float):
        """Record API request metrics."""
        self.stats[f"{provider}_requests"] += 1
        if success:
            self.stats[f"{provider}_success"] += 1
        self.stats[f"{provider}_response_time"] += response_time

    def get_stats(self) -> Dict[str, Any]:
        """Get collected statistics."""
        return dict(self.stats)
```

### Cost Tracking

```python
class CostTracker:
    """Track API usage costs."""

    def __init__(self):
        self.costs = defaultdict(float)

    def record_cost(self, provider: str, tokens: int, cost_per_1k: float):
        """Record cost for token usage."""
        cost = (tokens / 1000) * cost_per_1k
        self.costs[provider] += cost

    def get_total_cost(self, provider: str = None) -> float:
        """Get total cost for provider or all providers."""
        if provider:
            return self.costs[provider]
        return sum(self.costs.values())
```

## Security

### API Key Management

```python
class SecureKeyManager:
    """Securely manage API keys."""

    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt API key for storage."""
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use."""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### Rate Limiting

```python
class RateLimiter:
    """Implement rate limiting for API calls."""

    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.redis_client = redis.Redis()

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        current = self.redis_client.get(key)
        if current and int(current) >= self.max_requests:
            return False

        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.time_window)
        pipe.execute()
        return True
```

## Testing

### Mock Provider

```python
class MockProvider(BaseProvider):
    """Mock provider for testing."""

    def __init__(self, responses: List[Entity] = None):
        self.responses = responses or []
        self.request_count = 0

    async def extract_entities(self, text: str, config: ProcessingConfig) -> List[Entity]:
        """Return mock entities."""
        self.request_count += 1
        return self.responses.copy()

    async def test_connection(self) -> bool:
        """Always return True for testing."""
        return True
```

### Integration Tests

```python
class TestLLMIntegration(TestCase):
    """Test LLM integration functionality."""

    def setUp(self):
        self.mock_provider = MockProvider([
            Entity(text="حسین", entity_type="PERSON", start=0, end=5)
        ])

    async def test_entity_extraction(self):
        """Test entity extraction process."""
        entities = await self.mock_provider.extract_entities("حسین ابن علی", {})
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].text, "حسین")
```

This LLM integration system provides a robust, scalable foundation for AI-powered entity recognition in Urdu Marsiya poetry.
