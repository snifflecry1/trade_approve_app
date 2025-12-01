FROM python:3.9-slim

WORKDIR /workspace

COPY tests/requirements_dev.txt /workspace/tests/requirements_dev.txt
RUN pip install --no-cache-dir -r /workspace/tests/requirements_dev.txt

COPY app/ /workspace/app/
COPY tests/ /workspace/tests/

ENV PYTHONPATH=/workspace

CMD ["pytest", "-v"]
