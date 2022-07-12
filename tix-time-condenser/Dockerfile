FROM ubuntu:xenial
MAINTAINER Facundo Martinez <fnmartinez88@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

# Installing basic utils for software language installation and logging
RUN apt-get update -y \
	&& apt-get install -y \
			software-properties-common \
			curl

# Installing and setting up software and properties specific to the Java Language
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
RUN add-apt-repository ppa:webupd8team/java \
	&& apt-get update \
	&& apt-get install -y oracle-java8-installer \
	&& apt-get install -y oracle-java8-set-default

RUN mkdir -p /root/tix-time-condenser
COPY tix-time-condenser.jar /root/tix-time-condenser
COPY run.sh /root/tix-time-condenser
WORKDIR /root/tix-time-condenser

ENTRYPOINT ["./run.sh"]
