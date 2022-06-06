# tix-time-server
[![Build Status](https://travis-ci.org/TiX-measurements/tix-time-server.svg?branch=master)](https://travis-ci.org/TiX-measurements/tix-time-server)
[![codecov](https://codecov.io/gh/TiX-measurements/tix-time-server/branch/master/graph/badge.svg)](https://codecov.io/gh/TiX-measurements/tix-time-server)

The `tix-time-server` is a micro-service that is expected to receive all the packets coming from the `tix-client`s. There are two modes in which it operates. 

If the packet is a normal packet, it simply returns with the added reception and sent timestamps.

If the packet is a data packet, it also serializes this packet into a queue. This is to make further processing later.

The server provides a health check endpoint that can be used to assert it's health.

## Installation

The `tix-time-server` is currently in CD, by using Travis and DockerHub. So to install it you only need to download the latest container from the repository.

This micro-service is not made with special framework, but it uses a custom solution for externalized configuration that is loosely based in SpringBoot Profiles.  
It can use either the variables held in the `application.yml` or replace any value by using the environment variables.

## Configuration

As previously stated, the `tix-time-server` uses a custom configuration service that uses primarily the `application.yml` file. There you can find all the configurations variables and default settings for each _profile_.

If you need to override any variable, you can simply use an environment variable for that. The environment variable must start with the `TIX` prefix. 

Then, for each property category, the environment variable must use double underscore (*\_\_*). The category name must use underscores. So, for example, if you want to override the host where the RabbitMQ service is running, the environment variable name must be `TIX__QUEUE__HOST`. If you want to override the number of working threads, the environment variable name must be `TIX__WORKER_THREADS_QUANTITY`.

The `evironment` keyword is reserved. So if you want to use a particular environment/profile, you must override the variable by giving the environment variable `TIX__ENVIRONMENT` the value you need.

## How to run it

Since this is a standalone micro-service with no framework support whatsoever, created using gradle, to run it outside the container you only need to run:
```
$> ./gradlew fatJar
$> java -jar build/libs/tix-time-server-all-<VERSION>.jar
```

On the other hand, if you want to use the service in a container, you simply need to run
```
$> docker run -dit tixmeasurements/tix-time-server:latest
```