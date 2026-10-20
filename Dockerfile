FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY web ./web
COPY data ./data

ENV DATABASE_URL=sqlite:////dados/worlds2026.db
EXPOSE 8000
CMD ["python", "-m", "worlds2026", "api", "--host", "0.0.0.0"]
