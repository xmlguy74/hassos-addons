ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# install requirements for addon
RUN apk add --no-cache python3
RUN apk add --no-cache py3-pyserial
RUN apk add --no-cache py3-requests

# Copy data for add-on
COPY program.py /
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
