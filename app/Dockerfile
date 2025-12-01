FROM python:3.9-slim

WORKDIR /workspace

COPY requirements.txt /workspace/app/requirements.txt
RUN pip install --no-cache-dir -r /workspace/app/requirements.txt

COPY . /workspace/app/

ENV PYTHONPATH=/workspace

CMD ["python", "-m", "app.main", "--interactive"]
