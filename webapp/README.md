# Frontend Documentation

## Quick Start

```bash
cd webapp

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

## Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject from Create React App
npm run eject
```

## Project Structure

```
webapp/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx    # Main dashboard component
│   │   ├── Dashboard.css    # Dashboard styles
│   │   └── index.ts         # Page exports
│   ├── services/
│   │   └── api.ts           # API service layer
│   ├── App.tsx              # Main app component
│   ├── index.tsx            # Entry point
│   └── index.css            # Global styles
├── package.json
└── tsconfig.json
```

## Components

### Dashboard

The main dashboard component featuring:

- **Stats Overview**: Total events, attacks, unique IPs, active alerts
- **Monitoring Controls**: Start/stop real-time monitoring, set thresholds
- **Charts**: Attack activity over time, top attacking countries
- **Navigation Tabs**:
  - Dashboard: Overview and charts
  - Events: Security events log
  - Alerts: Active alerts management
  - Intelligence: Attacker details

## API Integration

The frontend uses the `api` service from `services/api.ts`:

```typescript
import api, { Stats, Alert, Intelligence } from './services/api';

// Get dashboard stats
const stats = await api.getStats();

// Get alerts
const alerts = await api.getAlerts({ active_only: true });

// Start monitoring
await api.startMonitoring(3);

// Stop monitoring
await api.stopMonitoring();
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| REACT_APP_API_URL | Backend API URL | http://localhost:8000 |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^19.2.4 | UI framework |
| react-dom | ^19.2.4 | React DOM renderer |
| react-scripts | 5.0.1 | Build tooling |
| axios | ^1.13.4 | HTTP client |
| bootstrap | ^5.3.8 | UI components |
| recharts | ^2.12.0 | Charts |
| react-router-dom | ^6.22.0 | Routing |

## Styling

The dashboard uses a custom dark theme with:

- Professional SIEM-style dark colors
- Bootstrap for layout and components
- Recharts for data visualization
- Custom CSS for specialized elements

## Build for Production

```bash
npm run build
```

This creates a `build/` folder with optimized static files ready for deployment.

## Deployment

### Static Hosting

Upload the `build/` folder to any static hosting service:

- Vercel
- Netlify
- AWS S3
- GitHub Pages

### Docker

```dockerfile
# Build stage
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

