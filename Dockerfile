FROM python:3.9-slim-bullseye

ARG CODEDIR=/opt/turnierchecker/

RUN apt-get update \
    && apt-get install -y bash vim curl htop tmux unzip gcc \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/local/bin/python3 /usr/bin/python3
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN python3 -m pip install --upgrade pip
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR ${CODEDIR}
ENV PYTHONPATH=${CODEDIR}
ENV RUNNING_IN_DOCKER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt ${CODEDIR}/
COPY ./turnierchecker ${CODEDIR}/
RUN pip install -r ${CODEDIR}/requirements.txt

#CMD tail -f /dev/null
CMD python3 turnierchecker.py
