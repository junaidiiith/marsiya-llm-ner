from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import UserStampedModel, SoftDeleteModel


class LLMModel(UserStampedModel, SoftDeleteModel):
    """Configuration for different LLM providers and models."""
    
    # Basic Information
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    
    # Provider Information
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('local', 'Local Model'),
        ('custom', 'Custom API'),
    ]
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # Model Configuration
    model_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=500)
    api_base_url = models.URLField(blank=True)
    
    # Provider-specific Settings
    settings = models.JSONField(default=dict)
    
    # Status and Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0)
    
    # Performance Metrics
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(null=True, blank=True)
    
    # Rate Limiting
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    
    # Cost Tracking
    cost_per_1k_tokens = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0.00
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Metadata
    tags = models.JSONField(default=list)
    
    class Meta:
        db_table = 'llm_integration_llm_model'
        verbose_name = 'LLM Model'
        verbose_name_plural = 'LLM Models'
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.provider})"
    
    def clean(self):
        """Validate model configuration."""
        if self.rate_limit_per_hour < self.rate_limit_per_minute:
            raise ValidationError("Hourly rate limit must be greater than or equal to minute rate limit")
        
        if self.cost_per_1k_tokens < 0:
            raise ValidationError("Cost per 1K tokens cannot be negative")
        
        if self.total_cost < 0:
            raise ValidationError("Total cost cannot be negative")
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one default model per provider."""
        if self.is_default:
            # Set other models of same provider as non-default
            LLMModel.objects.filter(
                provider=self.provider,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def test_connection(self):
        """Test connection to the LLM provider."""
        try:
            # This would be implemented in the provider class
            from .providers import ProviderFactory
            provider = ProviderFactory.create_provider(self)
            return provider.test_connection()
        except Exception as e:
            return False
    
    def record_request(self, success: bool, response_time: float = None, tokens_used: int = 0):
        """Record API request metrics."""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if response_time:
            if self.average_response_time:
                # Calculate running average
                self.average_response_time = (
                    (self.average_response_time * (self.total_requests - 1) + response_time) 
                    / self.total_requests
                )
            else:
                self.average_response_time = response_time
        
        # Calculate cost
        if tokens_used > 0:
            cost = (tokens_used / 1000) * float(self.cost_per_1k_tokens)
            self.total_cost += cost
        
        self.save(update_fields=[
            'total_requests', 'successful_requests', 'failed_requests',
            'average_response_time', 'total_cost'
        ])
    
    def get_success_rate(self):
        """Get success rate percentage."""
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_failure_rate(self):
        """Get failure rate percentage."""
        if self.total_requests == 0:
            return 0
        return (self.failed_requests / self.total_requests) * 100
    
    def get_setting(self, key, default=None):
        """Get provider-specific setting."""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set provider-specific setting."""
        self.settings[key] = value
        self.save(update_fields=['settings'])
    
    def add_tag(self, tag):
        """Add tag to model."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remove tag from model."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])


class LLMProcessingConfig(models.Model):
    """Configuration for LLM text processing."""
    
    llm_model = models.ForeignKey(
        LLMModel,
        on_delete=models.CASCADE,
        related_name='processing_configs'
    )
    
    # Text Processing Settings
    chunk_size = models.PositiveIntegerField(default=1000)
    overlap_size = models.PositiveIntegerField(default=100)
    max_tokens = models.PositiveIntegerField(default=4000)
    
    # Entity Extraction Settings
    confidence_threshold = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.7
    )
    entity_types = models.JSONField(default=list)
    
    # Prompt Configuration
    prompt_type = models.CharField(
        max_length=20,
        choices=[
            ('general_ner', 'General NER'),
            ('urdu_ner', 'Urdu NER'),
            ('marsiya_ner', 'Marsiya NER'),
            ('custom', 'Custom'),
        ],
        default='marsiya_ner'
    )
    custom_prompt = models.TextField(blank=True)
    custom_entity_types = models.JSONField(default=list)
    custom_instructions = models.TextField(blank=True)
    
    # Processing Options
    enable_post_processing = models.BooleanField(default=True)
    enable_entity_validation = models.BooleanField(default=True)
    enable_confidence_scoring = models.BooleanField(default=True)
    
    # Metadata
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'llm_integration_llm_processing_config'
        verbose_name = 'LLM Processing Config'
        verbose_name_plural = 'LLM Processing Configs'
        ordering = ['name']
        indexes = [
            models.Index(fields=['llm_model']),
            models.Index(fields=['prompt_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.llm_model.name})"
    
    def clean(self):
        """Validate configuration."""
        if self.chunk_size <= 0:
            raise ValidationError("Chunk size must be positive")
        
        if self.overlap_size >= self.chunk_size:
            raise ValidationError("Overlap size must be less than chunk size")
        
        if self.max_tokens <= 0:
            raise ValidationError("Max tokens must be positive")
        
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            raise ValidationError("Confidence threshold must be between 0 and 1")
    
    def get_prompt_config(self):
        """Get prompt configuration."""
        return {
            'prompt_type': self.prompt_type,
            'custom_prompt': self.custom_prompt,
            'custom_entity_types': self.custom_entity_types,
            'custom_instructions': self.custom_instructions,
        }
    
    def get_processing_settings(self):
        """Get processing settings."""
        return {
            'chunk_size': self.chunk_size,
            'overlap_size': self.overlap_size,
            'max_tokens': self.max_tokens,
            'confidence_threshold': self.confidence_threshold,
            'entity_types': self.entity_types,
            'enable_post_processing': self.enable_post_processing,
            'enable_entity_validation': self.enable_entity_validation,
            'enable_confidence_scoring': self.enable_confidence_scoring,
        }
    
    def is_custom_prompt(self):
        """Check if this is a custom prompt configuration."""
        return self.prompt_type == 'custom' and bool(self.custom_prompt)
    
    def get_entity_types_display(self):
        """Get formatted entity types."""
        if self.entity_types:
            return ', '.join(self.entity_types)
        return 'All available types'
    
    def get_chunk_info(self):
        """Get chunk processing information."""
        return {
            'chunk_size': self.chunk_size,
            'overlap_size': self.overlap_size,
            'effective_chunk_size': self.chunk_size - self.overlap_size
        }
