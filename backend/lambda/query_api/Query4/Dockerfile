FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y libGL ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY model.pt .

CMD ["app.lambda_handler"]
