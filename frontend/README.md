# Break-even Frontend

A modern React application for small business management, providing tools to create websites, manage customers, track analytics, and grow businesses.

## Features

- 🏪 **Business Website Builder** - Create custom websites with QR codes
- 👥 **Customer Management** - Track and communicate with customers
- 📊 **Analytics Dashboard** - Monitor business performance
- 💬 **Real-time Messaging** - Instant customer communication
- 🤖 **AI-Powered Tools** - Content generation and business insights
- 📱 **Mobile Responsive** - Works perfectly on all devices

## Tech Stack

- **React 18** - Modern React with hooks
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Hook Form** - Form handling
- **Recharts** - Data visualization
- **Socket.IO** - Real-time communication
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see backend README)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd break-even-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update environment variables in `.env`:
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WEBSITE_BASE_URL=http://localhost:3001
```

5. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`.

## Available Scripts

- `npm start` - Start development server
- `npm build` - Create production build
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App