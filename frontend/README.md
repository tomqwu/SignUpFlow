# Roster Scheduler - Web GUI

A clean, modern single-page web application for managing roster schedules through the Roster API.

## 🚀 Quick Start

### Prerequisites

- Roster API running on `http://localhost:8000`
- Python 3 (for serving the frontend)

### Start the GUI

```bash
cd frontend
python3 -m http.server 8080
```

Then open your browser to: **http://localhost:8080**

## ✨ Features

### 📋 Organization Management
- Create and view organizations/leagues
- Manage organization settings and regions

### 👥 People Management
- Add players, volunteers, or team members
- Assign roles and contact information
- Filter by organization

### 🏆 Team Management
- Create teams with members
- View team composition
- Track team metadata

### 📅 Event Management
- Schedule matches, shifts, or meetings
- Set start/end times
- Link events to teams

### 🎯 Schedule Solver
- Generate optimized schedules
- View solution metrics in real-time:
  - Assignment count
  - Hard constraint violations
  - Health score (0-100)
  - Solve time
- Instant feedback on solution quality

### 💾 Solutions
- View all generated solutions
- Export solutions in multiple formats:
  - **CSV** - Spreadsheet-friendly
  - **JSON** - Complete data
  - **ICS** - Calendar import
- Track solution history

## 🎨 Design

- **Modern UI** - Clean, professional interface
- **Responsive** - Works on desktop, tablet, and mobile
- **Real-time** - Instant API status monitoring
- **Intuitive** - Tab-based navigation
- **Fast** - Vanilla JavaScript (no framework bloat)

## 🔧 Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid/Flexbox
- **Vanilla JavaScript** - No frameworks required
- **Fetch API** - RESTful communication
- **Python HTTP Server** - Simple static file serving

## 📖 Usage Guide

### 1. Check API Status

The header shows real-time API connection status:
- 🟢 **● API Online** - Ready to use
- 🔴 **● API Offline** - Check backend connection

### 2. Create an Organization

1. Click the **Organizations** tab
2. Click **+ New Organization**
3. Fill in organization details
4. Click **Create**

### 3. Add People

1. Click the **People** tab
2. Click **+ New Person**
3. Select organization
4. Enter person details and roles
5. Click **Create**

### 4. Create Events

1. Click the **Events** tab
2. Click **+ New Event**
3. Select organization and set details
4. Choose start/end times
5. Click **Create**

### 5. Generate Schedule

1. Click the **Solve** tab
2. Select organization
3. Set date range
4. Choose mode (strict/relaxed)
5. Click **🚀 Generate Schedule**
6. View metrics and results

### 6. Export Solutions

1. Click the **Solutions** tab
2. Find your solution
3. Click **Export CSV**, **Export JSON**, or **Export ICS**
4. File downloads automatically

## 🌐 API Integration

The GUI communicates with the Roster API at `http://localhost:8000`:

```javascript
// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Example API calls
fetch(`${API_BASE_URL}/organizations/`)
fetch(`${API_BASE_URL}/solver/solve`, { method: 'POST', ... })
fetch(`${API_BASE_URL}/solutions/${id}/export`)
```

To change the API URL, edit `js/app.js` line 2.

## 📱 Screenshots

### Dashboard View
Clean interface with tab-based navigation for all features.

### Solver Results
Real-time metrics showing assignment count, violations, and health score.

### Data Management
Easy CRUD operations for organizations, people, teams, and events.

## 🔒 Security Note

This is a development frontend with no authentication. For production:

1. Add user authentication (JWT/OAuth)
2. Implement HTTPS
3. Add CSRF protection
4. Validate all inputs
5. Rate limit API calls

## 🛠️ Development

### File Structure

```
frontend/
├── index.html          # Main HTML page
├── css/
│   └── styles.css      # All styles
├── js/
│   └── app.js          # Application logic
└── README.md           # This file
```

### Customization

**Colors**: Edit CSS variables in `css/styles.css`:
```css
:root {
    --primary: #3b82f6;
    --success: #10b981;
    --danger: #ef4444;
    ...
}
```

**API URL**: Edit `js/app.js`:
```javascript
const API_BASE_URL = 'http://your-api-url';
```

## 🚀 Production Deployment

### Option 1: Nginx

```nginx
server {
    listen 80;
    server_name roster.example.com;
    root /path/to/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
    }
}
```

### Option 2: Docker

```dockerfile
FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
EXPOSE 80
```

### Option 3: Static Hosting

Deploy to:
- **Vercel** - `vercel frontend/`
- **Netlify** - Drag & drop `frontend/` folder
- **GitHub Pages** - Push to `gh-pages` branch
- **AWS S3** - Static website hosting

## 📄 License

MIT License
