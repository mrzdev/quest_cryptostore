FROM python:3.9-slim-bullseye

RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir cryptofeed
RUN pip install --no-cache-dir questdb
COPY bookquest.py /bookquest.py

CMD ["/bookquest.py"]
ENTRYPOINT ["python"]