from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from entities.models import EntityType
from projects.models import Project
from llm_integration.models import LLMModel, LLMProcessingConfig

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create default entity types
        self.create_entity_types()
        
        # Create default LLM models
        self.create_llm_models()
        
        # Create default processing configs
        self.create_processing_configs()
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))

    def create_entity_types(self):
        """Create default entity types."""
        entity_types_data = [
            {
                'name': 'PERSON',
                'display_name': 'Person',
                'description': 'Names of people, prophets, Imams, and historical figures',
                'color_code': '#87CEEB',
                'icon': 'person',
                'is_system': True,
                'sort_order': 1,
                'examples': ['حسین', 'علی', 'فاطمہ', 'عباس', 'زینب'],
                'validation_rules': {'min_length': 2, 'max_length': 100}
            },
            {
                'name': 'LOCATION',
                'display_name': 'Location',
                'description': 'Places, landmarks, and geographical features',
                'color_code': '#90EE90',
                'icon': 'location_on',
                'is_system': True,
                'sort_order': 2,
                'examples': ['کربلا', 'مدینہ', 'مکہ', 'طف', 'نجف'],
                'validation_rules': {'min_length': 2, 'max_length': 100}
            },
            {
                'name': 'DATE',
                'display_name': 'Date',
                'description': 'Dates, Islamic months, and specific days',
                'color_code': '#FFFFE0',
                'icon': 'event',
                'is_system': True,
                'sort_order': 3,
                'examples': ['عاشورا', 'محرم', '10', 'رمضان', 'شوال'],
                'validation_rules': {'min_length': 1, 'max_length': 50}
            },
            {
                'name': 'TIME',
                'display_name': 'Time',
                'description': 'Time references and periods',
                'color_code': '#FFC0CB',
                'icon': 'schedule',
                'is_system': True,
                'sort_order': 4,
                'examples': ['صبح', 'شام', 'رات', 'دن', 'رات'],
                'validation_rules': {'min_length': 2, 'max_length': 50}
            },
            {
                'name': 'ORGANIZATION',
                'display_name': 'Organization',
                'description': 'Groups, tribes, armies, and institutions',
                'color_code': '#FFA500',
                'icon': 'business',
                'is_system': True,
                'sort_order': 5,
                'examples': ['بنی ہاشم', 'اہل بیت', 'یزیدی لشکر', 'صحابہ'],
                'validation_rules': {'min_length': 3, 'max_length': 100}
            },
            {
                'name': 'DESIGNATION',
                'display_name': 'Designation',
                'description': 'Titles, honorifics, and roles',
                'color_code': '#D3D3D3',
                'icon': 'badge',
                'is_system': True,
                'sort_order': 6,
                'examples': ['امام', 'خلیفہ', 'شہید', 'سردار', 'قائد'],
                'validation_rules': {'min_length': 2, 'max_length': 50}
            },
            {
                'name': 'NUMBER',
                'display_name': 'Number',
                'description': 'Numerically significant values',
                'color_code': '#E6E6FA',
                'icon': 'looks_one',
                'is_system': True,
                'sort_order': 7,
                'examples': ['72', '40', '1000', '1444', '10'],
                'validation_rules': {'min_length': 1, 'max_length': 20}
            },
        ]
        
        created_count = 0
        for data in entity_types_data:
            entity_type, created = EntityType.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created entity type: {entity_type.name}')
        
        self.stdout.write(f'Created {created_count} entity types')

    def create_llm_models(self):
        """Create default LLM models."""
        llm_models_data = [
            {
                'name': 'OpenAI GPT-4',
                'description': 'OpenAI GPT-4 model for entity recognition',
                'provider': 'openai',
                'model_name': 'gpt-4',
                'api_key': 'your-openai-api-key-here',
                'is_active': True,
                'is_default': True,
                'priority': 1,
                'cost_per_1k_tokens': 0.03,
                'rate_limit_per_hour': 1000,
                'rate_limit_per_minute': 60,
                'settings': {
                    'temperature': 0.1,
                    'max_tokens': 4000,
                    'top_p': 1.0
                }
            },
            {
                'name': 'Anthropic Claude',
                'description': 'Anthropic Claude model for entity recognition',
                'provider': 'anthropic',
                'model_name': 'claude-3-sonnet-20240229',
                'api_key': 'your-anthropic-api-key-here',
                'is_active': True,
                'is_default': False,
                'priority': 2,
                'cost_per_1k_tokens': 0.015,
                'rate_limit_per_hour': 500,
                'rate_limit_per_minute': 30,
                'settings': {
                    'temperature': 0.1,
                    'max_tokens': 4000
                }
            },
        ]
        
        created_count = 0
        for data in llm_models_data:
            llm_model, created = LLMModel.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created LLM model: {llm_model.name}')
        
        self.stdout.write(f'Created {created_count} LLM models')

    def create_processing_configs(self):
        """Create default processing configurations."""
        configs_data = [
            {
                'name': 'Default Marsiya NER',
                'description': 'Default configuration for Marsiya NER processing',
                'llm_model': LLMModel.objects.filter(is_default=True).first(),
                'chunk_size': 1000,
                'overlap_size': 100,
                'max_tokens': 4000,
                'confidence_threshold': 0.7,
                'entity_types': ['PERSON', 'LOCATION', 'DATE', 'TIME', 'ORGANIZATION', 'DESIGNATION', 'NUMBER'],
                'prompt_type': 'marsiya_ner',
                'enable_post_processing': True,
                'enable_entity_validation': True,
                'enable_confidence_scoring': True,
                'is_active': True
            },
            {
                'name': 'General NER',
                'description': 'Configuration for general NER processing',
                'llm_model': LLMModel.objects.filter(is_default=True).first(),
                'chunk_size': 800,
                'overlap_size': 50,
                'max_tokens': 4000,
                'confidence_threshold': 0.8,
                'entity_types': ['PERSON', 'LOCATION', 'DATE', 'TIME', 'ORGANIZATION', 'DESIGNATION', 'NUMBER'],
                'prompt_type': 'general_ner',
                'enable_post_processing': True,
                'enable_entity_validation': True,
                'enable_confidence_scoring': True,
                'is_active': True
            },
        ]
        
        created_count = 0
        for data in configs_data:
            if data['llm_model']:
                config, created = LLMProcessingConfig.objects.get_or_create(
                    name=data['name'],
                    defaults=data
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created processing config: {config.name}')
        
        self.stdout.write(f'Created {created_count} processing configurations')
