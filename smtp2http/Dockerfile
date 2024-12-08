#ARG BUILD_FROM
#FROM $BUILD_FROM
FROM homeassistant/armv7-base-python

ENV LANG C.UTF-8

# Copy data for add-on
COPY smtp2http /
#RUN chmod a+x /smtp2http
ENTRYPOINT /smtp2http --listen 25 --webhook="https://192.168.15.50:8123/api/webhook/7l2vvVkhxaskZmFD5aw8MCTdZg6H2zJO"
