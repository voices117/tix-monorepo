package com.github.tix_measurements.time.condenser.handlers;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.tix_measurements.time.condenser.model.TixInstallation;
import com.github.tix_measurements.time.condenser.model.TixUser;
import com.github.tix_measurements.time.condenser.utils.jackson.TixPacketSerDe;
import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.data.TixPacketType;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import org.apache.logging.log4j.util.Strings;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyPair;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Base64;
import java.util.Comparator;
import java.util.stream.Stream;

import static java.lang.String.format;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.util.Base64Utils.encodeToString;

public class TestTixReceiver {
	private static final Path REPORTS_PATH = Paths.get(System.getProperty("java.io.tmpdir"));
	private static final boolean USE_HTTPS = false;
	private static final String API_HOST = "localhost";
	private static final int API_PORT = 80;
	private static final long USER_ID = 1L;
	private static final String API_USER = "test-admin";
	private static final String API_PASS = "test-password";
	private static final String ENCODED_CREDENTIALS = encodeToString(format("%s:%s", API_USER, API_PASS).getBytes());
	private static final String USERNAME = "test-user";
	private static final long INSTALLATION_ID = 1L;
	private static final String INSTALLATION_NAME = "test-installation";
	private static final KeyPair INSTALLATION_KEY_PAIR = TixCoreUtils.NEW_KEY_PAIR.get();
	private static final TixPacketSerDe TIX_PACKET_SER_DE = new TixPacketSerDe();

	private MockRestServiceServer server;
	private TixReceiver receiver;
	private byte[] message;
	private long reportFirstUnixTimestamp;

	public static byte[] generateMessage() throws InterruptedException {
		int reports = 10;
		int unixTimestampSize = Long.BYTES;
		int packetTypeSize = Character.BYTES;
		int packetSizeSize = Integer.BYTES;
		int timestamps = 4;
		int timestampSize = Long.BYTES;
		int rowSize = unixTimestampSize + packetTypeSize + packetSizeSize + timestampSize * timestamps;
		ByteBuffer messageBuffer = ByteBuffer.allocate(reports * rowSize);
		for (int i = 0; i < reports; i++) {
			messageBuffer.putLong(LocalDateTime.now().toEpochSecond(ZoneOffset.UTC));
			char packetType = (i % 2 == 0 ? 'S' : 'L');
			messageBuffer.put((byte)packetType);
			messageBuffer.putInt((i % 2 == 0 ? TixPacketType.SHORT.getSize() : TixPacketType.LONG.getSize()));
			for (int j = 0; j < timestamps; j++) {
				messageBuffer.putLong(TixCoreUtils.NANOS_OF_DAY.get());
				Thread.sleep(5L);
			}
			Thread.sleep(1000L - 5L * timestamps);
		}
		byte[] message = messageBuffer.array();
		return message;
	}

	public static long getReportFirstUnixTimestamp(byte[] message) {
		ByteBuffer buffer = ByteBuffer.allocate(Long.BYTES);
		byte[] bytes = Arrays.copyOfRange(message, 0, Long.BYTES);
		buffer.put(bytes);
		buffer.flip();
		return buffer.getLong();
	}

	@Before
	public void setup() throws InterruptedException {
		receiver = new TixReceiver(REPORTS_PATH.toString(), USE_HTTPS, API_HOST, API_PORT, API_USER, API_PASS);
		server = MockRestServiceServer.createServer(receiver.getApiClient());
		message = generateMessage();
		reportFirstUnixTimestamp = getReportFirstUnixTimestamp(message);
	}

	public static TixDataPacket createNewPacket(byte[] message, long userId, long installationId, KeyPair keyPair) throws UnknownHostException, InterruptedException {
		TixDataPacket packet = new TixDataPacket(
				new InetSocketAddress(InetAddress.getLocalHost(), 4500),
				new InetSocketAddress(InetAddress.getByName("8.8.8.8"), 4500),
				TixCoreUtils.NANOS_OF_DAY.get(),
				userId,
				installationId,
				keyPair.getPublic().getEncoded(),
				message,
				TixCoreUtils.sign(message, keyPair));
		Thread.sleep(5L);
		packet.setReceptionTimestamp(TixCoreUtils.NANOS_OF_DAY.get());
		return packet;
	}

	@After
	public void teardown() throws IOException {
		if (REPORTS_PATH.resolve(Long.toString(USER_ID)).toFile().exists()) {
			Files.walk(REPORTS_PATH.resolve(Long.toString(USER_ID)))
					.sorted(Comparator.reverseOrder())
					.map(Path::toFile)
					.peek(System.out::println)
					.forEach(File::delete);
		}
	}

	@Test
	public void testConstructor() {
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(null, true, API_HOST, API_PORT, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(Strings.EMPTY, true, API_HOST, API_PORT, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, null, API_PORT, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, Strings.EMPTY, API_PORT, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, 0, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, -1, API_USER, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, API_PORT, null, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, API_PORT, Strings.EMPTY, API_PASS));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, API_PORT, API_USER, null));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixReceiver(REPORTS_PATH.toString(), true, API_HOST, API_PORT, API_USER, Strings.EMPTY));
	}

	@Test
	public void testValidPacket() throws IOException, InterruptedException {
		TixDataPacket packet = createNewPacket(message, USER_ID, INSTALLATION_ID, INSTALLATION_KEY_PAIR);
		ObjectMapper mapper = new ObjectMapper();
		server.expect(requestTo(format("http://%s:%d/api/user/%d", API_HOST, API_PORT, USER_ID)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(USER_ID, USERNAME, true)), MediaType.APPLICATION_JSON));
		server.expect(requestTo(format("http://%s:%d/api/user/%d/installation/%d", API_HOST, API_PORT, USER_ID, INSTALLATION_ID)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(
						mapper.writeValueAsString(new TixInstallation(INSTALLATION_ID, INSTALLATION_NAME,TixCoreUtils.ENCODER.apply(INSTALLATION_KEY_PAIR.getPublic().getEncoded()))),
						MediaType.APPLICATION_JSON));
		receiver.receiveMessage(TIX_PACKET_SER_DE.serialize(packet));
		server.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(REPORTS_PATH, packet);
		assertThat(expectedReportPath)
				.exists()
				.isDirectory();
		assertThat(Files.walk(expectedReportPath).count()).isEqualTo(2);
		final TixDataPacket expectedPacket = packet;
		try (Stream<Path> paths = Files.walk(expectedReportPath)) {
			paths.forEach(file -> {
				if (file.equals(expectedReportPath)) {
					return;
				}
				assertThat(file)
						.exists()
						.isRegularFile();
				assertThat(file.getFileName().toString())
						.startsWith(TixReceiver.REPORTS_FILE_SUFFIX)
						.endsWith(TixReceiver.REPORTS_FILE_EXTENSION);
				assertThat(file.getFileName().toString())
						.isEqualTo(format(TixReceiver.REPORTS_FILE_NAME_TEMPLATE, reportFirstUnixTimestamp));
				try (BufferedReader reader = Files.newBufferedReader(file)) {
					assertThat(reader.lines().count()).isEqualTo(1);
					reader.lines().forEach(reportLine -> {
						try {
							TixDataPacket filePacket = TIX_PACKET_SER_DE.deserialize(reportLine.getBytes());
							assertThat(filePacket).isEqualTo(expectedPacket);
						} catch (IOException e) {
							throw new AssertionError(e);
						}
					});
				} catch (IOException e) {
					throw new AssertionError(e);
				}
			});
		}
	}

	@Test
	public void testInvalidUser() throws InterruptedException, UnknownHostException, JsonProcessingException {
		long otherUserId = USER_ID + 1L;
		TixDataPacket packet = createNewPacket(message, otherUserId, INSTALLATION_ID, INSTALLATION_KEY_PAIR);
		server.expect(requestTo(format("http://%s:%d/api/user/%d", API_HOST, API_PORT, otherUserId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withStatus(HttpStatus.NOT_FOUND));
		receiver.receiveMessage(TIX_PACKET_SER_DE.serialize(packet));
		server.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(REPORTS_PATH, packet);
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	public void testDisabledUser() throws InterruptedException, UnknownHostException, JsonProcessingException {
		long otherUserId = USER_ID + 1L;
		TixDataPacket packet = createNewPacket(message, otherUserId, INSTALLATION_ID, INSTALLATION_KEY_PAIR);
		ObjectMapper mapper = new ObjectMapper();
		server.expect(requestTo(format("http://%s:%d/api/user/%d", API_HOST, API_PORT, otherUserId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(otherUserId, USERNAME, false)), MediaType.APPLICATION_JSON));
		receiver.receiveMessage(TIX_PACKET_SER_DE.serialize(packet));
		server.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(REPORTS_PATH, packet);
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	public void testInvalidInstallation() throws InterruptedException, UnknownHostException, JsonProcessingException {
		long otherInstallationId = INSTALLATION_ID + 1L;
		TixDataPacket packet = createNewPacket(message, USER_ID, otherInstallationId, INSTALLATION_KEY_PAIR);
		ObjectMapper mapper = new ObjectMapper();
		server.expect(requestTo(format("http://%s:%d/api/user/%d", API_HOST, API_PORT, USER_ID)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(USER_ID, USERNAME, true)), MediaType.APPLICATION_JSON));
		server.expect(requestTo(format("http://%s:%d/api/user/%d/installation/%d", API_HOST, API_PORT, USER_ID, otherInstallationId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withStatus(HttpStatus.NOT_FOUND));
		receiver.receiveMessage(TIX_PACKET_SER_DE.serialize(packet));
		server.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(REPORTS_PATH, packet);
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	public void testInstallationPublicKey() throws InterruptedException, UnknownHostException, JsonProcessingException {
		KeyPair otherKeyPair = TixCoreUtils.NEW_KEY_PAIR.get();
		TixDataPacket packet = createNewPacket(message, USER_ID, INSTALLATION_ID, otherKeyPair);
		ObjectMapper mapper = new ObjectMapper();
		server.expect(requestTo(format("http://%s:%d/api/user/%d", API_HOST, API_PORT, USER_ID)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(USER_ID, USERNAME, true)), MediaType.APPLICATION_JSON));
		server.expect(requestTo(format("http://%s:%d/api/user/%d/installation/%d", API_HOST, API_PORT, USER_ID, INSTALLATION_ID)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + ENCODED_CREDENTIALS))
				.andRespond(withSuccess(
						mapper.writeValueAsString(new TixInstallation(INSTALLATION_ID, INSTALLATION_NAME,TixCoreUtils.ENCODER.apply(INSTALLATION_KEY_PAIR.getPublic().getEncoded()))),
						MediaType.APPLICATION_JSON));
		receiver.receiveMessage(TIX_PACKET_SER_DE.serialize(packet));
		server.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(REPORTS_PATH, packet);
		assertThat(expectedReportPath).doesNotExist();
	}
}
