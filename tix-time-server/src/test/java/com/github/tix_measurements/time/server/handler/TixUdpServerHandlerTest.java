package com.github.tix_measurements.time.server.handler;

import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.data.TixPacket;
import com.github.tix_measurements.time.core.data.TixPacketType;
import com.github.tix_measurements.time.core.decoder.TixMessageDecoder;
import com.github.tix_measurements.time.core.encoder.TixMessageEncoder;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import com.github.tix_measurements.time.server.util.jackson.TixPacketSerDe;
import com.github.tix_measurements.time.server.utils.TestDataUtils;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.channel.socket.DatagramPacket;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.util.Random;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

public class TixUdpServerHandlerTest {

	private EmbeddedChannel encoderDecoderChannel;
	private EmbeddedChannel testChannel;
	private Random random;
	private InetSocketAddress from;
	private InetSocketAddress to;
	private Channel queueChannel;
	private String queueName;
	private long userId;
	private long installationId;

	@Before
	public void setUp() throws Exception {
		queueChannel = mock(Channel.class);
		queueName = "mocking-queue";
		encoderDecoderChannel = new EmbeddedChannel(
				new TixMessageDecoder(),
				new TixMessageEncoder());
		testChannel = new EmbeddedChannel(
				new TixMessageDecoder(),
				new TixUdpServerHandler(queueChannel, queueName),
				new TixMessageEncoder());
		from = new InetSocketAddress(InetAddress.getLocalHost(), 4500);
		to = new InetSocketAddress(InetAddress.getLocalHost(), 4501);
		random = new Random();
		userId = 1L;
		installationId = 1L;
	}

	private <T extends TixPacket> T passThroughChannel(T message) throws InterruptedException {
		Thread.sleep(random.nextInt(10), random.nextInt(100));
		DatagramPacket datagramPacket = encodeMessage(message);
		testChannel.writeInbound(datagramPacket);
		Object returnedDatagram = testChannel.readOutbound();
		T returnedMessage = decodeDatagram((DatagramPacket)returnedDatagram);
		Thread.sleep(random.nextInt(10), random.nextInt(100));
		return returnedMessage;
	}

	@SuppressWarnings("unchecked")
	private <T extends TixPacket> T decodeDatagram(DatagramPacket datagramPacket) {
		assertThat(encoderDecoderChannel.writeInbound(datagramPacket)).isTrue();
		Object o = encoderDecoderChannel.readInbound();
		assertThat(o).isNotNull();
		return (T)o;
	}

	private <T extends TixPacket> DatagramPacket encodeMessage(T message) {
		assertThat(encoderDecoderChannel.writeOutbound(message)).isTrue();
		Object o = encoderDecoderChannel.readOutbound();
		assertThat(o).isNotNull();
		return (DatagramPacket)o;
	}

	@Test
	public void testTixTimestampPackage() throws InterruptedException {
		long initialTimestamp = TixCoreUtils.NANOS_OF_DAY.get();
		TixPacket timestampPackage = new TixPacket(from, to, TixPacketType.SHORT, initialTimestamp);
		TixPacket returnedTimestampPackage = passThroughChannel(timestampPackage);
		long finalTimestamp = TixCoreUtils.NANOS_OF_DAY.get();
		assertReturnedPackageTimestamps(timestampPackage, returnedTimestampPackage, finalTimestamp);
	}

	@Test
	public void testTixDataPackage() throws IOException, InterruptedException {
		long initialTimestamp = TixCoreUtils.NANOS_OF_DAY.get();
		byte[] message = TestDataUtils.INSTANCE.generateMessage();
		TixDataPacket dataPackage = new TixDataPacket(from, to, initialTimestamp, userId, installationId,
				TestDataUtils.INSTANCE.getPublicKey(), message, TestDataUtils.INSTANCE.getSignature(message));
		TixDataPacket returnedDataPackage = passThroughChannel(dataPackage);
		long finalTimestamp = TixCoreUtils.NANOS_OF_DAY.get();
		assertReturnedPackageTimestamps(dataPackage, returnedDataPackage, finalTimestamp);
		TixPacketSerDe serde = new TixPacketSerDe();
		verify(queueChannel).basicPublish("", queueName, null, serde.serialize(dataPackage));
	}

	private void assertReturnedPackageTimestamps(TixPacket originalPackage, TixPacket returnedPackage,
	                                             long finalTimestamp) {
		assertThat(returnedPackage.getFrom()).isEqualTo(originalPackage.getTo());
		assertThat(returnedPackage.getTo()).isEqualTo(originalPackage.getFrom());
		assertThat(returnedPackage.getInitialTimestamp()).isEqualTo(originalPackage.getInitialTimestamp());

		Stream.of(returnedPackage.getReceptionTimestamp(), returnedPackage.getSentTimestamp())
				.forEach(internalTimestamp -> {
					assertThat(internalTimestamp).isNotZero();
					assertThat(internalTimestamp).isPositive();
					assertThat(internalTimestamp).isGreaterThan(originalPackage.getInitialTimestamp());
					assertThat(internalTimestamp).isLessThan(finalTimestamp);
				});

		assertThat(returnedPackage.getReceptionTimestamp()).isLessThanOrEqualTo(returnedPackage.getSentTimestamp());
		assertThat(returnedPackage.getFinalTimestamp()).isZero();
	}
}
