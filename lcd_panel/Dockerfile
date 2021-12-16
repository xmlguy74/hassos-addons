#ARG BUILD_FROM
#FROM $BUILD_FROM
FROM homeassistant/armv7-base-python

ENV LANG C.UTF-8

# install requirements for addon
#RUN apk add --no-cache python3
#RUN apk add --no-cache py3-pyserial
#RUN apk add --no-cache py3-requests
#RUN apk add --no-cache py3-pip

RUN apk add --no-cache gcc
RUN apk add --no-cache musl-dev
#RUN apk add --no-cache python3-dev
RUN pip3 install pyserial
RUN pip3 install requests
RUN pip3 install RPi.GPIO==0.7.1a4

# Copy data for add-on
COPY program.py /
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
