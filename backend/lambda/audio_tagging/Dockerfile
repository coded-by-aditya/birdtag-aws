FROM public.ecr.aws/lambda/python:3.10

# Install minimal tools for extraction (tar, xz) and curl
RUN yum install -y tar xz libsndfile

# Download and install static ffmpeg
RUN curl -L -o /tmp/ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    mkdir -p /tmp/ffmpeg-static && \
    tar -xf /tmp/ffmpeg.tar.xz -C /tmp/ffmpeg-static --strip-components=1 && \
    mv /tmp/ffmpeg-static/ffmpeg /usr/bin/ffmpeg && \
    chmod +x /usr/bin/ffmpeg && \
    rm -rf /tmp/ffmpeg*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY birdnet_analyzer ./birdnet_analyzer
ENV PYTHONPATH="/opt/BirdNET-Analyzer:${PYTHONPATH}"

COPY lambda_handler.py ./

CMD ["lambda_handler.lambda_handler"]
