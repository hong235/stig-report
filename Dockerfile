
FROM python:3
WORKDIR /opt/app-root/src
CMD ["python", "report.py", "--config", "report.ini"]

