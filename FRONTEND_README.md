# Medical Insight Engine - Frontend

A modern, robust React-based frontend for medical document digitization and analysis.

## Project Structure

```
src/
├── index.js                 # Application entry point
├── App.jsx                  # Main application component with routing
├── components/              # Reusable React components
│   ├── Auth/               # Authentication components
│   │   ├── Login.jsx       # Login page
│   │   ├── Register.jsx    # Registration page
│   │   └── ProtectedRoute.jsx  # Route protection wrapper
│   ├── Common/             # Common UI components
│   │   ├── ErrorBoundary.jsx   # Error handling
│   │   ├── Loading.jsx     # Loading spinner
│   │   └── Toast.jsx       # Toast notifications
│   ├── Layout/             # Layout components
│   │   ├── Navbar.jsx      # Top navigation bar
│   │   ├── Sidebar.jsx     # Side navigation menu
│   │   └── Footer.jsx      # Footer component
│   ├── Dashboard/          # Dashboard components
│   │   ├── Dashboard.jsx   # Main dashboard page
│   │   ├── StatsCard.jsx   # Statistics card component
│   │   └── RecentReports.jsx   # Recent reports widget
│   ├── Reports/            # Reports management
│   │   ├── ReportsList.jsx # Reports list view
│   │   ├── ReportDetail.jsx # Individual report detail
│   │   └── ReportSearch.jsx # Search and filter component
│   ├── Upload/             # Document upload
│   │   ├── DocumentUpload.jsx  # Upload interface
│   │   └── UploadProgress.jsx  # Progress indicator
│   └── Analytics/          # Analytics components
│       ├── Charts.jsx      # Chart visualizations
│       ├── InsightsDashboard.jsx # Key insights
│       └── TrendAnalysis.jsx # Trend analysis
├── context/                # React context providers
│   ├── AuthContext.jsx     # Authentication state management
│   └── ThemeContext.jsx    # Theme state management
├── hooks/                  # Custom React hooks
│   ├── useAuth.js          # Auth hook
│   └── useDebounce.js      # Debounce hook
├── services/               # API services
│   ├── api.js              # Axios instance with interceptors
│   ├── auth.js             # Authentication API
│   ├── reports.js          # Reports API
│   └── analytics.js        # Analytics API
├── utils/                  # Utility functions
│   ├── formatters.js       # Data formatting utilities
│   ├── validation.js       # Form validation utilities
├── styles/                 # Global styles
│   └── global.css          # Tailwind + custom CSS
└── public/                 # Static assets
    └── index.html          # HTML entry point

```

## Key Features

### Authentication
- Login and registration pages
- JWT token-based authentication
- Protected routes
- Automatic token refresh
- Secure logout

### Document Management
- Upload multiple documents
- Drag-and-drop interface
- File validation
- Progress tracking
- Document preview

### Reporting
- Report list with pagination
- Advanced search and filtering
- Detailed report view
- Report export functionality

### Analytics
- Dashboard with key metrics
- Trend analysis
- Chart visualizations
- Custom insights

### UI/UX
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Toast notifications
- Error boundaries
- Loading states

## Technologies Used

### Core
- **React 18** - UI library
- **React Router v6** - Client-side routing
- **Vite** - Build tool and dev server

### State Management & Forms
- **Zustand** - Lightweight state management
- **React Context** - Built-in context API
- **React Hook Form** - Form state management
- **React Query** - Server state management

### Styling
- **Tailwind CSS** - Utility-first CSS
- **PostCSS** - CSS processing
- **Autoprefixer** - Vendor prefixing

### Data & Visualization
- **Recharts** - React charting library
- **Axios** - HTTP client
- **date-fns** - Date manipulation

### UI Components & Icons
- **Lucide React** - Icon library
- **React Hot Toast** - Toast notifications
- **Framer Motion** - Animations (optional)

### Development
- **ESLint** - Code linting
- **Prettier** - Code formatting

## Installation

### Prerequisites
- Node.js 16+ (recommend 18+)
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Configure environment variables:
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Medical Insight Engine
```

## Running the Application

### Development Server
```bash
npm run dev
```
Starts the dev server at `http://localhost:3000`

### Build for Production
```bash
npm run build
```
Outputs production build to `dist/` directory

### Preview Production Build
```bash
npm run preview
```
Preview the production build locally

### Linting
```bash
npm run lint
```

## Code Quality Standards

### Error Handling
- Try-catch blocks in async operations
- Error boundaries for React errors
- User-friendly error messages
- Console error logging

### Form Validation
- Email format validation
- Password strength requirements
- File type and size validation
- Required field validation
- Real-time validation feedback

### Security
- CSRF protection ready
- Input sanitization
- XSS prevention with React's built-in protection
- Secure token storage in localStorage
- HTTPS-ready configuration

### Performance
- Code splitting
- Lazy loading components (ready for implementation)
- Debounced search input
- Optimized re-renders
- Asset optimization in build

### Accessibility
- Semantic HTML
- ARIA labels (can be enhanced)
- Keyboard navigation support
- Screen reader friendly
- Color contrast compliance

## API Integration

### Base Configuration
- Base URL: Environment variable `VITE_API_URL`
- Timeout: 30 seconds
- Auto-retry on 401 (unauthorized)

### Request Interceptor
- Automatically adds Bearer token to headers
- Reads token from localStorage

### Response Interceptor
- Handles 401 errors by redirecting to login
- Clears auth state on token expiration

## Authentication Flow

1. User enters credentials on login page
2. Submit to `/api/auth/login`
3. Receive `access_token` and `user` object
4. Store in localStorage
5. Token added to all subsequent requests
6. On expiration (401), redirect to login
7. Logout clears localStorage

## State Management

### AuthContext
- `user` - Current user object
- `isAuthenticated` - Auth status
- `loading` - Loading state
- `error` - Error message
- Methods: `login()`, `register()`, `logout()`

### ThemeContext
- `theme` - Current theme (light/dark)
- `isDark` / `isLight` - Theme flags
- Methods: `toggleTheme()`, `setTheme()`

## Validation Examples

```javascript
// Email validation
validateEmail('user@example.com') // true
validateEmail('invalid') // false

// Password validation
validatePassword('Weak')
// { valid: false, errors: ['Password must be at least 8 characters...'] }

validatePassword('Strong@123')
// { valid: true, errors: [] }

// File validation
validateFile(file, { maxSize: 10*1024*1024, allowedTypes: ['application/pdf'] })
```

## Formatting Utilities

```javascript
// Date formatting
formatDate('2024-01-15')           // "1/15/2024"
formatDateTime('2024-01-15T10:00') // "1/15/2024, 10:00:00 AM"

// Number formatting
formatBytes(1024)                  // "1 KB"
formatNumber(1000)                // "1,000"
formatPercentage(0.75)             // "75%"
formatCurrency(99.99, 'USD')       // "$99.99"

// Text formatting
truncateText('Long text...', 10)   // "Long text..."
capitalizeFirst('hello')           // "Hello"
```

## Component Patterns

### Service Layer Pattern
```javascript
// services/example.js
export const exampleService = {
  async fetchData() {
    try {
      const response = await api.get('/endpoint');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },
  handleError(error) {
    // Centralized error handling
  }
};
```

### Custom Hook Pattern
```javascript
// hooks/useCustom.js
export const useCustom = () => {
  const context = useContext(CustomContext);
  if (!context) {
    throw new Error('useCustom must be used within Provider');
  }
  return context;
};
```

### Protected Route Pattern
```javascript
<Route
  path="/protected"
  element={
    <ProtectedRoute>
      <ProtectedComponent />
    </ProtectedRoute>
  }
/>
```

## Environment Variables

```env
# API
VITE_API_URL=http://localhost:8000/api

# App Info
VITE_APP_NAME=Medical Insight Engine
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_OFFLINE_MODE=false

# Storage Keys
VITE_TOKEN_STORAGE_KEY=access_token
VITE_USER_STORAGE_KEY=user

# Debug
VITE_LOG_LEVEL=info
VITE_DEBUG=false
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check API server is running
   - Verify `VITE_API_URL` is correct
   - Ensure backend CORS is configured

2. **Auth Token Expires**
   - Check token refresh endpoint
   - Verify localStorage is accessible
   - Check API interceptors

3. **Build Errors**
   - Clear `node_modules` and reinstall
   - Check for syntax errors
   - Verify all imports are correct

4. **Styling Issues**
   - Ensure Tailwind CSS is processing
   - Check PostCSS config
   - Verify CSS imports in index.js

## Contributing

1. Follow the project structure
2. Use consistent naming conventions
3. Add proper error handling
4. Include JSDoc comments for functions
5. Test components thoroughly
6. Follow security best practices

## License

Medical Insight Engine © 2024. All rights reserved.

## Support

For issues, questions, or contributions, please contact the development team.
