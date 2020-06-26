
FROM python:3
WORKDIR /opt/app-root/src
RUN pip install --upgrade pip
CMD ["python", "report.py", "--config", "report.ini"]

