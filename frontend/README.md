# Graph RAG Frontend

Modern React UI for the Multimodal Graph RAG system.

## Features

- 🎨 Clean, modern UI with Tailwind CSS
- 🔍 Advanced query interface with filters
- 📤 Drag-and-drop PDF upload
- 📊 Entity and company browsing
- 🚀 Real-time API integration
- 📱 Responsive design
- ⚡ Fast dev experience with Vite

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will start at http://localhost:3000

### 3. Make Sure Backend is Running

The frontend connects to the FastAPI backend at http://localhost:8000

Start the backend:
```bash
cd ..
python src/api/server.py
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   └── Layout.jsx   # Main layout with navigation
│   ├── pages/           # Page components
│   │   ├── Home.jsx     # Landing page
│   │   ├── Query.jsx    # Query interface
│   │   ├── Ingest.jsx   # Document upload
│   │   ├── Entities.jsx # Entity browser
│   │   ├── Company.jsx  # Company details
│   │   └── About.jsx    # System information
│   ├── services/        # API services
│   │   └── api.js       # API client
│   ├── styles/          # Global styles
│   │   └── index.css    # Tailwind + custom styles
│   ├── App.jsx          # Root component
│   └── main.jsx         # Entry point
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── tailwind.config.js   # Tailwind configuration
```

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Features Overview

### Home Page
- System overview and quick actions
- Feature highlights
- Getting started guide

### Query Page
- Natural language query input
- Advanced filters (ticker, year, section)
- Search strategy selection
- Result display with citations
- Context preview

### Ingest Page
- PDF file upload
- Metadata input (ticker, year, date)
- Processing progress
- Ingestion statistics

### Entities Page
- Browse extracted entities
- Filter by entity type
- View entity properties
- Navigate to company pages

### Company Page
- Company overview
- Financial metrics
- Executive team
- Subsidiaries

### About Page
- Architecture overview
- Technology stack
- Pipeline flow
- Performance stats

## API Integration

The frontend communicates with the FastAPI backend through `/api` proxy:

```javascript
// Example API call
import { querySystem } from './services/api';

const response = await querySystem({
  query: "What was Apple's revenue?",
  top_k: 10,
  filters: { fiscal_year: 2024 }
});
```

## Customization

### Colors
Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### API Base URL
Edit `src/services/api.js` if backend runs on different port:

```javascript
const API_BASE_URL = '/api'; // or 'http://localhost:8000'
```

## Development Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **API Proxy**: Vite proxies `/api` to `http://localhost:8000`
3. **Error Handling**: Check browser console for errors
4. **Backend Connection**: Green indicator in header shows connection status

## Build for Production

```bash
# Build optimized bundle
npm run build

# Output in dist/ folder
ls dist/

# Preview production build
npm run preview
```

## Deployment

### Option 1: Serve with Python

```bash
cd dist
python -m http.server 3000
```

### Option 2: Serve with Backend

Configure FastAPI to serve static files:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True))
```

### Option 3: Deploy to Vercel/Netlify

1. Push to GitHub
2. Connect to Vercel/Netlify
3. Set build command: `cd frontend && npm run build`
4. Set output directory: `frontend/dist`
5. Add environment variable for API URL

## Troubleshooting

### Backend Connection Error
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API proxy in `vite.config.js`

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Styling Issues
```bash
# Rebuild Tailwind
npm run dev
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

## License

Part of the Multimodal Graph RAG project.
