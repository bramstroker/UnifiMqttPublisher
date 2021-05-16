FROM python:3

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir unificontrol && \
    pip install --no-cache-dir unificontrol paho-mqtt

WORKDIR /usr/local/bin

COPY publish_stats.py .
RUN chmod +x publish_stats.py

CMD ["publish_stats.py"]