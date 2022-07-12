#!/usr/bin/env bash

condenser_image_name="condenser"
mock_server_image_name="mock-server"
queue_name="server-condenser-test"
api_host="localhost"
api_port=3000
reports_volume_name="ReportsVolume"

./gradlew bootRepackage
cp build/libs/tix-time-condenser-*.jar tix-time-condenser.jar
docker volume create --name ReportsVolume
docker build -f Dockerfile -t tixmeasurements/tix-time-condenser:citest .

docker kill ${mock_server_image_name}
docker rm ${mock_server_image_name}
docker run --name="${mock_server_image_name}" -v $PWD/docker-ci-test-resources/mock-api-responses.md:/etc/secrets/api.md -p 3000:${api_port} -dit wolfdeng/api-mock-server

echo 'Sleeping a while, waiting for the mock-server to start'
sleep 30

docker kill ${condenser_image_name}
docker rm ${condenser_image_name}
docker run --net="host" --name="${condenser_image_name}" -e TIX_CONDENSER_QUEUES_RECEIVING_NAME="${queue_name}" -e TIX_CONDENSER_TIX_API_HOST="${api_host}" -e TIX_CONDENSER_TIX_API_PORT=${api_port} -v ReportsVolume:/tmp/reports -dit tixmeasurements/tix-time-condenser:citest

echo 'Sleeping a while, waiting for the condenser to start'
sleep 60

curl -i -u guest:guest -H "content-type:application/json" -XPOST -d @$PWD/docker-ci-test-resources/docker-ci-rabbitmq-data.json http://localhost:15672/api/exchanges/%2f/amq.default/publish

echo 'Sleeping a while, waiting for me to catch up'
sleep 5

python docker-ci-test-resources/assert_docker_ci.py

exit $?
