#  Geocipher Backend

A feature-rich backend API for a Geoguessr-inspired game where players guess locations based on coordinates and earn scores based on accuracy.

## What It Does

This is a Django REST API backend that powers a location-guessing game. Players receive random coordinates, make their guesses, and receive scores based on how close their guess is to the actual location. The system includes user authentication, game session management, score tracking, and a leveling/XP progression system.

## Key Features

- **Authentication**: JWT-based authentication with Google OAuth2 integration and traditional email/password signup
- **Game Sessions**: Create and manage game rounds with coordinate distribution
- **Scoring System**: Exponential scoring algorithm that heavily rewards accurate guesses
- **User Profiles**: Track player statistics including average scores, maximum scores, and minimum distances
- **Leveling System**: Dynamic XP and level progression based on total score
- **Score Persistence**: Store and retrieve game history for authenticated users
- **WebSocket Support**: Real-time capabilities via Django Channels and Redis
- **Environment-Aware**: Separate configurations for development and production deployments

## Tech Stack

- **Framework**: Django 5.2.7 with Django REST Framework
- **Authentication**: Django AllAuth, Simple JWT
- **Real-time**: Django Channels with Redis
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Cache**: Redis
- **Authentication Provider**: Google OAuth2
- **Server**: Daphne (ASGI) for async support
- **CORS**: django-cors-headers for cross-origin requests

## Getting Started

### Prerequisites

- Python 3.14.0 (I personally made in this)
- pip
- Redis (for caching and channels)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/kabir-afk/Geocipher-backend.git
   cd Geocipher-backend
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the `backend/` directory:

   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   ENVIRONMENT=development
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Google OAuth
   CLIENT_ID=your-google-client-id
   CLIENT_SECRET=your-google-client-secret

   # Database (development uses SQLite by default)
   DATABASE_URL=your-postgres-url  # For production

   # Redis (optional for development, uses localhost:6379 by default)
   REDIS_URL=redis://...
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Start the development server**

   ```bash
   python manage.py runserver
   # Or with Daphne for WebSocket support
   daphne backend.asgi:application
   ```

7. **Start the redis server**
   ```bash
   redis-server
   ```

Upon hitting `http://localhost:8000` you'll see blank page with `Home Page` as heading.The API will be available at `http://localhost:8000/api/v1/`

## API Endpoints

### Game Endpoints

- `GET /api/v1/` - Get 5 random coordinates for a round
- `POST /api/v1/game-id` - Create a new game session
- `POST /api/v1/score` - Submit a guess and calculate score
- `GET /api/v1/score` - Get all scores

### Authentication Endpoints

- `POST /api/v1/auth/` - Register new user
- `POST /api/v1/auth/google` - Google OAuth login
- `POST /api/token/` - Obtain JWT access token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/v1/logout/` - Logout and clear refresh token

### User Endpoints

- `GET /api/v1/protected-view/` - Get authenticated user's profile and statistics

## Development

### Running Tests

```bash
cd backend
python manage.py test api
```

### Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Revert to specific migration
python manage.py migrate api 0001_initial
```

### Creating a Superuser

```bash
python manage.py createsuperuser
```

Access the admin panel at `http://localhost:8000/admin`

## Project Structure

```
backend/
├── backend/              # Django project configuration
│   ├── settings.py      # Project settings
│   ├── urls.py          # URL routing
│   ├── asgi.py          # ASGI configuration for async
│   ├── wsgi.py          # WSGI configuration
│   └── views.py         # Authentication views
├── api/                 # Main app
│   ├── models.py        # Database models (Coordinates, Game, Score)
│   ├── views.py         # API endpoints
│   ├── serializers.py   # DRF serializers
│   ├── urls.py          # App URL routing
│   ├── utils.py         # Utility functions (scoring, XP calculations)
│   ├── middleware.py    # Custom middleware
│   ├── consumer.py      # WebSocket consumer
│   └── migrations/      # Database migrations
├── manage.py            # Django CLI
└── requirements.txt     # Python dependencies
```

## Scoring Algorithm

The scoring system uses an exponential decay function:

```
score = max_score * e^(-decay_rate * distance)
```

Where:

- `max_score` = 5000 (maximum points for perfect guess)
- `decay_rate` = 0.0005 (controls how quickly points decrease with distance)
- `distance` = calculated distance in kilometers using the Haversine formula

This heavily rewards accurate guesses while still providing points for less accurate ones.

## XP and Leveling

The leveling system uses a linear progression:

```
xp_required_per_level = base * level
```

Where `base = 150`. Players advance to the next level after accumulating enough total score.

## Environment Variables

| Variable        | Description                         | Example                           |
| --------------- | ----------------------------------- | --------------------------------- |
| `SECRET_KEY`    | Django secret key                   | `your-secret-key-here`            |
| `ENVIRONMENT`   | Deployment environment              | `development` or `production`     |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts       | `localhost,127.0.0.1,example.com` |
| `CLIENT_ID`     | Google OAuth client ID              | (from Google Cloud Console)       |
| `CLIENT_SECRET` | Google OAuth secret                 | (from Google Cloud Console)       |
| `DATABASE_URL`  | PostgreSQL connection string (prod) | `postgres://user:pass@host/db`    |
| `REDIS_URL`     | Redis connection URL                | `redis://localhost:6379`          |

## Deployment

- **Backend Service**: Render
- **Database**: Supabase PostgresSQl. Supabase connection string is IPv6 by default and render services are IPv4. Switch to IPv4 session pooler since its free , or go for a IPv4 add-on(it's paid).
- **Redis**: Render Redis Service

## Support & Documentation

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Django Channels**: https://channels.readthedocs.io/

---

**Built with ❤️**
