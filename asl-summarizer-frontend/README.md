# ASL Article Summarizer - Frontend

A React.js frontend application for an article summarizer that converts content to ASL interpretation. This application features user authentication, file management, content summarization, real-time translation, and a community sharing platform.

## 🚀 Features

### ✅ Implemented (Phase 1)
- **Authentication System**: Login/logout with JWT token management
- **Responsive Design**: Mobile-first approach with modern UI/UX
- **Navigation**: Clean routing between all main sections
- **State Management**: Context API for user data and application state
- **Error Handling**: Comprehensive error boundaries and loading states
- **Mock Data**: Development-ready with sample data structures

### 🔄 In Development (Phase 2)
- **Sources Management**: Folder tree view with drag-and-drop file uploads
- **Content Summarization**: AI-powered summary generation from multiple sources
- **ASL Translation**: Real-time video playback of ASL interpretations
- **Community Platform**: Instagram-like feed for sharing ASL summary videos

## 🛠️ Technology Stack

- **Frontend Framework**: React.js 18+ with modern JavaScript (ES6+)
- **Styling**: CSS3 with CSS Modules and CSS Variables
- **Routing**: React Router v6
- **State Management**: React Context API + useReducer
- **Build Tool**: Vite (fast development and building)
- **HTTP Client**: Axios (ready for API integration)
- **File Upload**: React Dropzone (planned)

## 📁 Project Structure

```
asl-summarizer-frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── common/           # Reusable UI components
│   │   │   ├── Button/
│   │   │   ├── LoadingSpinner/
│   │   │   └── ErrorBoundary/
│   │   └── auth/             # Authentication components
│   │       └── ProtectedRoute/
│   ├── pages/                # Main application pages
│   │   ├── LoginPage/
│   │   ├── HomePage/
│   │   ├── SourcesPage/
│   │   ├── SummariesPage/
│   │   ├── TranslationPage/
│   │   └── CommunityPage/
│   ├── context/              # React Context providers
│   │   ├── AuthContext.jsx
│   │   └── DataContext.jsx
│   ├── services/             # API and data services
│   │   ├── authService.js
│   │   └── mockData.js
│   ├── styles/               # Global styles and variables
│   │   └── globals.css
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
└── README.md
```

## 🚦 Getting Started

### Prerequisites
- Node.js 16+ and npm (or yarn)
- Modern web browser

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd asl-summarizer-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Demo Credentials
- **Email**: `demo@example.com`
- **Password**: `password123`

Alternative:
- **Email**: `test@example.com`
- **Password**: `test123`

## 🎯 Application Flow

### Authentication
1. Users start at the login page
2. Enter credentials (or use demo credentials)
3. Upon successful login, redirected to home page
4. All other routes are protected and require authentication

### Main Navigation
From the home page, users can access:

1. **Sources** (`/sources`) - Upload and organize content
2. **Summaries** (`/summaries`) - Generate AI summaries
3. **Real-time Translation** (`/translation`) - Watch ASL videos
4. **Community** (`/community`) - Share and discover content

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (#667eea to #764ba2)
- **Secondary**: Neutral grays
- **Accent**: Green (#10b981)
- **Danger**: Red (#ef4444)

### Typography
- **Font Family**: System fonts (Apple/Segoe UI/Roboto)
- **Scale**: Responsive typography with CSS variables
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Components
- **Buttons**: Multiple variants (primary, secondary, success, danger, ghost)
- **Forms**: Consistent styling with validation states
- **Cards**: Elevated surfaces with hover effects
- **Loading States**: Animated spinners and skeleton screens

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Organization
- **Components**: Organized by feature with co-located styles
- **Hooks**: Custom hooks for reusable logic
- **Context**: Global state management
- **Services**: API calls and data transformation

### Styling Approach
- **CSS Variables**: Consistent theming and easy customization
- **Mobile-First**: Responsive design starting from mobile
- **Accessibility**: Focus states, ARIA labels, semantic HTML
- **Performance**: Optimized animations and transitions

## 🔮 Future Enhancements

### Phase 2 Features
1. **Advanced File Management**
   - Drag-and-drop file uploads
   - Folder tree with nested organization
   - File search and filtering
   - Bulk operations

2. **Smart Summarization**
   - AI-powered content analysis
   - Multi-source summary generation
   - Summary customization options
   - Export capabilities

3. **ASL Translation**
   - Custom video player
   - Playback speed controls
   - Subtitle options
   - Accessibility features

4. **Community Features**
   - Social feed with infinite scroll
   - Post creation and editing
   - Like and comment system
   - User profiles

### Technical Improvements
- Progressive Web App (PWA) capabilities
- Offline functionality with service workers
- Real-time notifications
- Advanced search and filtering
- Performance optimization
- Comprehensive testing suite

## 🤝 Contributing

This is a frontend-only implementation designed to work with a future backend API. The current version uses mock data and services that can be easily replaced with real API calls.

### Backend Integration Points
- Authentication endpoints (`/api/auth/*`)
- File management (`/api/files/*`, `/api/folders/*`)
- Summary generation (`/api/summaries/*`)
- Community features (`/api/community/*`)

## 📄 License

This project is part of a larger ASL accessibility initiative. Please refer to the main project documentation for licensing information.

## 🆘 Support

For questions or issues:
1. Check the browser console for error messages
2. Verify all dependencies are installed correctly
3. Ensure you're using a modern browser with JavaScript enabled
4. Try the demo credentials if login issues occur

---

**Note**: This is a frontend-only implementation with mock data. The application is designed to be easily integrated with a backend API when available.