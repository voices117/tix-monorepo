FROM ubuntu:xenial
MAINTAINER Facundo Martinez <fnmartinez88@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

# Installing basic utils for software language installation and logging
RUN apt-get update -y \
	&& apt-get install -y \
			software-properties-common \
			curl
RUN apt-get install -y wget

# install Java
WORKDIR /usr/local/
COPY jdk-8u202-linux-x64.tar.gz .

RUN tar zxvf jdk-8u202-linux-x64.tar.gz
RUN update-alternatives --install /usr/bin/java java /usr/local/jdk1.8.0_202/bin/java 100

COPY . .
RUN ./gradlew bootRepackage
RUN rm jdk-8u202-linux-x64.tar.gz

RUN mkdir -p /root/tix-time-condenser
RUN mv build/libs/tix-time-condenser-*.jar /root/tix-time-condenser.jar
#COPY tix-time-condenser.jar /root/tix-time-condenser
RUN mv run.sh /root/
WORKDIR /root/

ENTRYPOINT ["./run.sh"]
