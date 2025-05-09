# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12 AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install wkhtmltopdf
RUN apt-get update && \
    apt-get install -y wkhtmltopdf

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
    awslambdaric

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.12-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Install wkhtmltopdf in final image
RUN apt-get update && \
    apt-get install -y wkhtmltopdf

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Install requirements
COPY requirements.txt ${FUNCTION_DIR}/
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ${FUNCTION_DIR}/

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.lambda_handler" ]
