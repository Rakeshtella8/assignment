# Fintech Document Processing CMS

A production-grade Content Management System (CMS) specifically designed for financial document processing and management. Built with enterprise-grade security and scalability features to handle sensitive financial data processing needs of organizations like Ocrolus.

## Key Differentiators

- **Financial Document Intelligence**
  - Structured metadata extraction from financial documents
  - Support for multiple financial document types (bank statements, invoices, tax forms)
  - Document version control with audit trails
  - Automated document classification

- **Enterprise-Grade Security**
  - Role-Based Access Control (RBAC) with granular permissions
  - Document-level access controls
  - Audit logging of all system actions
  - Data encryption at rest and in transit
  - IP-based access restrictions
  - Session management with automatic timeouts

- **High Performance & Scalability**
  - Optimized database queries for large financial datasets
  - Caching layer for frequently accessed documents
  - Efficient connection pooling
  - Rate limiting and request throttling
  - Horizontal scaling support

- **Compliance & Audit Features**
  - Detailed audit trails for document access and modifications
  - GDPR and CCPA compliance support
  - Data retention policy enforcement
  - Export capabilities for audit purposes

## Technical Features

- **Core Functionality**
  - RESTful APIs for financial document CRUD operations
  - Smart document search with metadata filtering
  - Concurrent user operation handling
  - Recently viewed documents with thread-safe implementation
  - Batch operation support for bulk document processing

- **Performance Optimizations**
  - Efficient pagination with offset-based implementation
  - Optimized database indexing for financial queries
  - Connection pooling for database efficiency
  - Response compression

- **Developer Experience**
  - Comprehensive API documentation with Swagger
  - Development environment in Docker
  - Automated testing with high coverage
  - CI/CD pipeline configuration
  - Performance monitoring setup

## Tech Stack

- **Backend Framework**: Python with Flask
- **Database**: MySQL 8.0 with InnoDB engine
- **Caching**: Redis for performance optimization
- **ORM**: SQLAlchemy
- **Authentication**: JWT with refresh token rotation
- **Documentation**: Swagger UI
- **Containerization**: Docker with multi-stage builds
- **Testing**: pytest with unittest

## Architecture

```
├── app/
│   ├── api/
│   │   ├── routes/             # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── documents.py   # Document management
│   │   │   ├── users.py       # User management
│   │   │   └── audit.py       # Audit trail endpoints
│   │   └── middleware.py      # Request middleware
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # Security utilities
│   │   └── logging.py         # Logging configuration
│   ├── database/
│   │   ├── base.py            # Database setup
│   │   ├── session.py         # Session management
│   │   └── migrations/        # Database migrations
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Data validation schemas
│   ├── services/              # Business logic
│   │   ├── document.py        # Document processing
│   │   └── audit.py          # Audit logging
│   └── utils/                 # Utility functions
├── tests/
│   ├── integration/           # Integration tests
│   ├── unit/                  # Unit tests
│   └── performance/           # Performance tests
└── docker/
    ├── Dockerfile            # Multi-stage build
    ├── docker-compose.yml    # Service orchestration
    └── nginx/                # Reverse proxy config
```

## Performance Benchmarks

- Document upload: 100 concurrent users, < 500ms response time
- Search operations: < 200ms for complex queries
- API response time: 95th percentile < 300ms
- Support for millions of documents with efficient querying

## Security Measures

- **Authentication & Authorization**
  - JWT with short expiration and refresh token rotation
  - Password hashing with bcrypt
  - Rate limiting on auth endpoints
  - Session management with Redis
  - IP-based access control

- **Data Protection**
  - AES-256 encryption for sensitive data
  - TLS 1.3 for data in transit
  - Secure headers configuration
  - CORS with strict origin policy
  - SQL injection prevention through parameterized queries

## Monitoring & Observability

- Prometheus metrics integration
- Grafana dashboards for visualization
- ELK stack for log aggregation
- Health check endpoints
- Performance monitoring

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- MySQL 8.0+
- Make (optional, for using Makefile commands)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fintech-cms
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the API documentation:
   - Swagger UI: http://localhost:5000/docs
   - API Base URL: http://localhost:5000/api/v1

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. Run database migrations:
   ```bash
   flask db upgrade
   ```

5. Start the development server:
   ```bash
   flask run --debug
   ```

## API Endpoints

### Authentication
- POST /api/v1/auth/register - Register a new user
- POST /api/v1/auth/login - Login and get JWT token
- POST /api/v1/auth/refresh - Refresh access token

### Documents
- GET /api/v1/documents - List documents (with pagination)
- POST /api/v1/documents - Create a new document
- GET /api/v1/documents/{id} - Get document details
- PUT /api/v1/documents/{id} - Update a document
- DELETE /api/v1/documents/{id} - Delete a document
- GET /api/v1/documents/recent - Get recently viewed documents

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MYSQL_DATABASE_URI | MySQL connection URL | mysql://user:password@localhost:3306/cms |
| JWT_SECRET_KEY | Secret key for JWT tokens | None |
| JWT_ACCESS_TOKEN_EXPIRES | Access token expiration (minutes) | 30 |
| JWT_REFRESH_TOKEN_EXPIRES | Refresh token expiration (days) | 7 |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 