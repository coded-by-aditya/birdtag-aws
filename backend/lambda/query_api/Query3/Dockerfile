FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies
RUN yum -y install gcc git libglvnd-devel

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy app code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the Lambda handler
CMD ["app.lambda_handler"]
