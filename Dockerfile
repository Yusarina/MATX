FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libgtk-3-0 libgdk-pixbuf2.0-0 libpango-1.0-0 libpangocairo-1.0-0 \
    libglib2.0-0 libcairo2 libwebkit2gtk-4.0-37 xvfb

RUN pip3 install wxPython

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

CMD ["xvfb-run", "python3", "-m", "unittest", "discover", "tests"]
