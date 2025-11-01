# Copilot Instructions for Hack-Coms

## Project Overview
This is a React.js frontend for an ASL Article Summarizer. It enables users to upload media (news article links or YouTube videos), extract and validate transcripts, and generate AI-powered summaries. The app is structured for easy backend integration and currently uses mock data/services.

## Architecture & Data Flow
- **Pages**: Main features are split into pages under `src/pages/`:
  - `SourcesPage`: Upload and validate media sources (articles, videos)
  - `SummariesPage`: Display AI-generated summaries
  - `TranslationPage`: ASL video playback for summaries
  - `CommunityPage`: Social feed for sharing ASL summaries
- **Components**: Reusable UI in `src/components/common/` (Button, ErrorBoundary, LoadingSpinner)
- **Context**: Global state via `src/context/AuthContext.jsx` and `DataContext.jsx`
- **Services**: API/data logic in `src/services/` (currently mock, ready for backend)

## Key Workflows
- **Media Upload & Validation**:
  - Users upload links/files in `SourcesPage`
  - Scraping and transcript validation (pornography, profanity, hate-speech, discrimination, racism, political bias) should be handled via backend/LLM APIs
  - Only accepted transcripts are summarized
- **Summary Generation**:
  - Summaries are generated using LLM APIs (mocked for now)
  - Displayed in `SummariesPage`
- **ASL Translation**:
  - Summaries are converted to ASL videos in `TranslationPage`
- **Community Sharing**:
  - Users share/view ASL summaries in `CommunityPage`

## Developer Conventions
- **Routing**: Use React Router v6 for navigation
- **State**: Use Context API for auth/data; avoid prop drilling
- **Styling**: Use CSS Modules and variables; mobile-first design
- **Error Handling**: Use `ErrorBoundary` and `LoadingSpinner` for robust UX
- **Mock Data**: Replace `src/services/mockData.js` with real API calls when backend is ready

## Build & Run
- Install: `npm install` in `asl-summarizer-frontend/`
- Dev server: `npm run dev` (Vite)
- Lint: `npm run lint`
- Production build: `npm run build`

## Integration Points
- Backend endpoints (to be implemented):
  - `/api/auth/*` for authentication
  - `/api/files/*`, `/api/folders/*` for media management
  - `/api/summaries/*` for summary generation
  - `/api/community/*` for social features

## Example Patterns
- **Protected Routes**: See `src/components/auth/ProtectedRoute/ProtectedRoute.jsx`
- **Global State**: See `src/context/AuthContext.jsx` and `DataContext.jsx`
- **Error Boundaries**: See `src/components/common/ErrorBoundary/ErrorBoundary.jsx`

## Special Notes
- All uploads and transcript validation must occur in `SourcesPage`.
- Summaries are only generated for accepted transcripts and shown in `SummariesPage`.
- Use mock data until backend is available.

---

If any section is unclear or missing, please provide feedback for improvement.