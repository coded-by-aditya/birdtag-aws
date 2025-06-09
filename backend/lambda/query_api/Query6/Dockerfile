FROM public.ecr.aws/lambda/python:3.10

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY app.py ${LAMBDA_TASK_ROOT}

# Command
CMD ["app.lambda_handler"]