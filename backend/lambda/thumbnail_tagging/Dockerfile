FROM public.ecr.aws/lambda/python:3.10

# System dependencies
RUN yum install -y libGL ffmpeg

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and model
COPY app.py .
COPY model.pt .

CMD ["app.lambda_handler"]
