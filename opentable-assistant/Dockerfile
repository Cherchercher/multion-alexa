FROM public.ecr.aws/lambda/python:3.9

ARG AWS_DEFAULT_REGION
ARG MULTION_API_KEY
ARG OPENAI_API_KEY
ARG MEM0_API_KEY

ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV MULTION_API_KEY=${MULTION_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV MEM0_API_KEY=${MEM0_API_KEY}

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY src ${LAMBDA_TASK_ROOT}

# Set the CMD to handler
CMD [ "lambda_function.lambda_handler" ]
