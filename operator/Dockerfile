FROM python:3.9-slim
ENV USER_ID=1001
ENV GROUP_ID=1001
RUN apt-get update && apt-get install -y git && apt-get clean
RUN groupadd -g $GROUP_ID gitrollout && \
    useradd -m -u $USER_ID -g $GROUP_ID gitrollout
WORKDIR /app
RUN chown -R gitrollout:gitrollout /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER gitrollout
ENTRYPOINT ["python", "main.py"]
