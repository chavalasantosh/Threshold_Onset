# THRESHOLD_ONSET — Enterprise Docker Image

FROM python:3.11-slim

WORKDIR /app

# Copy project
COPY pyproject.toml setup.py README.md ./
COPY threshold_onset/ ./threshold_onset/
COPY config/ ./config/
COPY integration/ ./integration/
COPY main.py run_and_log.py ./

# Install package (non-editable)
RUN pip install --no-cache-dir .

ENV THRESHOLD_ONSET_CONFIG=/app/config/default.json

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD threshold-onset config > /dev/null || exit 1

CMD ["threshold-onset", "run"]
