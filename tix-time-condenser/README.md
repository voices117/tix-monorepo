# tix-time-condenser
[![Build Status](https://travis-ci.org/TiX-measurements/tix-time-condenser.svg?branch=master)](https://travis-ci.org/TiX-measurements/tix-time-condenser)
[![codecov](https://codecov.io/gh/TiX-measurements/tix-time-condenser/branch/master/graph/badge.svg)](https://codecov.io/gh/TiX-measurements/tix-time-condenser)

This is the `tix-time-condenser` microservice. The idea behind it is to condense all the reports from the server into the 
directories of each user and installation.  
It also checks the package integrity and coherence by performing a check upon the message, signature and public key provided.

## Installation

The `tix-time-condenser` is currently in CD through Travis and DockerHub. So to install it you just need to download the 
latest release of this repository container and run the image.

Since this microservice is made using SpringBoot, you can update any configuration variable using environment variables 
or passing them to the image at runtime.

It is important to add a volume to the container, since the image may be fragile, or there might be more than one image, 
but the reports must always be kept safe for processing.

## Configurations

The `tix-time-condenser` has four SpringBoot Profiles. `dev` or `default`, `test`, `staging` and `production`. While 
they are self explanatory, you should bare in mind that

  * `dev` or `default` are for development purposes only
  * `test` is only intended for the CI environment
  * `staging` is to deploy the microservice in an unestable environment
  * `production` is to deploy the microservice in the stable environment
  
Both `staging` and `production` have almost no difference whatsoever in the performance department. The only difference 
is in the queue name where the new packets are received.

## How to run it

If you are in a dev environment, you can simply use the gradle script by doing:
```
$> ./gradlew bootRun
```

If you are in a deployment environment or simply want to run the container, you can must follow these steps:
```
$> docker volume create --name ReportsVolume
$> docker run --net="host" -v ReportsVolume:/tmp/reports -dit tixmeasurements/tix-time-condenser:latest
```

In the first step we create a volume that will be used by our container and the `tix-time-processor`'s. 
On the second step we run our container with:

  * The host interface so we can attach to the RabbitMQ service
  * The name `tix_time_condenser` to be able to find it quicker when doing `docker ps` or any other docker management command
  * The `-v` flag with our recently created volume
  * The `-d` flag to detach it and run it as a daemon
  
Since the version 0.2.0, the `tix-time-condenser` uses Basic Auth to authenticate with the API. The default values for the 
`tix-condenser.api.user` and the `tix-condenser.api.password` parameters are `admin` and `admin`, respectively. The values
in the Docker version for `production` and `staging` are left blank on purpose. This will end up crashing the app unless 
you pass the parameters by environment variables arguments to in the `docker run` command.
