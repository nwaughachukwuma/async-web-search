#!/usr/bin/env bash

PORT=${PORT:-3131}
THREADS=${THREADS:-8}

# Calculate default workers if WORKERS not set
if [ -z "$WORKERS" ]; then
    WORKERS=$(($(nproc) * 2 + 1))
fi

exec granian --interface asgi src/main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --runtime-threads "$THREADS" \
    --loop uvloop \
    --runtime-mode mt
