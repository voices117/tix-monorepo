package com.github.tix_measurements.time.server.integration_test;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.data.TixPacket;
import com.github.tix_measurements.time.core.data.TixPacketType;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import com.github.tix_measurements.time.server.TixTimeServer;
import com.github.tix_measurements.time.server.handler.TixHttpServerHandler;
import com.github.tix_measurements.time.server.util.jackson.TixPacketSerDe;
import com.github.tix_measurements.time.server.utils.TestDataUtils;
import com.rabbitmq.client.*;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.RandomUtils;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClients;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

public class TixTimeServerTest {

	private String queueHost;
	private String queueUser;
	private String queuePassword;
	private String queueName;
	private int serverWorkerThreads;
	private int udpPort;
	private int httpPort;
	private long userId;
	private long installationId;

	private TixTimeTestClient client;

	private TixTimeServer server;

	@Before
	public void setup() throws IOException, TimeoutException, InterruptedException {
		queueHost = "localhost";
		queueUser = "guest";
		queuePassword = "guest";
		queueName = "test-queue-" + RandomStringUtils.randomAlphanumeric(4);
		serverWorkerThreads = Runtime.getRuntime().availableProcessors();
		udpPort = RandomUtils.nextInt(1025, (Short.MAX_VALUE * 2) - 1);
		userId = 1L;
		installationId = 1L;
		do {
			httpPort = RandomUtils.nextInt(1025, (Short.MAX_VALUE * 2) - 1);
		} while(httpPort == udpPort);
		this.server = new TixTimeServer(queueHost, queueUser, queuePassword, queueName,
				serverWorkerThreads, udpPort, httpPort);
		this.client = new TixTimeTestClient(udpPort);
	}

	@After
	public void teardown() throws IOException, TimeoutException {
		Channel channel = getChannel();
		channel.queueDelete(queueName);
	}

	private Channel getChannel() throws IOException, TimeoutException {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(queueHost);
		return factory.newConnection()
					.createChannel();
	}

	private void testPacket(TixPacket packet) throws InterruptedException {
		this.server.start();
		this.client.start(new ChannelInboundHandlerAdapter(){
			@Override
			public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
				TixPacket incomingPacket = (TixPacket)msg;
				assertThat(incomingPacket.getTo()).isEqualTo(packet.getFrom());
				assertThat(incomingPacket.getFrom()).isEqualTo(packet.getTo());
				assertThat(incomingPacket.getInitialTimestamp()).isEqualTo(packet.getInitialTimestamp());
				assertThat(incomingPacket.getReceptionTimestamp()).isNotZero();
				assertThat(incomingPacket.getSentTimestamp()).isNotZero();
				assertThat(incomingPacket.getFinalTimestamp()).isZero();
				ctx.close();
			}
		});
		this.client.send(packet);
		this.client.stop();
		this.server.stop();
	}

	@Test
	public void testSendShortPacket() throws InterruptedException {
		TixPacket packet = new TixPacket(this.client.getClientAddress(), this.client.getServerAddress(),
				TixPacketType.SHORT, TixCoreUtils.NANOS_OF_DAY.get());
		testPacket(packet);
	}

	@Test
	public void testSendLongPacket() throws InterruptedException {
		TixPacket packet = new TixPacket(this.client.getClientAddress(), this.client.getServerAddress(),
				TixPacketType.LONG, TixCoreUtils.NANOS_OF_DAY.get());
		testPacket(packet);
	}

	@Test
	public void testSendDataPacket() throws InterruptedException, IOException, TimeoutException {
		byte[] message = TestDataUtils.INSTANCE.generateMessage();
		TixPacket dataPacket = new TixDataPacket(this.client.getClientAddress(), this.client.getServerAddress(),
				TixCoreUtils.NANOS_OF_DAY.get(), userId, installationId, TestDataUtils.INSTANCE.getPublicKey(), message,
				TestDataUtils.INSTANCE.getSignature(message));
		testPacket(dataPacket);
		Channel channel = getChannel();
		Consumer consumer = new DefaultConsumer(channel) {
			@Override
			public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
				TixPacketSerDe serde = new TixPacketSerDe();
				TixDataPacket receivedPacket = serde.deserialize(body);
				assertThat(receivedPacket).isEqualTo(dataPacket);
			}
		};
		channel.basicConsume(queueName, true, consumer);
	}

	@Test
	public void testHealthCheck() throws IOException {
		server.start();
		HttpClient httpClient = HttpClients.createMinimal();
		String url = String.format("http://localhost:%d/%s", httpPort, TixHttpServerHandler.HTTP_PATH);
		HttpGet getRequest = new HttpGet(url);
		HttpResponse response = httpClient.execute(getRequest);
		assertThat(response.getStatusLine().getStatusCode()).isEqualTo(HttpStatus.SC_OK);
		String responseContent = getEntityContent(response.getEntity());
		ObjectMapper mapper = new ObjectMapper();
		TixHttpServerHandler.StatusMessage expectedStatus = new TixHttpServerHandler.StatusMessage(true);
		assertThat(responseContent).isEqualTo(mapper.writeValueAsString(expectedStatus));
		server.stop();
	}

	private String getEntityContent(HttpEntity entity) throws IOException {
		try (BufferedReader reader = new BufferedReader(new InputStreamReader(entity.getContent()))) {
			return reader.lines().collect(Collectors.joining("\n"));
		}
	}
}
