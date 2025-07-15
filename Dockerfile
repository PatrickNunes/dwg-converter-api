FROM ghcr.io/osgeo/gdal:ubuntu-small-3.11.0

RUN apt-get update && apt-get install -y curl gnupg && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv && \
    apt-get clean

WORKDIR /app
COPY . .

COPY libredwg_bin/dwgread /usr/local/bin/
COPY libredwg_bin/libredwg.so* /usr/local/lib/

RUN chmod +x /usr/local/bin/dwgread && ldconfig 

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
