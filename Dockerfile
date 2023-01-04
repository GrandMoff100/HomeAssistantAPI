ARG BUILD_FROM

FROM ${BUILD_FROM} AS base
ENV PYTHONPATH=.
WORKDIR /app
COPY ./ /app/

FROM base AS dependencies
RUN pip install --upgrade pip wheel
RUN pip install poetry
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    poetry install --with testing && \
    deactivate

FROM base AS final
COPY --from=dependencies /app/.venv /app/.venv

ENTRYPOINT [ "sh", "entrypoint.sh" ]

