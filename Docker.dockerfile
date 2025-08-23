FROM python:3.11-slim

WORKDIR /app

# install backend
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# install frontend deps
RUN pip install --no-cache-dir streamlit requests

# copy code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# env
ENV PORT=8000
ENV BACKEND_URL=http://localhost:8000/chat

# default starts backend; override CMD for frontend container if splitting
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
