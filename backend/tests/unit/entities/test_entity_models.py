"""
Unit tests for entities models.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from entities.models import EntityType, Entity, EntityRelationship
from documents.models import Document
from projects.models import Project

User = get_user_model()


class TestEntityTypeModel(TestCase):
    """Test EntityType model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            slug='test-project',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            content='This is a test document for entity extraction.',
            language='urdu',
            project=self.project,
            created_by=self.user
        )
    
    def test_entity_type_creation(self):
        """Test entity type creation."""
        entity_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people, prophets, Imams',
            color_code='#87CEEB',
            is_active=True
        )
        
        self.assertEqual(entity_type.name, 'PERSON')
        self.assertEqual(entity_type.description, 'Names of people, prophets, Imams')
        self.assertEqual(entity_type.color_code, '#87CEEB')
        self.assertTrue(entity_type.is_active)
        self.assertIsInstance(entity_type.metadata, dict)
    
    def test_entity_type_str_representation(self):
        """Test string representation of entity type."""
        entity_type = EntityType.objects.create(
            name='LOCATION',
            description='Places and locations',
            color_code='#90EE90'
        )
        
        expected_str = 'LOCATION'
        self.assertEqual(str(entity_type), expected_str)
    
    def test_entity_type_name_validation(self):
        """Test entity type name validation."""
        # Test with valid names
        valid_names = ['PERSON', 'LOCATION', 'DATE', 'TIME', 'ORGANIZATION', 'DESIGNATION', 'NUMBER']
        
        for name in valid_names:
            entity_type = EntityType.objects.create(
                name=name,
                description=f'Description for {name}'
            )
            self.assertEqual(entity_type.name, name)
        
        # Test with very long name
        long_name = 'A' * 50
        entity_type = EntityType.objects.create(
            name=long_name,
            description='Test description'
        )
        self.assertEqual(entity_type.name, long_name)
    
    def test_entity_type_color_code_validation(self):
        """Test entity type color code validation."""
        # Test with valid color codes
        valid_colors = ['#87CEEB', '#90EE90', '#F0E68C', '#DDA0DD', '#98FB98', '#F0F8FF']
        
        for color in valid_colors:
            entity_type = EntityType.objects.create(
                name=f'Type_{color.replace("#", "")}',
                description='Test description',
                color_code=color
            )
            self.assertEqual(entity_type.color_code, color)
        
        # Test with invalid color codes (should still work as it's just a CharField)
        invalid_colors = ['invalid', '123456', 'blue', '']
        
        for color in invalid_colors:
            entity_type = EntityType.objects.create(
                name=f'Type_{color}',
                description='Test description',
                color_code=color
            )
            self.assertEqual(entity_type.color_code, color)
    
    def test_entity_type_metadata(self):
        """Test entity type metadata field."""
        metadata = {
            'examples': ['Hazrat Ali', 'Imam Husayn', 'Prophet Muhammad'],
            'urdu_terms': ['حضرت علی', 'امام حسین', 'پیغمبر محمد'],
            'categories': ['religious', 'historical', 'prophetic']
        }
        
        entity_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            metadata=metadata
        )
        
        # Refresh from database
        entity_type.refresh_from_db()
        
        self.assertEqual(entity_type.metadata, metadata)
        self.assertEqual(entity_type.metadata['examples'], ['Hazrat Ali', 'Imam Husayn', 'Prophet Muhammad'])
        self.assertEqual(entity_type.metadata['urdu_terms'], ['حضرت علی', 'امام حسین', 'پیغمبر محمد'])
    
    def test_entity_type_ordering(self):
        """Test entity type ordering."""
        # Create entity types in random order
        EntityType.objects.create(name='Z_TYPE', description='Z type')
        EntityType.objects.create(name='A_TYPE', description='A type')
        EntityType.objects.create(name='M_TYPE', description='M type')
        
        # Get all entity types ordered by name
        entity_types = EntityType.objects.all().order_by('name')
        
        # Should be ordered alphabetically
        self.assertEqual(entity_types[0].name, 'A_TYPE')
        self.assertEqual(entity_types[1].name, 'M_TYPE')
        self.assertEqual(entity_types[2].name, 'Z_TYPE')
    
    def test_entity_type_unique_name(self):
        """Test entity type unique name constraint."""
        # Create first entity type
        EntityType.objects.create(
            name='UNIQUE_TYPE',
            description='First description'
        )
        
        # Try to create another with same name
        with self.assertRaises(Exception):
            EntityType.objects.create(
                name='UNIQUE_TYPE',
                description='Second description'
            )


class TestEntityModel(TestCase):
    """Test Entity model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            slug='test-project',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            content='This is a test document for entity extraction.',
            language='urdu',
            project=self.project,
            created_by=self.user
        )
        
        self.entity_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            color_code='#87CEEB'
        )
    
    def test_entity_creation(self):
        """Test entity creation."""
        entity = Entity.objects.create(
            document=self.document,
            text='Hazrat Ali',
            entity_type=self.entity_type,
            start_position=0,
            end_position=10,
            confidence=0.95,
            source='llm',
            is_verified=False
        )
        
        self.assertEqual(entity.document, self.document)
        self.assertEqual(entity.text, 'Hazrat Ali')
        self.assertEqual(entity.entity_type, self.entity_type)
        self.assertEqual(entity.start_position, 0)
        self.assertEqual(entity.end_position, 10)
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.source, 'llm')
        self.assertFalse(entity.is_verified)
        self.assertIsInstance(entity.metadata, dict)
    
    def test_entity_str_representation(self):
        """Test string representation of entity."""
        entity = Entity.objects.create(
            document=self.document,
            text='Karbala',
            entity_type=self.entity_type,
            start_position=15,
            end_position=22
        )
        
        expected_str = 'Karbala (PERSON) in Test Document'
        self.assertEqual(str(entity), expected_str)
    
    def test_entity_position_validation(self):
        """Test entity position validation."""
        # Test with valid positions
        entity = Entity.objects.create(
            document=self.document,
            text='Test Entity',
            entity_type=self.entity_type,
            start_position=0,
            end_position=10
        )
        
        self.assertEqual(entity.start_position, 0)
        self.assertEqual(entity.end_position, 10)
        
        # Test with positions at document boundaries
        entity2 = Entity.objects.create(
            document=self.document,
            text='End Entity',
            entity_type=self.entity_type,
            start_position=len(self.document.content) - 10,
            end_position=len(self.document.content)
        )
        
        self.assertEqual(entity2.start_position, len(self.document.content) - 10)
        self.assertEqual(entity2.end_position, len(self.document.content))
    
    def test_entity_confidence_validation(self):
        """Test entity confidence validation."""
        # Test with valid confidence values
        valid_confidences = [0.0, 0.5, 0.75, 1.0]
        
        for confidence in valid_confidences:
            entity = Entity.objects.create(
                document=self.document,
                text=f'Entity_{confidence}',
                entity_type=self.entity_type,
                start_position=0,
                end_position=10,
                confidence=confidence
            )
            self.assertEqual(entity.confidence, confidence)
        
        # Test with invalid confidence values (should still work as it's just a FloatField)
        invalid_confidences = [-0.1, 1.1, 2.0]
        
        for confidence in invalid_confidences:
            entity = Entity.objects.create(
                document=self.document,
                text=f'Entity_{confidence}',
                entity_type=self.entity_type,
                start_position=0,
                end_position=10,
                confidence=confidence
            )
            self.assertEqual(entity.confidence, confidence)
    
    def test_entity_source_choices(self):
        """Test entity source choices."""
        valid_sources = ['manual', 'llm', 'import', 'api']
        
        for source in valid_sources:
            entity = Entity.objects.create(
                document=self.document,
                text=f'Entity_{source}',
                entity_type=self.entity_type,
                start_position=0,
                end_position=10,
                source=source
            )
            self.assertEqual(entity.source, source)
    
    def test_entity_metadata(self):
        """Test entity metadata field."""
        metadata = {
            'llm_model': 'gpt-3.5-turbo',
            'prompt_type': 'marsiya',
            'processing_time': 1.5,
            'extraction_method': 'llm',
            'urdu_text': 'حضرت علی',
            'alternatives': ['Ali', 'علی'],
            'context': 'religious figure in Islamic history'
        }
        
        entity = Entity.objects.create(
            document=self.document,
            text='Hazrat Ali',
            entity_type=self.entity_type,
            start_position=0,
            end_position=10,
            metadata=metadata
        )
        
        # Refresh from database
        entity.refresh_from_db()
        
        self.assertEqual(entity.metadata, metadata)
        self.assertEqual(entity.metadata['llm_model'], 'gpt-3.5-turbo')
        self.assertEqual(entity.metadata['urdu_text'], 'حضرت علی')
    
    def test_entity_relationships(self):
        """Test entity relationships."""
        # Create another entity type
        location_type = EntityType.objects.create(
            name='LOCATION',
            description='Places and locations',
            color_code='#90EE90'
        )
        
        # Create entities
        person_entity = Entity.objects.create(
            document=self.document,
            text='Hazrat Ali',
            entity_type=self.entity_type,
            start_position=0,
            end_position=10
        )
        
        location_entity = Entity.objects.create(
            document=self.document,
            text='Karbala',
            entity_type=location_type,
            start_position=15,
            end_position=22
        )
        
        # Test document relationship
        self.assertEqual(person_entity.document, self.document)
        self.assertEqual(location_entity.document, self.document)
        
        # Test entity type relationship
        self.assertEqual(person_entity.entity_type, self.entity_type)
        self.assertEqual(location_entity.entity_type, location_type)
        
        # Test reverse relationships
        self.assertIn(person_entity, self.document.entities.all())
        self.assertIn(location_entity, self.document.entities.all())
        self.assertIn(person_entity, self.entity_type.entities.all())
        self.assertIn(location_entity, location_type.entities.all())
    
    def test_entity_verification_workflow(self):
        """Test entity verification workflow."""
        entity = Entity.objects.create(
            document=self.document,
            text='Unverified Entity',
            entity_type=self.entity_type,
            start_position=0,
            end_position=20,
            is_verified=False
        )
        
        # Initially not verified
        self.assertFalse(entity.is_verified)
        self.assertIsNone(entity.verified_by)
        self.assertIsNone(entity.verified_at)
        
        # Verify the entity
        entity.is_verified = True
        entity.verified_by = self.user
        entity.save()
        
        # Refresh from database
        entity.refresh_from_db()
        
        # Should now be verified
        self.assertTrue(entity.is_verified)
        self.assertEqual(entity.verified_by, self.user)
        self.assertIsNotNone(entity.verified_at)
    
    def test_entity_soft_delete(self):
        """Test entity soft deletion."""
        entity = Entity.objects.create(
            document=self.document,
            text='Test Entity',
            entity_type=self.entity_type,
            start_position=0,
            end_position=10
        )
        
        entity_id = entity.id
        
        # Soft delete the entity
        entity.is_deleted = True
        entity.deleted_by = self.user
        entity.save()
        
        # Entity should still exist in database
        self.assertTrue(Entity.objects.filter(id=entity_id).exists())
        
        # But should be marked as deleted
        deleted_entity = Entity.objects.get(id=entity_id)
        self.assertTrue(deleted_entity.is_deleted)
        self.assertEqual(deleted_entity.deleted_by, self.user)
        self.assertIsNotNone(deleted_entity.deleted_at)


class TestEntityRelationshipModel(TestCase):
    """Test EntityRelationship model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            slug='test-project',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            content='Hazrat Ali went to Karbala.',
            language='urdu',
            project=self.project,
            created_by=self.user
        )
        
        self.person_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            color_code='#87CEEB'
        )
        
        self.location_type = EntityType.objects.create(
            name='LOCATION',
            description='Places and locations',
            color_code='#90EE90'
        )
        
        self.person_entity = Entity.objects.create(
            document=self.document,
            text='Hazrat Ali',
            entity_type=self.person_type,
            start_position=0,
            end_position=10
        )
        
        self.location_entity = Entity.objects.create(
            document=self.document,
            text='Karbala',
            entity_type=self.location_type,
            start_position=15,
            end_position=22
        )
    
    def test_entity_relationship_creation(self):
        """Test entity relationship creation."""
        relationship = EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='WENT_TO',
            confidence=0.9,
            source='llm'
        )
        
        self.assertEqual(relationship.source_entity, self.person_entity)
        self.assertEqual(relationship.target_entity, self.location_type)
        self.assertEqual(relationship.relationship_type, 'WENT_TO')
        self.assertEqual(relationship.confidence, 0.9)
        self.assertEqual(relationship.source, 'llm')
        self.assertIsInstance(relationship.metadata, dict)
    
    def test_entity_relationship_str_representation(self):
        """Test string representation of entity relationship."""
        relationship = EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='WENT_TO'
        )
        
        expected_str = 'Hazrat Ali (PERSON) WENT_TO Karbala (LOCATION)'
        self.assertEqual(str(relationship), expected_str)
    
    def test_entity_relationship_types(self):
        """Test entity relationship types."""
        valid_types = ['WENT_TO', 'BORN_IN', 'DIED_IN', 'LEADER_OF', 'MEMBER_OF', 'FATHER_OF', 'SON_OF']
        
        for rel_type in valid_types:
            relationship = EntityRelationship.objects.create(
                source_entity=self.person_entity,
                target_entity=self.location_type,
                relationship_type=rel_type
            )
            self.assertEqual(relationship.relationship_type, rel_type)
    
    def test_entity_relationship_metadata(self):
        """Test entity relationship metadata field."""
        metadata = {
            'llm_model': 'gpt-3.5-turbo',
            'prompt_type': 'marsiya',
            'processing_time': 0.5,
            'context': 'historical event',
            'urdu_text': 'حضرت علی کربلا گئے',
            'confidence_factors': ['text_similarity', 'context_analysis', 'historical_knowledge']
        }
        
        relationship = EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='WENT_TO',
            metadata=metadata
        )
        
        # Refresh from database
        relationship.refresh_from_db()
        
        self.assertEqual(relationship.metadata, metadata)
        self.assertEqual(relationship.metadata['llm_model'], 'gpt-3.5-turbo')
        self.assertEqual(relationship.metadata['urdu_text'], 'حضرت علی کربلا گئے')
    
    def test_entity_relationship_confidence(self):
        """Test entity relationship confidence."""
        # Test with valid confidence values
        valid_confidences = [0.0, 0.5, 0.75, 1.0]
        
        for confidence in valid_confidences:
            relationship = EntityRelationship.objects.create(
                source_entity=self.person_entity,
                target_entity=self.location_type,
                relationship_type='WENT_TO',
                confidence=confidence
            )
            self.assertEqual(relationship.confidence, confidence)
    
    def test_entity_relationship_source_choices(self):
        """Test entity relationship source choices."""
        valid_sources = ['manual', 'llm', 'import', 'api', 'inference']
        
        for source in valid_sources:
            relationship = EntityRelationship.objects.create(
                source_entity=self.person_entity,
                target_entity=self.location_type,
                relationship_type='WENT_TO',
                source=source
            )
            self.assertEqual(relationship.source, source)
    
    def test_entity_relationship_ordering(self):
        """Test entity relationship ordering."""
        # Create relationships in random order
        EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='WENT_TO'
        )
        
        EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='BORN_IN'
        )
        
        # Get all relationships ordered by created_at
        relationships = EntityRelationship.objects.all().order_by('created_at')
        
        # Should be ordered by creation time
        self.assertEqual(len(relationships), 2)
        self.assertEqual(relationships[0].relationship_type, 'WENT_TO')
        self.assertEqual(relationships[1].relationship_type, 'BORN_IN')
    
    def test_entity_relationship_soft_delete(self):
        """Test entity relationship soft deletion."""
        relationship = EntityRelationship.objects.create(
            source_entity=self.person_entity,
            target_entity=self.location_type,
            relationship_type='WENT_TO'
        )
        
        relationship_id = relationship.id
        
        # Soft delete the relationship
        relationship.is_deleted = True
        relationship.deleted_by = self.user
        relationship.save()
        
        # Relationship should still exist in database
        self.assertTrue(EntityRelationship.objects.filter(id=relationship_id).exists())
        
        # But should be marked as deleted
        deleted_relationship = EntityRelationship.objects.get(id=relationship_id)
        self.assertTrue(deleted_relationship.is_deleted)
        self.assertEqual(deleted_relationship.deleted_by, self.user)
        self.assertIsNotNone(deleted_relationship.deleted_at)


class TestEntityModelsIntegration(TestCase):
    """Integration tests for entity models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            slug='test-project',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            content='Hazrat Ali went to Karbala with his companions.',
            language='urdu',
            project=self.project,
            created_by=self.user
        )
        
        self.person_type = EntityType.objects.create(
            name='PERSON',
            description='Names of people',
            color_code='#87CEEB'
        )
        
        self.location_type = EntityType.objects.create(
            name='LOCATION',
            description='Places and locations',
            color_code='#90EE90'
        )
        
        self.organization_type = EntityType.objects.create(
            name='ORGANIZATION',
            description='Groups and organizations',
            color_code='#FFA500'
        )
    
    def test_complete_entity_workflow(self):
        """Test complete entity creation and relationship workflow."""
        # Create entities
        ali_entity = Entity.objects.create(
            document=self.document,
            text='Hazrat Ali',
            entity_type=self.person_type,
            start_position=0,
            end_position=10,
            confidence=0.95,
            source='llm'
        )
        
        karbala_entity = Entity.objects.create(
            document=self.document,
            text='Karbala',
            entity_type=self.location_type,
            start_position=15,
            end_position=22,
            confidence=0.98,
            source='llm'
        )
        
        companions_entity = Entity.objects.create(
            document=self.document,
            text='companions',
            entity_type=self.organization_type,
            start_position=27,
            end_position=37,
            confidence=0.85,
            source='llm'
        )
        
        # Create relationships
        went_to_relationship = EntityRelationship.objects.create(
            source_entity=ali_entity,
            target_entity=karbala_entity,
            relationship_type='WENT_TO',
            confidence=0.9,
            source='llm'
        )
        
        led_relationship = EntityRelationship.objects.create(
            source_entity=ali_entity,
            target_entity=companions_entity,
            relationship_type='LED',
            confidence=0.95,
            source='llm'
        )
        
        # Verify all entities exist
        self.assertEqual(Entity.objects.count(), 3)
        self.assertEqual(EntityRelationship.objects.count(), 2)
        
        # Verify entity types
        self.assertEqual(EntityType.objects.count(), 3)
        
        # Verify relationships
        self.assertEqual(ali_entity.outgoing_relationships.count(), 2)
        self.assertEqual(karbala_entity.incoming_relationships.count(), 1)
        self.assertEqual(companions_entity.incoming_relationships.count(), 1)
        
        # Verify document entities
        document_entities = self.document.entities.all()
        self.assertEqual(document_entities.count(), 3)
        
        # Verify entity type entities
        person_entities = self.person_type.entities.all()
        self.assertEqual(person_entities.count(), 1)
        self.assertEqual(person_entities[0], ali_entity)
    
    def test_entity_verification_workflow(self):
        """Test complete entity verification workflow."""
        # Create unverified entity
        entity = Entity.objects.create(
            document=self.document,
            text='Unverified Entity',
            entity_type=self.person_type,
            start_position=0,
            end_position=20,
            is_verified=False,
            source='llm'
        )
        
        # Verify the entity
        entity.is_verified = True
        entity.verified_by = self.user
        entity.save()
        
        # Refresh from database
        entity.refresh_from_db()
        
        # Should now be verified
        self.assertTrue(entity.is_verified)
        self.assertEqual(entity.verified_by, self.user)
        self.assertIsNotNone(entity.verified_at)
        
        # Check verification status
        verified_entities = self.document.entities.filter(is_verified=True)
        self.assertEqual(verified_entities.count(), 1)
        self.assertEqual(verified_entities[0], entity)
    
    def test_entity_statistics(self):
        """Test entity statistics and counting."""
        # Create multiple entities
        entities_data = [
            ('Hazrat Ali', 'PERSON', 0, 10),
            ('Karbala', 'LOCATION', 15, 22),
            ('companions', 'ORGANIZATION', 27, 37),
            ('Imam Husayn', 'PERSON', 40, 50),
            ('Mecca', 'LOCATION', 55, 60)
        ]
        
        for text, entity_type_name, start, end in entities_data:
            entity_type = EntityType.objects.get(name=entity_type_name)
            Entity.objects.create(
                document=self.document,
                text=text,
                entity_type=entity_type,
                start_position=start,
                end_position=end,
                source='llm'
            )
        
        # Test entity counts
        self.assertEqual(Entity.objects.count(), 5)
        self.assertEqual(self.document.entities.count(), 5)
        
        # Test entity type counts
        self.assertEqual(self.person_type.entities.count(), 2)
        self.assertEqual(self.location_type.entities.count(), 2)
        self.assertEqual(self.organization_type.entities.count(), 1)
        
        # Test verified vs unverified counts
        unverified_entities = self.document.entities.filter(is_verified=False)
        self.assertEqual(unverified_entities.count(), 5)
        
        # Verify some entities
        person_entities = self.document.entities.filter(entity_type=self.person_type)
        for entity in person_entities:
            entity.is_verified = True
            entity.verified_by = self.user
            entity.save()
        
        verified_entities = self.document.entities.filter(is_verified=True)
        self.assertEqual(verified_entities.count(), 2)
        self.assertEqual(verified_entities.count(), person_entities.count())
