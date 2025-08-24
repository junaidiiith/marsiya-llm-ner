# User Guide - Urdu Marsiya NER Web Application

## Overview

Welcome to the Urdu Marsiya NER (Named Entity Recognition) application! This tool helps researchers identify, annotate, and verify named entities in Urdu Marsiya poetry using AI assistance and human verification.

## Getting Started

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

### For Project Managers

#### Workflow Design

- **Define standards**: Establish annotation guidelines
- **Assign roles**: Distribute verification tasks
- **Set milestones**: Create timeline for completion
- **Monitor progress**: Track verification rates and quality

#### Team Coordination

- **Regular meetings**: Schedule review sessions
- **Training**: Provide training on annotation standards
- **Feedback loops**: Establish processes for questions and clarifications
- **Documentation**: Maintain project documentation and guidelines

## Troubleshooting

### Common Issues

#### Processing Problems

- **Slow processing**: Check file size and chunk settings
- **API errors**: Verify AI model configuration
- **Memory issues**: Reduce chunk size for large documents
- **Connection problems**: Check internet connectivity

#### Entity Issues

- **Missing entities**: Lower confidence threshold
- **Wrong entity types**: Use manual correction tools
- **Overlapping entities**: Review entity boundaries
- **Inconsistent tagging**: Follow annotation guidelines

#### Interface Problems

- **Display issues**: Check browser compatibility
- **Performance**: Clear browser cache and cookies
- **Login problems**: Reset password or contact support
- **Data loss**: Check auto-save settings

### Getting Help

#### Support Resources

- **Help documentation**: Access built-in help system
- **Video tutorials**: Watch step-by-step guides
- **FAQ section**: Find answers to common questions
- **Contact support**: Reach out to technical team

#### Community

- **User forums**: Connect with other researchers
- **Training sessions**: Attend online workshops
- **Best practices**: Share experiences and tips
- **Feature requests**: Suggest improvements

## Tips and Tricks

### Efficiency Tips

- **Use keyboard shortcuts**: Learn navigation shortcuts for faster work
- **Batch operations**: Process multiple entities together
- **Template projects**: Create project templates for similar research
- **Auto-save**: Enable auto-save to prevent data loss

### Quality Tips

- **Regular breaks**: Take breaks to maintain focus
- **Peer review**: Have colleagues review your annotations
- **Source verification**: Cross-reference entities with reliable sources
- **Documentation**: Keep notes on difficult annotation decisions

### Research Tips

- **Start small**: Begin with shorter texts to learn the system
- **Iterate**: Refine annotations based on new insights
- **Collaborate**: Work with team members on complex texts
- **Export regularly**: Save your work in multiple formats

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
