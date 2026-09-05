FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser --home /home/appuser/ appuser

WORKDIR /code

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

ENV UV_NO_DEV=1

RUN uv sync --frozen

COPY --chown=appuser:appuser . .

USER appuser

ENTRYPOINT ["./entrypoint.sh"]

CMD ["bash", "./entrypoint.sh"]
