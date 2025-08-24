# Frontend Architecture - Urdu Marsiya NER Web Application

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Component Architecture](#component-architecture)
5. [State Management](#state-management)
6. [Routing and Navigation](#routing-and-navigation)
7. [UI/UX Design](#uiux-design)
8. [Performance Optimization](#performance-optimization)
9. [Internationalization](#internationalization)
10. [Testing Strategy](#testing-strategy)
11. [Build and Deployment](#build-and-deployment)

## Overview

The frontend is built using React 18+ with modern JavaScript features and follows a component-based architecture. The application provides an intuitive interface for researchers to upload, process, and annotate Urdu Marsiya poetry texts with AI-powered entity recognition.

### Key Features

- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Real-time Updates**: WebSocket integration for live processing updates
- **Accessibility**: WCAG 2.1 AA compliance with keyboard navigation
- **Performance**: Virtual scrolling, lazy loading, and optimization techniques
- **Internationalization**: Support for Urdu (RTL) and English languages

## Technology Stack

### Core Technologies

- **React 18+**: Latest React with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server

### State Management

- **Redux Toolkit**: Modern Redux with RTK Query
- **React Query**: Server state management
- **Zustand**: Lightweight state management for UI state

### UI Framework

- **Material-UI (MUI)**: Component library with custom theme
- **Emotion**: CSS-in-JS styling solution
- **React Hook Form**: Form handling and validation

### Development Tools

- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **Husky**: Git hooks for code quality
- **Storybook**: Component development and documentation

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   ├── manifest.json
│   └── locales/           # Translation files
├── src/
│   ├── index.tsx          # Application entry point
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # React 18 root rendering
│   ├── vite-env.d.ts      # Vite type definitions
│   ├── components/         # Reusable components
│   ├── pages/             # Page components
│   ├── features/          # Feature-based modules
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API and external services
│   ├── store/             # Redux store configuration
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── styles/            # Global styles and themes
│   └── assets/            # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

### Feature-Based Organization

```
src/features/
├── auth/                  # Authentication feature
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── index.ts
├── documents/             # Document management
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── index.ts
├── entities/              # Entity management
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── index.ts
├── projects/              # Project management
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── index.ts
└── processing/            # Text processing
    ├── components/
    ├── hooks/
    ├── services/
    ├── types/
    └── index.ts
```

## Component Architecture

### Component Hierarchy

```
App
├── Layout
│   ├── Header
│   ├── Sidebar
│   └── MainContent
├── Router
│   ├── Dashboard
│   ├── DocumentUpload
│   ├── DocumentViewer
│   ├── EntityEditor
│   └── Settings
└── Providers
    ├── ReduxProvider
    ├── ThemeProvider
    └── AuthProvider
```

### Component Categories

#### 1. Layout Components

- **App**: Main application wrapper
- **Layout**: Page layout with header, sidebar, and content
- **Header**: Navigation bar with user info and actions
- **Sidebar**: Project and document navigation
- **MainContent**: Dynamic content area with routing

#### 2. Page Components

- **Dashboard**: Overview with statistics and recent documents
- **DocumentUpload**: File upload and text input interface
- **DocumentViewer**: Interactive text viewing with entity editing
- **EntityEditor**: Entity management and verification interface
- **Settings**: User preferences and system configuration

#### 3. Feature Components

- **TextViewer**: Main text display with entity highlighting
- **EntityTag**: Individual entity display component
- **ProcessingStatus**: Job progress and status indicators
- **ExportModal**: Data export options and configuration
- **StatisticsChart**: Data visualization components

#### 4. Common Components

- **Button**: Reusable button component with variants
- **Input**: Form input components
- **Modal**: Modal dialog component
- **Loading**: Loading spinner and skeleton components
- **ErrorBoundary**: Error handling component

### Component Design Principles

#### 1. Single Responsibility

Each component should have a single, well-defined purpose.

#### 2. Composition over Inheritance

Use component composition to build complex UIs from simple components.

#### 3. Props Interface

Define clear prop interfaces with TypeScript for better maintainability.

#### 4. Controlled vs Uncontrolled

Use controlled components for form inputs and uncontrolled for simple displays.

## State Management

### Redux Store Structure

```typescript
interface RootState {
  auth: AuthState;
  documents: DocumentsState;
  entities: EntitiesState;
  processing: ProcessingState;
  projects: ProjectsState;
  settings: SettingsState;
  ui: UIState;
}
```

### State Slices

#### Auth State

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  refreshToken: string | null;
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.refreshToken = null;
    },
  },
});
```

#### Documents State

```typescript
interface DocumentsState {
  list: Document[];
  current: Document | null;
  loading: boolean;
  error: string | null;
  filters: DocumentFilters;
  pagination: PaginationState;
}

const documentsSlice = createSlice({
  name: "documents",
  initialState,
  reducers: {
    setDocuments: (state, action) => {
      state.list = action.payload;
    },
    setCurrentDocument: (state, action) => {
      state.current = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    updatePagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
  },
});
```

#### Entities State

```typescript
interface EntitiesState {
  list: Entity[];
  selected: Entity | null;
  editing: Entity | null;
  loading: boolean;
  error: string | null;
  filters: EntityFilters;
}

const entitiesSlice = createSlice({
  name: "entities",
  initialState,
  reducers: {
    setEntities: (state, action) => {
      state.list = action.payload;
    },
    setSelectedEntity: (state, action) => {
      state.selected = action.payload;
    },
    setEditingEntity: (state, action) => {
      state.editing = action.payload;
    },
    updateEntity: (state, action) => {
      const index = state.list.findIndex((e) => e.id === action.payload.id);
      if (index !== -1) {
        state.list[index] = action.payload;
      }
    },
    addEntity: (state, action) => {
      state.list.push(action.payload);
    },
    removeEntity: (state, action) => {
      state.list = state.list.filter((e) => e.id !== action.payload);
    },
  },
});
```

### RTK Query Integration

```typescript
// API service definitions
export const documentsApi = createApi({
  reducerPath: "documentsApi",
  baseQuery: fetchBaseQuery({
    baseUrl: "/api/",
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["Document", "Entity"],
  endpoints: (builder) => ({
    getDocuments: builder.query<
      PaginatedResponse<Document>,
      GetDocumentsParams
    >({
      query: (params) => ({
        url: "documents/",
        params,
      }),
      providesTags: ["Document"],
    }),
    getDocument: builder.query<Document, number>({
      query: (id) => `documents/${id}/`,
      providesTags: (result, error, id) => [{ type: "Document", id }],
    }),
    createDocument: builder.mutation<Document, CreateDocumentRequest>({
      query: (body) => ({
        url: "documents/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Document"],
    }),
    updateDocument: builder.mutation<Document, UpdateDocumentRequest>({
      query: ({ id, ...body }) => ({
        url: `documents/${id}/`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Document", id },
        "Document",
      ],
    }),
  }),
});
```

### Custom Hooks

```typescript
// Custom hooks for state management
export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, loading, error } = useAppSelector(
    (state) => state.auth
  );

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        dispatch(setLoading(true));
        const response = await authApi.login(credentials);
        dispatch(setUser(response.user));
        localStorage.setItem("refreshToken", response.refresh_token);
        return response;
      } catch (error) {
        dispatch(setError(error.message));
        throw error;
      } finally {
        dispatch(setLoading(false));
      }
    },
    [dispatch]
  );

  const logout = useCallback(() => {
    dispatch(logout());
    localStorage.removeItem("refreshToken");
  }, [dispatch]);

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
  };
};

export const useDocuments = () => {
  const dispatch = useAppDispatch();
  const { list, current, loading, error, filters, pagination } = useAppSelector(
    (state) => state.documents
  );

  const fetchDocuments = useCallback(
    async (params?: GetDocumentsParams) => {
      try {
        dispatch(setLoading(true));
        const response = await documentsApi.getDocuments(params || filters);
        dispatch(setDocuments(response.results));
        dispatch(
          updatePagination({
            count: response.count,
            next: response.next,
            previous: response.previous,
          })
        );
      } catch (error) {
        dispatch(setError(error.message));
      } finally {
        dispatch(setLoading(false));
      }
    },
    [dispatch, filters]
  );

  return {
    documents: list,
    currentDocument: current,
    loading,
    error,
    filters,
    pagination,
    fetchDocuments,
    setCurrentDocument: (doc: Document) => dispatch(setCurrentDocument(doc)),
    setFilters: (filters: Partial<DocumentFilters>) =>
      dispatch(setFilters(filters)),
  };
};
```

## Routing and Navigation

### Route Configuration

```typescript
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: "projects",
        element: <Projects />,
      },
      {
        path: "projects/:projectId",
        element: <ProjectDetail />,
      },
      {
        path: "documents",
        element: <Documents />,
      },
      {
        path: "documents/upload",
        element: <DocumentUpload />,
      },
      {
        path: "documents/:documentId",
        element: <DocumentViewer />,
      },
      {
        path: "entities",
        element: <Entities />,
      },
      {
        path: "settings",
        element: <Settings />,
      },
    ],
  },
  {
    path: "/auth",
    element: <AuthLayout />,
    children: [
      {
        path: "login",
        element: <Login />,
      },
      {
        path: "register",
        element: <Register />,
      },
      {
        path: "forgot-password",
        element: <ForgotPassword />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}
```

### Protected Routes

```typescript
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = [],
}) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.some((permission) =>
      user.permissions.includes(permission)
    );

    if (!hasPermission) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};
```

### Navigation Components

```typescript
// Sidebar navigation
export const Sidebar: React.FC = () => {
  const { projects, currentProject } = useProjects();
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    {
      label: "Dashboard",
      icon: <DashboardIcon />,
      path: "/",
      active: location.pathname === "/",
    },
    {
      label: "Projects",
      icon: <FolderIcon />,
      path: "/projects",
      active: location.pathname.startsWith("/projects"),
    },
    {
      label: "Documents",
      icon: <DescriptionIcon />,
      path: "/documents",
      active: location.pathname.startsWith("/documents"),
    },
    {
      label: "Entities",
      icon: <TagIcon />,
      path: "/entities",
      active: location.pathname.startsWith("/entities"),
    },
    {
      label: "Settings",
      icon: <SettingsIcon />,
      path: "/settings",
      active: location.pathname.startsWith("/settings"),
    },
  ];

  return (
    <Box
      sx={{
        width: 280,
        flexShrink: 0,
        borderRight: 1,
        borderColor: "divider",
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="h2">
          Marsiya NER
        </Typography>
      </Box>

      <List>
        {navigationItems.map((item) => (
          <ListItem
            key={item.path}
            button
            selected={item.active}
            onClick={() => navigate(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>

      {currentProject && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
          <Typography variant="subtitle2" color="text.secondary">
            Current Project
          </Typography>
          <Typography variant="body2">{currentProject.name}</Typography>
        </Box>
      )}
    </Box>
  );
};
```

## UI/UX Design

### Design System

#### Color Palette

```typescript
export const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
      light: "#42a5f5",
      dark: "#1565c0",
    },
    secondary: {
      main: "#dc004e",
      light: "#ff5983",
      dark: "#9a0036",
    },
    // Entity type colors
    entity: {
      person: "#87CEEB", // Light Blue
      location: "#90EE90", // Light Green
      date: "#FFFFE0", // Light Yellow
      time: "#FFC0CB", // Light Pink
      organization: "#FFA500", // Light Orange
      designation: "#D3D3D3", // Light Gray
      number: "#E6E6FA", // Light Purple
    },
    background: {
      default: "#fafafa",
      paper: "#ffffff",
    },
    text: {
      primary: "#212121",
      secondary: "#757575",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 300,
    },
    h2: {
      fontSize: "2rem",
      fontWeight: 300,
    },
    h3: {
      fontSize: "1.75rem",
      fontWeight: 400,
    },
    h4: {
      fontSize: "1.5rem",
      fontWeight: 400,
    },
    h5: {
      fontSize: "1.25rem",
      fontWeight: 400,
    },
    h6: {
      fontSize: "1rem",
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        },
      },
    },
  },
});
```

#### Component Variants

```typescript
// Button variants
export const ButtonVariants = {
  primary: {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    "&:hover": {
      backgroundColor: theme.palette.primary.dark,
    },
  },
  secondary: {
    backgroundColor: theme.palette.secondary.main,
    color: theme.palette.secondary.contrastText,
    "&:hover": {
      backgroundColor: theme.palette.secondary.dark,
    },
  },
  success: {
    backgroundColor: "#4caf50",
    color: "#ffffff",
    "&:hover": {
      backgroundColor: "#388e3c",
    },
  },
  warning: {
    backgroundColor: "#ff9800",
    color: "#ffffff",
    "&:hover": {
      backgroundColor: "#f57c00",
    },
  },
  error: {
    backgroundColor: "#f44336",
    color: "#ffffff",
    "&:hover": {
      backgroundColor: "#d32f2f",
    },
  },
};
```

### Responsive Design

#### Breakpoints

```typescript
export const breakpoints = {
  xs: 0, // Extra small devices (phones)
  sm: 600, // Small devices (tablets)
  md: 960, // Medium devices (desktops)
  lg: 1280, // Large devices (desktops)
  xl: 1920, // Extra large devices (large desktops)
};

// Responsive utility hooks
export const useResponsive = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.between("sm", "md"));
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const isLargeDesktop = useMediaQuery(theme.breakpoints.up("lg"));

  return {
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
  };
};
```

#### Mobile-First Approach

```typescript
// Responsive component example
export const DocumentCard: React.FC<DocumentCardProps> = ({ document }) => {
  const { isMobile, isTablet } = useResponsive();

  return (
    <Card
      sx={{
        width: isMobile ? "100%" : isTablet ? "calc(50% - 16px)" : "300px",
        mb: 2,
        mr: isMobile ? 0 : 2,
      }}
    >
      <CardContent>
        <Typography
          variant={isMobile ? "h6" : "h5"}
          component="h3"
          gutterBottom
        >
          {document.title}
        </Typography>

        {!isMobile && (
          <Typography variant="body2" color="text.secondary">
            {document.description}
          </Typography>
        )}

        <Box sx={{ mt: 2, display: "flex", justifyContent: "space-between" }}>
          <Chip
            label={document.processing_status}
            color={getStatusColor(document.processing_status)}
            size={isMobile ? "small" : "medium"}
          />
          <Typography variant="caption">
            {formatDate(document.created_at)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
```

### Accessibility Features

#### Keyboard Navigation

```typescript
// Keyboard navigation hook
export const useKeyboardNavigation = (
  items: any[],
  onSelect: (item: any) => void
) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      switch (event.key) {
        case "ArrowDown":
          event.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % items.length);
          break;
        case "ArrowUp":
          event.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + items.length) % items.length);
          break;
        case "Enter":
        case " ":
          event.preventDefault();
          if (items[selectedIndex]) {
            onSelect(items[selectedIndex]);
          }
          break;
        case "Escape":
          event.preventDefault();
          // Close or reset selection
          break;
      }
    },
    [items, selectedIndex, onSelect]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return { selectedIndex, setSelectedIndex };
};
```

#### Screen Reader Support

```typescript
// Accessible component example
export const EntityTag: React.FC<EntityTagProps> = ({ entity, onClick }) => {
  const { entity_type, text, is_verified } = entity;

  return (
    <Box
      component="span"
      role="button"
      tabIndex={0}
      aria-label={`${entity_type.name} entity: ${text}${
        is_verified ? " (verified)" : ""
      }`}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
      sx={{
        backgroundColor: entity_type.color_code,
        color: getContrastColor(entity_type.color_code),
        padding: "2px 6px",
        borderRadius: "4px",
        fontSize: "0.875rem",
        cursor: "pointer",
        border: is_verified ? "2px solid #4caf50" : "1px solid transparent",
        "&:focus": {
          outline: "2px solid #1976d2",
          outlineOffset: "2px",
        },
      }}
    >
      {text}
    </Box>
  );
};
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy loading for routes
const Dashboard = lazy(() => import("./pages/Dashboard"));
const DocumentUpload = lazy(() => import("./pages/DocumentUpload"));
const DocumentViewer = lazy(() => import("./pages/DocumentViewer"));
const EntityEditor = lazy(() => import("./pages/EntityEditor"));
const Settings = lazy(() => import("./pages/Settings"));

// Suspense wrapper
function AppRoutes() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<DocumentUpload />} />
        <Route path="/view/:id" element={<DocumentViewer />} />
        <Route path="/edit/:id" element={<EntityEditor />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### Virtual Scrolling

```typescript
// Virtual scrolling for large text documents
export const VirtualTextViewer: React.FC<VirtualTextViewerProps> = ({
  document,
  entities,
  onEntityClick,
}) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 100 });
  const containerRef = useRef<HTMLDivElement>(null);

  const lines = useMemo(() => {
    return document.content.split("\n");
  }, [document.content]);

  const visibleLines = useMemo(() => {
    return lines.slice(visibleRange.start, visibleRange.end);
  }, [lines, visibleRange]);

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const scrollTop = container.scrollTop;
    const clientHeight = container.clientHeight;
    const lineHeight = 24; // Approximate line height

    const start = Math.floor(scrollTop / lineHeight);
    const end = Math.ceil((scrollTop + clientHeight) / lineHeight) + 10; // Buffer

    setVisibleRange({
      start: Math.max(0, start),
      end: Math.min(lines.length, end),
    });
  }, [lines.length]);

  return (
    <Box
      ref={containerRef}
      onScroll={handleScroll}
      sx={{
        height: "100%",
        overflow: "auto",
        position: "relative",
      }}
    >
      <Box sx={{ height: lines.length * 24 }}>
        {" "}
        {/* Total height */}
        <Box sx={{ position: "absolute", top: visibleRange.start * 24 }}>
          {visibleLines.map((line, index) => (
            <TextLine
              key={visibleRange.start + index}
              line={line}
              lineNumber={visibleRange.start + index + 1}
              entities={entities.filter(
                (e) => e.line_number === visibleRange.start + index + 1
              )}
              onEntityClick={onEntityClick}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
};
```

### Memoization

```typescript
// Memoized components and calculations
export const EntityList = memo<EntityListProps>(
  ({ entities, onEntitySelect }) => {
    const sortedEntities = useMemo(() => {
      return [...entities].sort((a, b) => {
        if (a.document.id !== b.document.id) {
          return a.document.id - b.document.id;
        }
        return a.start_position - b.start_position;
      });
    }, [entities]);

    const groupedEntities = useMemo(() => {
      return sortedEntities.reduce((groups, entity) => {
        const key = `${entity.document.id}-${entity.entity_type.id}`;
        if (!groups[key]) {
          groups[key] = [];
        }
        groups[key].push(entity);
        return groups;
      }, {} as Record<string, Entity[]>);
    }, [sortedEntities]);

    return (
      <Box>
        {Object.entries(groupedEntities).map(([key, entityGroup]) => (
          <EntityGroup
            key={key}
            entities={entityGroup}
            onEntitySelect={onEntitySelect}
          />
        ))}
      </Box>
    );
  }
);

EntityList.displayName = "EntityList";
```

### Bundle Optimization

```typescript
// Vite configuration for optimization
export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2015",
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          mui: ["@mui/material", "@mui/icons-material"],
          redux: ["@reduxjs/toolkit", "react-redux"],
          utils: ["lodash", "date-fns"],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ["react", "react-dom", "@mui/material"],
  },
});
```

## Internationalization

### i18n Configuration

```typescript
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

i18n.use(initReactI18next).init({
  resources: {
    en: {
      translation: {
        common: {
          save: "Save",
          cancel: "Cancel",
          delete: "Delete",
          edit: "Edit",
          view: "View",
        },
        documents: {
          title: "Documents",
          upload: "Upload Document",
          processing: "Processing...",
          completed: "Completed",
          failed: "Failed",
        },
        entities: {
          title: "Entities",
          person: "Person",
          location: "Location",
          date: "Date",
          time: "Time",
          organization: "Organization",
          designation: "Designation",
          number: "Number",
        },
      },
    },
    ur: {
      translation: {
        common: {
          save: "محفوظ کریں",
          cancel: "منسوخ کریں",
          delete: "حذف کریں",
          edit: "ترمیم کریں",
          view: "دیکھیں",
        },
        documents: {
          title: "دستاویزات",
          upload: "دستاویز اپ لوڈ کریں",
          processing: "پروسیسنگ...",
          completed: "مکمل",
          failed: "ناکام",
        },
        entities: {
          title: "اشیاء",
          person: "شخص",
          location: "مقام",
          date: "تاریخ",
          time: "وقت",
          organization: "تنظیم",
          designation: "عہدہ",
          number: "نمبر",
        },
      },
    },
  },
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
```

### RTL Support

```typescript
// RTL support for Urdu
export const RTLWrapper: React.FC<{
  children: React.ReactNode;
  language: string;
}> = ({ children, language }) => {
  const isRTL = language === "ur";

  useEffect(() => {
    document.documentElement.dir = isRTL ? "rtl" : "ltr";
    document.documentElement.lang = language;
  }, [language, isRTL]);

  return (
    <ThemeProvider
      theme={createTheme({
        ...theme,
        direction: isRTL ? "rtl" : "ltr",
      })}
    >
      {children}
    </ThemeProvider>
  );
};

// Language switcher
export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (language: string) => {
    i18n.changeLanguage(language);
    localStorage.setItem("language", language);
  };

  return (
    <Box sx={{ display: "flex", gap: 1 }}>
      <Button
        variant={i18n.language === "en" ? "contained" : "outlined"}
        size="small"
        onClick={() => changeLanguage("en")}
      >
        English
      </Button>
      <Button
        variant={i18n.language === "ur" ? "contained" : "outlined"}
        size="small"
        onClick={() => changeLanguage("ur")}
      >
        اردو
      </Button>
    </Box>
  );
};
```

## Testing Strategy

### Testing Tools

- **Jest**: Unit testing framework
- **React Testing Library**: Component testing utilities
- **MSW**: API mocking for integration tests
- **Cypress**: End-to-end testing

### Test Structure

```typescript
// Component test example
describe("EntityTag", () => {
  const mockEntity = {
    id: 1,
    text: "حسین",
    entity_type: {
      id: 1,
      name: "PERSON",
      color_code: "#87CEEB",
    },
    is_verified: false,
  };

  it("renders entity text correctly", () => {
    render(<EntityTag entity={mockEntity} onClick={jest.fn()} />);
    expect(screen.getByText("حسین")).toBeInTheDocument();
  });

  it("applies correct styling based on entity type", () => {
    render(<EntityTag entity={mockEntity} onClick={jest.fn()} />);
    const tag = screen.getByRole("button");
    expect(tag).toHaveStyle({ backgroundColor: "#87CEEB" });
  });

  it("calls onClick when clicked", () => {
    const mockOnClick = jest.fn();
    render(<EntityTag entity={mockEntity} onClick={mockOnClick} />);

    fireEvent.click(screen.getByRole("button"));
    expect(mockOnClick).toHaveBeenCalledWith(mockEntity);
  });

  it("supports keyboard navigation", () => {
    const mockOnClick = jest.fn();
    render(<EntityTag entity={mockEntity} onClick={mockOnClick} />);

    const tag = screen.getByRole("button");
    tag.focus();

    fireEvent.keyDown(tag, { key: "Enter" });
    expect(mockOnClick).toHaveBeenCalledWith(mockEntity);
  });
});
```

### Integration Tests

```typescript
// API integration test
describe("Document API", () => {
  beforeEach(() => {
    server.listen();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  it("fetches documents successfully", async () => {
    server.use(
      rest.get("/api/documents/", (req, res, ctx) => {
        return res(
          ctx.json({
            count: 1,
            results: [
              {
                id: 1,
                title: "Test Document",
                content: "Test content",
                processing_status: "completed",
              },
            ],
          })
        );
      })
    );

    render(<Documents />);

    await waitFor(() => {
      expect(screen.getByText("Test Document")).toBeInTheDocument();
    });
  });
});
```

## Build and Deployment

### Build Configuration

```typescript
// Vite build configuration
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
```

### Environment Configuration

```typescript
// Environment variables
interface Environment {
  NODE_ENV: "development" | "production" | "test";
  VITE_API_BASE_URL: string;
  VITE_WS_BASE_URL: string;
  VITE_APP_NAME: string;
  VITE_APP_VERSION: string;
}

export const env: Environment = {
  NODE_ENV: import.meta.env.NODE_ENV,
  VITE_API_BASE_URL:
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  VITE_WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000",
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME || "Marsiya NER",
  VITE_APP_VERSION: import.meta.env.VITE_APP_VERSION || "1.0.0",
};
```

### Deployment Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "build:prod": "npm run type-check && npm run lint && npm run build"
  }
}
```

This comprehensive frontend architecture provides a solid foundation for building a modern, performant, and accessible web application for Urdu Marsiya NER processing.
