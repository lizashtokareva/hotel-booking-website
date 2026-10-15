FROM ubuntu:latest
LABEL authors="lizas"

ENTRYPOINT ["top", "-b"]