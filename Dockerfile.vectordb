# Python 3.11 runtime as a parent image
FROM python:3.11-slim

# working directory in the container
WORKDIR /app

# Copy contents into the container at /app
COPY . /app

# Install packages in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Adjust permissions to be OpenShift compatible
# OpenShift will run the container using an arbitrarily assigned user ID,
# so we need to make sure that user has the necessary permissions.
RUN mkdir -p /.cache/huggingface/hub && \
    chmod -R 777 /.cache/huggingface/hub && \
    mkdir -p /.cache/torch/sentence_transformers/sentence-transformers_all-mpnet-base-v2 && \
    chmod -R 777 /.cache/torch/sentence_transformers/sentence-transformers_all-mpnet-base-v2 && \
    chmod -R 777 /.cache && \
    chmod -R 777 /app

# No USER command is needed since OpenShift will assign a user

EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
