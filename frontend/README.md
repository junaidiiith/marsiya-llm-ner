# Marsiya LLM NER Frontend

A modern, fast React frontend for the Marsiya LLM NER application, built with Vite and TypeScript.

## Features

- 🚀 **Fast Development** - Built with Vite for lightning-fast development and build times
- 🎨 **Modern UI** - Beautiful, responsive design with Tailwind CSS
- 📱 **Mobile First** - Responsive design that works on all devices
- 🔄 **Real-time Updates** - Live processing status and entity extraction
- 📊 **Interactive Dashboard** - Comprehensive overview of your NER projects
- 📁 **Document Management** - Upload, process, and manage documents
- 🏷️ **Entity Visualization** - Browse and analyze extracted entities
- ⚙️ **Project Management** - Create and configure NER projects
- 🔧 **Advanced Settings** - Comprehensive configuration options

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 4
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Forms**: React Hook Form with Zod validation
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with navigation
│   └── ui/             # Basic UI components
├── pages/              # Page components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Documents.tsx   # Document management
│   ├── Entities.tsx    # Entity browsing
│   ├── Processing.tsx  # Job monitoring
│   ├── Projects.tsx    # Project management
│   └── Settings.tsx    # Application settings
├── lib/                # Utility functions
│   └── utils.ts        # Common utilities
├── App.tsx             # Main app component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Features Overview

### Dashboard

- Overview statistics and metrics
- Recent activity feed
- Quick action buttons
- Processing status monitoring

### Documents

- Drag & drop file upload
- Document status tracking
- Search and filtering
- Bulk operations

### Entities

- Entity type categorization
- Confidence scoring
- Context visualization
- Export capabilities

### Processing

- Real-time job monitoring
- Progress tracking
- Job management (pause, resume, stop)
- Error handling and retry

### Projects

- Project creation and configuration
- Entity type selection
- Model configuration
- Team collaboration

### Settings

- User profile management
- Security settings
- API configuration
- Notification preferences
- Appearance customization
- Data management

## API Integration

The frontend is configured to communicate with the Django backend API. The API proxy is configured in `vite.config.ts` to forward `/api` requests to `http://localhost:8000`.

## Styling

The application uses Tailwind CSS with a custom design system:

- **Primary Colors**: Blue-based palette for main actions
- **Secondary Colors**: Gray-based palette for secondary elements
- **Accent Colors**: Purple-based palette for highlights
- **Responsive Design**: Mobile-first approach with breakpoint-based layouts

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new components
3. Implement proper error handling
4. Add appropriate loading states
5. Ensure responsive design
6. Write meaningful commit messages

## Deployment

### Production Build

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment to any static hosting service.

### Environment Variables

Create a `.env` file in the frontend directory for environment-specific configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Marsiya NER
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lazy loading of page components
- Optimized bundle splitting
- Efficient state management
- Minimal re-renders with React.memo
- Optimized animations with Framer Motion

## License

This project is licensed under the MIT License.
