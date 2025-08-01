
#### README.md (Backend)
markdown
# Break-even Backend

Flask-based REST API for the Break-even small business management platform.

## Features

- 🔐 **JWT Authentication** - Secure user authentication
- 📊 **Analytics API** - Business performance tracking
- 💬 **Real-time Messaging** - WebSocket-based communication
- 🤖 **AI Integration** - OpenAI-powered business tools
- 📧 **Email Automation** - Customer communication
- 🗄 **MongoDB Integration** - Scalable data storage

## Tech Stack

- **Flask** - Python web framework
- **MongoDB** - NoSQL database
- **Flask-SocketIO** - Real-time communication
- **JWT** - Authentication
- **OpenAI API** - AI features
- **Flask-Mail** - Email services

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- Redis (optional, for caching)

### Installation

1. Clone the repository:
bash
git clone <repository-url>
cd break-even-backend


2. Create virtual environment:
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install dependencies:
bash
pip install -r requirements.txt


4. Create environment file:
bash
cp .env.example .env


5. Update environment variables in `.env`

6. Initialize database:
bash
python -c "from app.utils.database import init_database, create_sample_data; init_database(); create_sample_data()"


7. Start the server:
bash
python run.py


The API will be available at `http://localhost:5000`.

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify JWT token

### Dashboard
- `GET /api/dashboard` - Dashboard data
- `GET /api/dashboard/stats` - Current stats

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Messages
- `GET /api/messages` - List messages
- `POST /api/messages` - Create message (from child websites)
- `POST /api/messages/<id>/reply` - Reply to message

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers/register` - Register customer (from child websites)
- `POST /api/customers/send-bulk-email` - Send bulk email

### Website Builder
- `POST /api/website-builder/create` - Create website
- `PUT /api/website-builder/update` - Update website
- `GET /api/website-builder/my-website` - Get user's website

### AI Tools
- `POST /api/ai-tools/generate-content` - Generate content
- `POST /api/ai-tools/generate-image` - Generate images
- `POST /api/ai-tools/business-suggestions` - Get suggestions

## WebSocket Events

### Client to Server
- `join_room` - Join user's notification room
- `leave_room` - Leave user's room

### Server to Client
- `new_message` - New customer message
- `new_customer` - New customer registration
- `qr_scan` - QR code scanned
- `new_feedback` - New customer feedback

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/breakeven` |
| `JWT_SECRET_KEY` | JWT secret key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `MAIL_USERNAME` | Email username | Required for email features |
| `MAIL_PASSWORD` | Email password | Required for email features |

## Deployment

### Using Gunicorn

bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 run:app


### Using Docker

dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]


## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

This project is licensed under the MIT License.


#### docker-compose.yml (Optional)
yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MONGO_URI=mongodb://mongo:27017/breakeven
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis
    restart: unless-stopped

  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  frontend:
    image: node:18-alpine
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ../break-even-frontend:/app
    command: sh -c "npm install && npm start"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    restart: unless-stopped

volumes:
  mongo_data:
