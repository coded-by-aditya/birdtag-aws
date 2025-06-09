FROM public.ecr.aws/lambda/python:3.10

# Install boto3 if needed (already available in Lambda by default, but including for local test)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY app.py .

CMD ["app.lambda_handler"]
