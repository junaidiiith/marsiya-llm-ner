# Urdu Marsiya NER Web Application

## Project Overview

This application helps researchers, particularly in digital humanities, to identify, annotate, and verify named entities in Urdu Marsiya poetry. The tool combines AI-powered entity recognition with human verification to ensure accuracy in identifying entities such as people, locations, dates, and more within historical and religious texts.

## Demo Video

See the application in action! Watch our demo video showcasing the key features and user interface:

<video width="100%" controls>
  <source src="demo/marsiya-ner-dashboard-demo.mov" type="video/quicktime">
  Your browser does not support the video tag.
</video>

**Alternative Viewing Options:**

- [Download Video](demo/marsiya-ner-dashboard-demo.mov) - Right-click and "Save as" for offline viewing
- [View on GitHub](https://github.com/junaidiiith/marsiya-llm-ner/blob/main/demo/marsiya-ner-dashboard-demo.mov) - Watch directly on GitHub

**Video Details:**

- **Format**: MOV (QuickTime)
- **Size**: ~70MB
- **Duration**: Comprehensive walkthrough of all major features
- **Quality**: High-definition screen recording

_Note: The demo video shows the complete user experience including document upload, entity recognition, verification workflow, and project management features._

## Documentation Structure

- **[Design Plan](./design-plan.md)** - Complete technical design and architecture
- **[API Documentation](./api-documentation.md)** - Backend API endpoints and specifications
- **[Database Schema](./database-schema.md)** - Data models and relationships
- **[Frontend Architecture](./frontend-architecture.md)** - React component structure and state management
- **[LLM Integration](./llm-integration.md)** - AI model integration details
- **[Deployment Guide](./deployment-guide.md)** - Setup and deployment instructions
- **[User Guide](./user-guide.md)** - End-user documentation

## Quick Start

1. **Watch the Demo**: Start with our [demo video](#demo-video) to see the application in action
2. Review the [Design Plan](./design-plan.md) for complete technical specifications
3. Check [API Documentation](./api-documentation.md) for backend endpoints
4. Review [Frontend Architecture](./frontend-architecture.md) for UI/UX details
5. Follow [Deployment Guide](./deployment-guide.md) for setup instructions

## Live Demo

Want to see the application working? Check out our demo video that demonstrates:

🎯 **Key Features Shown:**

- User authentication and dashboard overview
- Document upload and processing workflow
- AI-powered entity recognition in action
- Interactive entity verification interface
- Project management and collaboration tools
- Real-time processing and status updates

📱 **User Experience Highlights:**

- Clean, intuitive interface design
- Responsive layout for all devices
- Smooth workflow from upload to verification
- Professional-grade entity annotation tools

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Frontend**: React 18+ with Redux Toolkit
- **Database**: PostgreSQL (recommended) or SQLite (development)
- **AI Integration**: Multiple LLM APIs (OpenAI, Anthropic, local models)
- **Deployment**: Docker, Nginx, Gunicorn

## User Guide

Welcome to the Urdu Marsiya NER (Named Entity Recognition) application! This tool helps researchers identify, annotate, and verify named entities in Urdu Marsiya poetry using AI assistance and human verification.

### 1. Account Creation

- Visit the application website
- Click "Register" to create a new account
- Provide your email, name, and research interests
- Verify your email address

### 2. First Login

- Use your email and password to log in
- Complete your profile with research information
- Set your preferences for language and interface

### 3. Dashboard Overview

The dashboard provides:

- Recent documents and projects
- Processing statistics
- Quick access to common actions
- System notifications

## Core Features

### Text Upload and Processing

#### Option 1: File Upload

1. Click "Upload Document" from the dashboard
2. Select your Urdu text file (.txt, .docx, .pdf)
3. Choose a project or create a new one
4. Select an AI model for entity recognition
5. Click "Start Processing"

#### Option 2: Text Paste

1. Click "Paste Text" from the dashboard
2. Copy and paste your Urdu text
3. Add a title and description
4. Select processing options
5. Click "Process Text"

#### Processing Options

- **Chunk Size**: How much text to process at once (default: 1000 characters)
- **Confidence Threshold**: Minimum confidence for AI suggestions (default: 70%)
- **Entity Types**: Which entity types to focus on
- **Language Model**: Choose from available AI models

### Understanding Entity Types

The application recognizes these entity categories:

| Entity Type      | Description                              | Color           | Examples          |
| ---------------- | ---------------------------------------- | --------------- | ----------------- |
| **PERSON**       | Names of people, prophets, Imams         | 🔵 Light Blue   | حسین، علی، فاطمہ  |
| **LOCATION**     | Places, landmarks, geographical features | 🟢 Light Green  | کربلا، مدینہ، مکہ |
| **DATE**         | Dates, Islamic months, specific days     | 🟡 Light Yellow | عاشورا، محرم، 10  |
| **TIME**         | Time references and periods              | 🟣 Light Pink   | صبح، شام، رات     |
| **ORGANIZATION** | Groups, tribes, armies, institutions     | 🟠 Light Orange | بنی ہاشم، اہل بیت |
| **DESIGNATION**  | Titles, honorifics, roles                | ⚪ Light Gray   | امام، خلیفہ، شہید |
| **NUMBER**       | Numerically significant values           | 🟣 Light Purple | 72، 40، 1000      |

### Reviewing and Editing Entities

#### Interactive Text Viewer

- **Line-by-line navigation**: Use arrow keys or click to move between lines
- **Entity highlighting**: Entities are color-coded by type
- **Click to edit**: Click on any entity to modify its properties
- **Keyboard shortcuts**: Use Tab, Enter, and Escape for navigation

#### Entity Verification

1. **Review AI suggestions**: Check each highlighted entity
2. **Verify correct entities**: Click the checkmark to confirm
3. **Edit incorrect entities**: Click to change entity type or boundaries
4. **Add missing entities**: Select text and choose entity type
5. **Remove wrong entities**: Click delete button for incorrect tags

#### Bulk Operations

- **Select multiple entities**: Use Ctrl+Click or Shift+Click
- **Bulk verify**: Verify multiple entities at once
- **Bulk edit**: Change entity types for multiple selections
- **Bulk delete**: Remove multiple incorrect entities

### Project Management

#### Creating Projects

1. Click "New Project" from the dashboard
2. Enter project name and description
3. Set research area and methodology
4. Add team members (optional)
5. Choose privacy settings

#### Organizing Documents

- **Group by project**: Organize documents within research projects
- **Add tags**: Use tags to categorize documents
- **Set priorities**: Mark important documents for review
- **Track progress**: Monitor processing and verification status

#### Collaboration Features

- **Invite researchers**: Add team members to projects
- **Assign roles**: Set permissions for different users
- **Share results**: Export and share annotated data
- **Version control**: Track changes and document versions

## Advanced Features

### Export and Analysis

#### Excel Export

1. Select document or project
2. Click "Export" button
3. Choose export format (Excel)
4. Select data to include:
   - Entity details
   - Verification status
   - Confidence scores
   - Metadata
5. Download the file

#### Email Export

1. Click "Email Export" option
2. Enter recipient email addresses
3. Add custom message
4. Choose export format
5. Send annotated data directly

#### Statistical Analysis

- **Entity distribution**: View counts by entity type
- **Verification rates**: Track progress on entity verification
- **Processing metrics**: Monitor AI performance
- **Quality scores**: Assess annotation quality

### Customization

#### User Preferences

- **Interface language**: English or Urdu
- **Theme**: Light or dark mode
- **Text size**: Adjust font sizes for readability
- **Keyboard shortcuts**: Customize navigation keys

#### Processing Settings

- **Default models**: Set preferred AI models
- **Confidence thresholds**: Adjust sensitivity levels
- **Entity type priorities**: Focus on specific categories
- **Batch processing**: Configure chunk sizes and overlap

## Best Practices

### For Researchers

#### Text Preparation

- **Clean formatting**: Remove unnecessary formatting before upload
- **Consistent encoding**: Use UTF-8 encoding for Urdu text
- **File size**: Keep files under 50MB for optimal processing
- **Language consistency**: Ensure text is primarily in Urdu

#### Entity Annotation

- **Start with AI**: Let AI identify entities first
- **Verify systematically**: Review entities line by line
- **Be consistent**: Use consistent entity type assignments
- **Document decisions**: Add notes for complex cases

#### Quality Control

- **Regular reviews**: Periodically review verified entities
- **Cross-reference**: Check entities against reliable sources
- **Team validation**: Have multiple researchers review important texts
- **Update annotations**: Refine annotations based on new insights


## Glossary

- **NER**: Named Entity Recognition - identifying and classifying named entities in text
- **Entity**: A named object, person, place, date, or concept in text
- **Verification**: Confirming that an AI-identified entity is correct
- **Chunk**: A portion of text processed by the AI model
- **Confidence Score**: AI model's certainty about an entity identification
- **Processing Job**: Background task for analyzing text with AI
- **Export**: Downloading annotated data in various formats
- **Project**: Collection of related documents and annotations
- **Tag**: Label for categorizing documents or entities
- **Annotation**: Process of marking and labeling entities in text

This user guide provides comprehensive instructions for using the Marsiya NER application effectively in your research workflow.
