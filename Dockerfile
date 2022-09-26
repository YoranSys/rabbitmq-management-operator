FROM python:3.10
ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
ADD rabbitmq-management.py /src/rabbitmq-management.py
CMD kopf run --liveness=http://0.0.0.0:8080/healthz --all-namespaces /src/rabbitmq-management.py --verbose