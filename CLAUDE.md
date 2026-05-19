# Ingestion Service

Service responsible for:
- document ingestion
- normalization
- chunking
- embedding generation
- vector database persistence
The service must be stateless and horizontally scalable.

# Technology Stack
- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- LangChain
- LangGraph
- Pydantic v2

# Directory Structure
- `src/`: sources root 
- `src/api/v1/endpoints`: fastapi routers for endpoints
- `src/services`: scripts services layers 
- `src/repositories`: scripts repositories  layers
- `src/depends.py`: depends
- `src/config.py`: pydantic settings
- `src/aws/client.py`: aiobotocore.client 

# Patterns
- DI (Dependency Injection)
- Service layers
- Repository layers

# Testing
- `tests`: base folder
- use Pytest

# Environment Variables
- `.env`

# Running Locally
- `python src/main.py`

# Database
- `src/db`: base folder
- `src/db/database`: session_maker, function get_db_session

# API Endpoints
- `endpoints/chunk.py`
- `endpoints/document.py`
- `endpoints/embedding.py`
- `endpoints/health.py`
- `endpoints/normalization.py`
