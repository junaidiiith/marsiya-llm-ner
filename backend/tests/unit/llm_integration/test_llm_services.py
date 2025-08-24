"""
Unit tests for LLM integration services.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock, Mock
from llm_integration.services import LLMService, PromptConfiguration
from llm_integration.models import LLMModel, LLMProcessingConfig
from entities.models import EntityType

User = get_user_model()


class TestPromptConfiguration(TestCase):
    """Test PromptConfiguration class."""
    
    def test_get_prompt_templates(self):
        """Test getting all prompt templates."""
        templates = PromptConfiguration.get_prompt_templates()
        
        # Check that all expected templates exist
        expected_templates = ['general', 'urdu', 'marsiya', 'custom']
        for template_name in expected_templates:
            self.assertIn(template_name, templates)
            self.assertIsInstance(templates[template_name], str)
            self.assertGreater(len(templates[template_name]), 0)
    
    def test_general_ner_prompt(self):
        """Test general NER prompt template."""
        templates = PromptConfiguration.get_prompt_templates()
        general_prompt = templates['general']
        
        # Check that it contains expected content
        self.assertIn('Named Entity Recognition', general_prompt)
        self.assertIn('PERSON', general_prompt)
        self.assertIn('LOCATION', general_prompt)
        self.assertIn('DATE', general_prompt)
        self.assertIn('TIME', general_prompt)
        self.assertIn('ORGANIZATION', general_prompt)
        self.assertIn('DESIGNATION', general_prompt)
        self.assertIn('NUMBER', general_prompt)
        self.assertIn('{text}', general_prompt)
    
    def test_urdu_ner_prompt(self):
        """Test Urdu NER prompt template."""
        templates = PromptConfiguration.get_prompt_templates()
        urdu_prompt = templates['urdu']
        
        # Check that it contains expected content
        self.assertIn('Urdu language', urdu_prompt)
        self.assertIn('linguistic patterns', urdu_prompt)
        self.assertIn('cultural context', urdu_prompt)
        self.assertIn('honorifics', urdu_prompt)
        self.assertIn('Hazrat', urdu_prompt)
        self.assertIn('Maulana', urdu_prompt)
        self.assertIn('Syed', urdu_prompt)
        self.assertIn('Islamic calendar', urdu_prompt)
        self.assertIn('{text}', urdu_prompt)
    
    def test_marsiya_ner_prompt(self):
        """Test Marsiya NER prompt template."""
        templates = PromptConfiguration.get_prompt_templates()
        marsiya_prompt = templates['marsiya']
        
        # Check that it contains expected content
        self.assertIn('Urdu Marsiya poetry', marsiya_prompt)
        self.assertIn('Karbala', marsiya_prompt)
        self.assertIn('Islamic history', marsiya_prompt)
        self.assertIn('Marsiya poetry traditions', marsiya_prompt)
        self.assertIn('Prophets', marsiya_prompt)
        self.assertIn('Imams', marsiya_prompt)
        self.assertIn('historical figures', marsiya_prompt)
        self.assertIn('Battle of Karbala', marsiya_prompt)
        self.assertIn('{text}', marsiya_prompt)
    
    def test_custom_prompt_template(self):
        """Test custom prompt template."""
        templates = PromptConfiguration.get_prompt_templates()
        custom_prompt = templates['custom']
        
        # Custom prompt should just contain the text placeholder
        self.assertEqual(custom_prompt, '{text}')
    
    def test_validate_prompt_template_valid(self):
        """Test validation of valid prompt templates."""
        valid_templates = [
            'This is a valid template with {text} placeholder that is long enough',
            'Another valid template with {text} and more content to meet length requirement',
            'Template with {text} and special characters: !@#$%^&*()',
            'Template with {text} and numbers: 12345 and more text to reach minimum length'
        ]
        
        for template in valid_templates:
            self.assertTrue(PromptConfiguration.validate_prompt_template(template))
    
    def test_validate_prompt_template_invalid(self):
        """Test validation of invalid prompt templates."""
        invalid_templates = [
            '',  # Empty string
            '   ',  # Only whitespace
            'Too short',  # Too short
            'No placeholder',  # No text placeholder
            'With {other} placeholder',  # Wrong placeholder
            'With {text} but short',  # Too short even with placeholder
        ]
        
        for template in invalid_templates:
            self.assertFalse(PromptConfiguration.validate_prompt_template(template))
    
    def test_validate_prompt_template_edge_cases(self):
        """Test validation edge cases."""
        # Exactly 50 characters with placeholder
        edge_case_valid = 'A' * 49 + '{text}'
        self.assertTrue(PromptConfiguration.validate_prompt_template(edge_case_valid))
        
        # 49 characters with placeholder
        edge_case_invalid = 'A' * 48 + '{text}'
        self.assertFalse(PromptConfiguration.validate_prompt_template(edge_case_invalid))
        
        # Multiple text placeholders
        multiple_placeholders = 'Template with {text} and another {text} placeholder'
        self.assertTrue(PromptConfiguration.validate_prompt_template(multiple_placeholders))


class TestLLMService(TestCase):
    """Test LLMService class."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create entity types
        self.person_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            color_code='#FF0000',
            is_active=True
        )
        
        self.location_type = EntityType.objects.create(
            name='LOCATION',
            description='Places and locations',
            color_code='#00FF00',
            is_active=True
        )
        
        # Create LLM model
        self.llm_model = LLMModel.objects.create(
            name='Test GPT Model',
            description='A test model for development',
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key-123',
            is_active=True,
            cost_per_1k_tokens=0.002
        )
        
        # Create LLM processing config
        self.llm_config = LLMProcessingConfig.objects.create(
            name='Test Marsiya Config',
            llm_model=self.llm_model,
            prompt_type='marsiya_ner',
            max_tokens=2000,
            chunk_size=1000,
            overlap_size=100,
            confidence_threshold=0.7,
            is_active=True
        )
    
    def test_llm_service_initialization(self):
        """Test LLM service initialization."""
        service = LLMService()
        
        self.assertEqual(service.llm_model, self.llm_model)
        self.assertEqual(service.config, self.llm_config)
    
    def test_llm_service_initialization_with_model(self):
        """Test LLM service initialization with specific model."""
        service = LLMService(self.llm_model)
        
        self.assertEqual(service.llm_model, self.llm_model)
        self.assertEqual(service.config, self.llm_config)
    
    def test_llm_service_initialization_no_active_model(self):
        """Test LLM service initialization when no active model exists."""
        # Deactivate the model
        self.llm_model.is_active = False
        self.llm_model.save()
        
        with self.assertRaises(ValueError):
            LLMService()
    
    def test_llm_service_initialization_no_active_config(self):
        """Test LLM service initialization when no active config exists."""
        # Deactivate the config
        self.llm_config.is_active = False
        self.llm_config.save()
        
        with self.assertRaises(ValueError):
            LLMService()
    
    def test_get_prompt_template(self):
        """Test getting prompt templates."""
        service = LLMService()
        
        # Test general prompt
        general_prompt = service._get_prompt_template('general')
        self.assertIn('Named Entity Recognition', general_prompt)
        self.assertIn('{text}', general_prompt)
        
        # Test Urdu prompt
        urdu_prompt = service._get_prompt_template('urdu')
        self.assertIn('Urdu language', urdu_prompt)
        self.assertIn('{text}', urdu_prompt)
        
        # Test Marsiya prompt
        marsiya_prompt = service._get_prompt_template('marsiya')
        self.assertIn('Urdu Marsiya poetry', marsiya_prompt)
        self.assertIn('{text}', marsiya_prompt)
        
        # Test custom prompt
        custom_prompt = service._get_prompt_template('custom')
        self.assertEqual(custom_prompt, '{text}')
        
        # Test default prompt (should be Marsiya)
        default_prompt = service._get_prompt_template('invalid_type')
        self.assertIn('Urdu Marsiya poetry', default_prompt)
    
    def test_format_prompt(self):
        """Test prompt formatting."""
        service = LLMService()
        test_text = "This is a test text for prompt formatting."
        
        formatted_prompt = service._format_prompt(test_text, 'general')
        
        self.assertIn(test_text, formatted_prompt)
        self.assertIn('Named Entity Recognition', formatted_prompt)
    
    def test_parse_llm_response_json(self):
        """Test parsing LLM response in JSON format."""
        service = LLMService()
        
        # Test JSON response with entities array
        json_response = '''
        {
            "entities": [
                {
                    "text": "Hazrat Ali",
                    "entity_type": "PERSON",
                    "start": 0,
                    "end": 10,
                    "confidence": 0.95
                },
                {
                    "text": "Karbala",
                    "entity_type": "LOCATION",
                    "start": 15,
                    "end": 22,
                    "confidence": 0.98
                }
            ]
        }
        '''
        
        entities = service._parse_llm_response(json_response)
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0]['text'], 'Hazrat Ali')
        self.assertEqual(entities[0]['entity_type'], 'PERSON')
        self.assertEqual(entities[1]['text'], 'Karbala')
        self.assertEqual(entities[1]['entity_type'], 'LOCATION')
    
    def test_parse_llm_response_json_list(self):
        """Test parsing LLM response in JSON list format."""
        service = LLMService()
        
        # Test JSON response as direct list
        json_response = '''
        [
            {
                "text": "Hazrat Ali",
                "entity_type": "PERSON",
                "start": 0,
                "end": 10,
                "confidence": 0.95
            },
            {
                "text": "Karbala",
                "entity_type": "LOCATION",
                "start": 15,
                "end": 22,
                "confidence": 0.98
            }
        ]
        '''
        
        entities = service._parse_llm_response(json_response)
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0]['text'], 'Hazrat Ali')
        self.assertEqual(entities[1]['text'], 'Karbala')
    
    def test_parse_llm_response_text_fallback(self):
        """Test parsing LLM response using text fallback."""
        service = LLMService()
        
        # Test text response
        text_response = '''
        Hazrat Ali:PERSON:0:10
        Karbala:LOCATION:15:22
        # This is a comment
        '''
        
        entities = service._parse_llm_response(text_response)
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0]['text'], 'Hazrat Ali')
        self.assertEqual(entities[0]['entity_type'], 'PERSON')
        self.assertEqual(entities[1]['text'], 'Karbala')
        self.assertEqual(entities[1]['entity_type'], 'LOCATION')
    
    def test_parse_llm_response_invalid(self):
        """Test parsing invalid LLM response."""
        service = LLMService()
        
        # Test invalid JSON
        invalid_json = 'This is not valid JSON'
        entities = service._parse_llm_response(invalid_json)
        
        self.assertEqual(len(entities), 0)
    
    def test_find_entity_positions(self):
        """Test finding entity positions in text."""
        service = LLMService()
        
        text = "Hazrat Ali went to Karbala. Hazrat Ali was brave."
        entities_data = [
            {'text': 'Hazrat Ali', 'entity_type': 'PERSON'},
            {'text': 'Karbala', 'entity_type': 'LOCATION'}
        ]
        
        positioned_entities = service._find_entity_positions(text, entities_data)
        
        # Should find 3 entities (2 Hazrat Ali, 1 Karbala)
        self.assertEqual(len(positioned_entities), 3)
        
        # Check first Hazrat Ali
        self.assertEqual(positioned_entities[0]['text'], 'Hazrat Ali')
        self.assertEqual(positioned_entities[0]['start'], 0)
        self.assertEqual(positioned_entities[0]['end'], 10)
        self.assertEqual(positioned_entities[0]['entity_type'], 'PERSON')
        
        # Check Karbala
        self.assertEqual(positioned_entities[1]['text'], 'Karbala')
        self.assertEqual(positioned_entities[1]['start'], 20)
        self.assertEqual(positioned_entities[1]['end'], 27)
        self.assertEqual(positioned_entities[1]['entity_type'], 'LOCATION')
        
        # Check second Hazrat Ali
        self.assertEqual(positioned_entities[2]['text'], 'Hazrat Ali')
        self.assertEqual(positioned_entities[2]['start'], 33)
        self.assertEqual(positioned_entities[2]['end'], 43)
        self.assertEqual(positioned_entities[2]['entity_type'], 'PERSON')
    
    def test_find_entity_positions_no_matches(self):
        """Test finding entity positions when no matches exist."""
        service = LLMService()
        
        text = "This text has no entities."
        entities_data = [
            {'text': 'Hazrat Ali', 'entity_type': 'PERSON'},
            {'text': 'Karbala', 'entity_type': 'LOCATION'}
        ]
        
        positioned_entities = service._find_entity_positions(text, entities_data)
        
        self.assertEqual(len(positioned_entities), 0)
    
    @patch('llm_integration.services.openai.OpenAI')
    def test_extract_entities_openai(self, mock_openai):
        """Test entity extraction with OpenAI."""
        service = LLMService()
        
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "entities": [
                {
                    "text": "Hazrat Ali",
                    "entity_type": "PERSON",
                    "start": 0,
                    "end": 10,
                    "confidence": 0.95
                }
            ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        text = "Hazrat Ali went to Karbala."
        entities = service.extract_entities(text, 'marsiya')
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['text'], 'Hazrat Ali')
        self.assertEqual(entities[0]['entity_type'], 'PERSON')
        self.assertIn('processing_time', entities[0])
        self.assertIn('llm_model', entities[0])
        self.assertIn('prompt_type', entities[0])
    
    @patch('llm_integration.services.anthropic.Anthropic')
    def test_extract_entities_anthropic(self, mock_anthropic):
        """Test entity extraction with Anthropic."""
        service = LLMService()
        
        # Change model to Anthropic
        service.llm_model.provider = 'anthropic'
        service.llm_model.model_name = 'claude-3-sonnet-20240229'
        
        # Mock Anthropic response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "entities": [
                {
                    "text": "Karbala",
                    "entity_type": "LOCATION",
                    "start": 15,
                    "end": 22,
                    "confidence": 0.98
                }
            ]
        }
        '''
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        text = "Hazrat Ali went to Karbala."
        entities = service.extract_entities(text, 'urdu')
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['text'], 'Karbala')
        self.assertEqual(entities[0]['entity_type'], 'LOCATION')
    
    def test_extract_entities_unsupported_provider(self):
        """Test entity extraction with unsupported provider."""
        service = LLMService()
        service.llm_model.provider = 'unsupported'
        
        text = "Test text"
        
        with self.assertRaises(ValueError):
            service.extract_entities(text, 'general')
    
    @patch('llm_integration.services.cache.get')
    @patch('llm_integration.services.cache.set')
    def test_extract_entities_cache(self, mock_cache_set, mock_cache_get):
        """Test entity extraction caching."""
        service = LLMService()
        
        # Mock cache hit
        cached_entities = [
            {
                'text': 'Hazrat Ali',
                'entity_type': 'PERSON',
                'start': 0,
                'end': 10,
                'confidence': 0.95,
                'processing_time': 0.5,
                'llm_model': 'gpt-3.5-turbo',
                'prompt_type': 'marsiya'
            }
        ]
        mock_cache_get.return_value = cached_entities
        
        text = "Hazrat Ali went to Karbala."
        entities = service.extract_entities(text, 'marsiya')
        
        # Should return cached result
        self.assertEqual(entities, cached_entities)
        
        # Cache should not be set again
        mock_cache_set.assert_not_called()
    
    def test_update_usage_stats(self):
        """Test updating usage statistics."""
        service = LLMService()
        
        initial_requests = service.llm_model.total_requests
        initial_time = service.llm_model.total_processing_time
        initial_entities = service.llm_model.total_entities_extracted
        
        processing_time = 1.5
        entity_count = 3
        
        service._update_usage_stats(processing_time, entity_count)
        
        # Refresh from database
        service.llm_model.refresh_from_db()
        
        self.assertEqual(service.llm_model.total_requests, initial_requests + 1)
        self.assertEqual(service.llm_model.total_processing_time, initial_time + processing_time)
        self.assertEqual(service.llm_model.total_entities_extracted, initial_entities + entity_count)
    
    def test_get_available_models_openai(self):
        """Test getting available models from OpenAI."""
        service = LLMService()
        
        with patch('llm_integration.services.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_model1 = Mock()
            mock_model1.id = 'gpt-4'
            mock_model2 = Mock()
            mock_model2.id = 'gpt-3.5-turbo'
            
            mock_response = Mock()
            mock_response.data = [mock_model1, mock_model2]
            mock_client.models.list.return_value = mock_response
            mock_openai.return_value = mock_client
            
            models = service.get_available_models()
            
            self.assertEqual(len(models), 2)
            self.assertEqual(models[0]['id'], 'gpt-4')
            self.assertEqual(models[0]['provider'], 'openai')
            self.assertEqual(models[1]['id'], 'gpt-3.5-turbo')
            self.assertEqual(models[1]['provider'], 'openai')
    
    def test_get_available_models_anthropic(self):
        """Test getting available models from Anthropic."""
        service = LLMService()
        service.llm_model.provider = 'anthropic'
        
        models = service.get_available_models()
        
        expected_models = ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
        
        self.assertEqual(len(models), 3)
        for i, model in enumerate(models):
            self.assertEqual(model['id'], expected_models[i])
            self.assertEqual(model['provider'], 'anthropic')
            self.assertTrue(model['available'])
    
    def test_get_available_models_unsupported_provider(self):
        """Test getting available models from unsupported provider."""
        service = LLMService()
        service.llm_model.provider = 'unsupported'
        
        models = service.get_available_models()
        
        self.assertEqual(len(models), 0)


class TestLLMServiceIntegration(TestCase):
    """Integration tests for LLMService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create entity types
        self.person_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            color_code='#FF0000',
            is_active=True
        )
        
        # Create LLM model
        self.llm_model = LLMModel.objects.create(
            name='Test GPT Model',
            description='A test model for development',
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key-123',
            is_active=True,
            cost_per_1k_tokens=0.002
        )
        
        # Create LLM processing config
        self.llm_config = LLMProcessingConfig.objects.create(
            name='Test Marsiya Config',
            llm_model=self.llm_model,
            prompt_type='marsiya_ner',
            max_tokens=2000,
            chunk_size=1000,
            overlap_size=100,
            confidence_threshold=0.7,
            is_active=True
        )
    
    def test_complete_entity_extraction_workflow(self):
        """Test complete entity extraction workflow."""
        service = LLMService()
        
        # Test text
        text = "Hazrat Ali went to Karbala with his companions."
        
        # Test different prompt types
        prompt_types = ['general', 'urdu', 'marsiya']
        
        for prompt_type in prompt_types:
            # Get prompt template
            template = service._get_prompt_template(prompt_type)
            self.assertIn('{text}', template)
            
            # Format prompt
            formatted_prompt = service._format_prompt(text, prompt_type)
            self.assertIn(text, formatted_prompt)
            
            # Test prompt validation
            self.assertTrue(PromptConfiguration.validate_prompt_template(template))
    
    def test_service_with_different_configurations(self):
        """Test service with different configurations."""
        # Create another config
        config2 = LLMProcessingConfig.objects.create(
            name='Test General Config',
            llm_model=self.llm_model,
            prompt_type='general_ner',
            max_tokens=1000,
            chunk_size=500,
            overlap_size=50,
            confidence_threshold=0.8,
            is_active=True
        )
        
        # Test service with first config
        service1 = LLMService()
        self.assertEqual(service1.config, self.llm_config)
        
        # Deactivate first config
        self.llm_config.is_active = False
        self.llm_config.save()
        
        # Service should now use second config
        service2 = LLMService()
        self.assertEqual(service2.config, config2)
    
    def test_error_handling(self):
        """Test error handling in service."""
        service = LLMService()
        
        # Test with invalid prompt type
        invalid_prompt = service._get_prompt_template('invalid')
        self.assertIn('Urdu Marsiya poetry', invalid_prompt)  # Should fall back to default
        
        # Test with empty text
        empty_text = ""
        formatted_prompt = service._format_prompt(empty_text, 'general')
        self.assertEqual(formatted_prompt, PromptConfiguration.get_prompt_templates()['general'].format(text=empty_text))
