import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import LLMModel, LLMProcessingConfig
from entities.models import EntityType
from documents.models import Document
from entities.models import Entity
import openai
import anthropic
import requests

logger = logging.getLogger(__name__)


class LLMService:
    """Service class for handling LLM operations and entity extraction."""

    def __init__(self, llm_model: Optional[LLMModel] = None):
        self.llm_model = llm_model or LLMModel.objects.filter(is_active=True).first()
        self.config = LLMProcessingConfig.objects.filter(is_active=True).first()

        if not self.llm_model:
            raise ValueError("No active LLM model found")

        if not self.config:
            raise ValueError("No active LLM processing configuration found")

    def _get_client(self):
        """Get the appropriate LLM client based on the provider."""
        if self.llm_model.provider == "openai":
            return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.llm_model.provider == "anthropic":
            return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_model.provider}")

    def _get_prompt_template(self, prompt_type: str = "marsiya") -> str:
        """Get the appropriate prompt template based on type."""
        # Get the appropriate prompt template from the configuration
        if prompt_type == "general":
            return PromptConfiguration.get_prompt_templates()["general"]
        elif prompt_type == "urdu":
            return PromptConfiguration.get_prompt_templates()["urdu"]
        elif prompt_type == "marsiya":
            return PromptConfiguration.get_prompt_templates()["marsiya"]
        elif prompt_type == "custom":
            # Use custom prompt if available, otherwise fall back to default
            if self.config.custom_prompt:
                return self.config.custom_prompt
            else:
                return PromptConfiguration.get_prompt_templates()["marsiya"]
        else:
            return PromptConfiguration.get_prompt_templates()["marsiya"]  # default

    def _format_prompt(self, text: str, prompt_type: str = "marsiya") -> str:
        """Format the prompt with the input text."""
        template = self._get_prompt_template(prompt_type)
        return template.format(text=text)

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract entities."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith("{"):
                data = json.loads(response)
                if isinstance(data, dict) and "entities" in data:
                    return data["entities"]
                elif isinstance(data, list):
                    return data

            # Fallback: try to extract entities from text
            entities = []
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Try to parse entity format: "text:entity_type:start:end"
                parts = line.split(":")
                if len(parts) >= 2:
                    entity_text = parts[0].strip()
                    entity_type = parts[1].strip()

                    # Validate entity type
                    if EntityType.objects.filter(name__iexact=entity_type).exists():
                        entity = {
                            "text": entity_text,
                            "entity_type": entity_type,
                            "start": 0,  # Will be calculated later
                            "end": len(entity_text),
                        }
                        entities.append(entity)

            return entities

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.error(f"Response: {response}")
            return []

    def _find_entity_positions(
        self, text: str, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find the actual positions of entities in the text."""
        positioned_entities = []

        for entity in entities:
            entity_text = entity["text"]
            entity_type = entity["entity_type"]

            # Find all occurrences of the entity text
            start = 0
            while True:
                pos = text.find(entity_text, start)
                if pos == -1:
                    break

                positioned_entity = {
                    "text": entity_text,
                    "entity_type": entity_type,
                    "start": pos,
                    "end": pos + len(entity_text),
                    "confidence": entity.get("confidence", 0.8),
                }
                positioned_entities.append(positioned_entity)
                start = pos + 1

        return positioned_entities

    def extract_entities(
        self, text: str, prompt_type: str = "marsiya"
    ) -> List[Dict[str, Any]]:
        """Extract entities from text using the configured LLM."""
        try:
            # Check cache first
            cache_key = f"llm_entities:{hash(text)}:{prompt_type}:{self.llm_model.id}"
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("Returning cached entity extraction result")
                return cached_result

            # Format prompt
            prompt = self._format_prompt(text, prompt_type)

            # Get LLM client
            client = self._get_client()

            # Make API call
            start_time = time.time()

            if self.llm_model.provider == "openai":
                response = client.chat.completions.create(
                    model=self.llm_model.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in Named Entity Recognition (NER). Extract entities from the given text and return them in JSON format with the following structure: [{'text': 'entity_text', 'entity_type': 'PERSON', 'start': 0, 'end': 10, 'confidence': 0.9}]",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    response_format={"type": "json_object"},
                )
                llm_response = response.choices[0].message.content

            elif self.llm_model.provider == "anthropic":
                response = client.messages.create(
                    model=self.llm_model.model_name,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system="You are an expert in Named Entity Recognition (NER). Extract entities from the given text and return them in JSON format with the following structure: [{'text': 'entity_text', 'entity_type': 'PERSON', 'start': 0, 'end': 10, 'confidence': 0.9}]",
                    messages=[{"role": "user", "content": prompt}],
                )
                llm_response = response.content[0].text
            else:
                raise ValueError(f"Unsupported provider: {self.llm_model.provider}")

            processing_time = time.time() - start_time

            # Parse response
            entities = self._parse_llm_response(llm_response)

            # Find positions
            positioned_entities = self._find_entity_positions(text, entities)

            # Add metadata
            for entity in positioned_entities:
                entity["processing_time"] = processing_time
                entity["llm_model"] = self.llm_model.model_name
                entity["prompt_type"] = prompt_type

            # Cache result
            cache.set(cache_key, positioned_entities, timeout=3600)  # 1 hour

            # Update usage statistics
            self._update_usage_stats(processing_time, len(positioned_entities))

            logger.info(
                f"Successfully extracted {len(positioned_entities)} entities in {processing_time:.2f}s"
            )
            return positioned_entities

        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            raise

    def _update_usage_stats(self, processing_time: float, entity_count: int):
        """Update usage statistics for the LLM model."""
        try:
            self.llm_model.total_requests += 1
            self.llm_model.total_processing_time += processing_time
            self.llm_model.total_entities_extracted += entity_count
            self.llm_model.last_used = timezone.now()
            self.llm_model.save(
                update_fields=[
                    "total_requests",
                    "total_processing_time",
                    "total_entities_extracted",
                    "last_used",
                ]
            )
        except Exception as e:
            logger.error(f"Error updating usage stats: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the LLM provider."""
        try:
            client = self._get_client()

            # Simple test prompt
            test_text = "Test text for connection verification."
            prompt = self._format_prompt(test_text, "general")

            start_time = time.time()

            if self.llm_model.provider == "openai":
                response = client.chat.completions.create(
                    model=self.llm_model.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Respond with 'OK' if you receive this message.",
                        },
                        {"role": "user", "content": "Test message"},
                    ],
                    max_tokens=10,
                    temperature=0,
                )
                response_text = response.choices[0].message.content

            elif self.llm_model.provider == "anthropic":
                response = client.messages.create(
                    model=self.llm_model.model_name,
                    max_tokens=10,
                    temperature=0,
                    system="You are a helpful assistant. Respond with 'OK' if you receive this message.",
                    messages=[{"role": "user", "content": "Test message"}],
                )
                response_text = response.content[0].text
            else:
                raise ValueError(f"Unsupported provider: {self.llm_model.provider}")

            processing_time = time.time() - start_time

            return {
                "success": True,
                "response_time": processing_time,
                "response": response_text,
                "provider": self.llm_model.provider,
                "model": self.llm_model.model_name,
            }

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.llm_model.provider,
                "model": self.llm_model.model_name,
            }

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from the provider."""
        try:
            if self.llm_model.provider == "openai":
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                models = client.models.list()
                return [
                    {
                        "id": model.id,
                        "name": model.id,
                        "provider": "openai",
                        "available": True,
                    }
                    for model in models.data
                ]
            elif self.llm_model.provider == "anthropic":
                # Anthropic has a limited set of models
                return [
                    {
                        "id": "claude-3-opus-20240229",
                        "name": "Claude 3 Opus",
                        "provider": "anthropic",
                        "available": True,
                    },
                    {
                        "id": "claude-3-sonnet-20240229",
                        "name": "Claude 3 Sonnet",
                        "provider": "anthropic",
                        "available": True,
                    },
                    {
                        "id": "claude-3-haiku-20240307",
                        "name": "Claude 3 Haiku",
                        "provider": "anthropic",
                        "available": True,
                    },
                ]
            else:
                return []

        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []


class PromptConfiguration:
    """Configuration class for managing different prompt types."""

    @staticmethod
    def get_prompt_templates() -> Dict[str, str]:
        """Get all available prompt templates."""
        return {
            "general": """You are an expert in Named Entity Recognition (NER). 
Analyze the following text and identify all named entities. 
Return the results in JSON format with the following structure:
[{{"text": "entity_text", "entity_type": "ENTITY_TYPE", "start": 0, "end": 10, "confidence": 0.9}}]

Text to analyze:
{text}

Entity types to identify: PERSON, LOCATION, DATE, TIME, ORGANIZATION, DESIGNATION, NUMBER""",
            "urdu": """You are an expert in Urdu language and Named Entity Recognition (NER). 
Analyze the following Urdu text and identify all named entities, considering Urdu linguistic patterns and cultural context.
Return the results in JSON format with the following structure:
[{{"text": "entity_text", "entity_type": "ENTITY_TYPE", "start": 0, "end": 10, "confidence": 0.9}}]

Text to analyze:
{text}

Entity types to identify: PERSON, LOCATION, DATE, TIME, ORGANIZATION, DESIGNATION, NUMBER

Urdu-specific considerations:
- Names may have honorifics (e.g., Hazrat, Maulana, Syed)
- Locations may include historical and religious sites
- Dates may include Islamic calendar references
- Organizations may include religious institutions and historical groups""",
            "marsiya": """You are an expert in Urdu Marsiya poetry and Named Entity Recognition (NER). 
Analyze the following Marsiya text and identify all named entities, considering the specific context of Karbala, Islamic history, and Marsiya poetry traditions.
Return the results in JSON format with the following structure:
[{{"text": "entity_text", "entity_type": "ENTITY_TYPE", "start": 0, "end": 10, "confidence": 0.9}}]

Text to analyze:
{text}

Entity types to identify: PERSON, LOCATION, DATE, TIME, ORGANIZATION, DESIGNATION, NUMBER

Marsiya-specific considerations:
- PERSON: Prophets, Imams, historical figures, family members, companions
- LOCATION: Karbala, Mecca, Medina, historical battle sites, sacred places
- DATE: Islamic dates, significant historical events, religious occasions
- TIME: Periods, eras, historical timeframes
- ORGANIZATION: Armies, tribes, religious groups, historical institutions
- DESIGNATION: Titles, honorifics, roles in historical context
- NUMBER: Significant numerical values, dates, quantities

Focus on the religious and historical significance of entities in the context of the Battle of Karbala and related events.""",
            "custom": """{text}""",
        }

    @staticmethod
    def validate_prompt_template(template: str) -> bool:
        """Validate a custom prompt template."""
        if not template or len(template.strip()) < 50:
            return False

        # Check if template contains required placeholders
        if "{text}" not in template:
            return False

        return True
