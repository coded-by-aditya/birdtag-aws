# Start with AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.10

# Install OS packages for OpenCV and soundfile
RUN yum install -y \
    gcc \
    ffmpeg \
    libsndfile \
    mesa-libGL \
    tar \
    xz && \
    yum clean all

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy your function code
COPY lambda_handler.py ./

# (Optional) Set environment variable for Numba cache
ENV NUMBA_CACHE_DIR="/tmp/numba_cache"

# Lambda entrypoint
CMD ["lambda_handler.lambda_handler"]
