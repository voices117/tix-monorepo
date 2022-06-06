# TiX monorepo

This repository contains a copy of all the repositories with every TiX service. The idea to simplify local development and temporarily push code that has some changes to make that possible.

This repository also contains a [`docker-compose.yml`](/docker-compose.yml) file that allows to spin up all services together.

## Running TiX locally

Install docker and clone this repository. Then, execute the following command:

```shell
docker-compose up --build
```

The first time the docker is executed it some services will fail because they need RabbitMQ (which takes a while to be created). Wait until RabbitMQ and the MySQL databases are created (about 20 seconds) and then stop (but don't delete!) the containers by pressing `ctrl+c` (or with the command `docker-compose stop`).

Once all services are stopped, start them again (`docker-compose up`) and this time they should start ok (some may still fail because RabbitMQ takes a while lo load, but they will retry some seconds later and succeed).
