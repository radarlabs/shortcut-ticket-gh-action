FROM python:3.9

COPY action.py requirements.txt /app/
WORKDIR /app

# We are installing a dependency here directly into our app source dir
RUN mkdir -p /app/dependencies && pip install --target=/app/dependencies -r requirements.txt --upgrade
ENV PYTHONPATH "/app/dependencies:${PYTHONPATH}"
CMD ["python", "action.py"]