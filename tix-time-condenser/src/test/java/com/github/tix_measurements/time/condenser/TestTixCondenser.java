package com.github.tix_measurements.time.condenser;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.tix_measurements.time.condenser.handlers.TestTixReceiver;
import com.github.tix_measurements.time.condenser.handlers.TixReceiver;
import com.github.tix_measurements.time.condenser.model.TixInstallation;
import com.github.tix_measurements.time.condenser.model.TixUser;
import com.github.tix_measurements.time.condenser.utils.jackson.TixPacketSerDe;
import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.amqp.rabbit.core.RabbitAdmin;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.client.MockRestServiceServer;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.net.UnknownHostException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyPair;
import java.util.Comparator;
import java.util.stream.Stream;

import static java.lang.String.format;
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.util.Base64Utils.encodeToString;

@RunWith(SpringRunner.class)
@ActiveProfiles("test")
@SpringBootTest
public class TestTixCondenser {

//	@Autowired
//	private RestTemplate restTemplate;

	@Autowired
	private RabbitAdmin rabbitAdmin;

	@Autowired
	private RabbitTemplate rabbitTemplate;

	@Autowired
	private TixReceiver tixReceiver;

	@Value("${tix-condenser.tix-api.host}")
	private String apiHost;

	@Value("${tix-condenser.tix-api.port}")
	private int apiPort;

	@Value("${tix-condenser.tix-api.https}")
	private boolean useHttps;

	@Value("${tix-condenser.tix-api.user}")
	private String apiUser;

	@Value("${tix-condenser.tix-api.password}")
	private String apiPassword;

	@Value("${tix-condenser.queues.receiving.name}")
	private String receivingQueueName;

	@Value("${tix-condenser.reports.path}")
	private String reportsPathString;

	@Value("${server.port}")
	private int actuatorPort;

	private TixPacketSerDe serDe;
	private MockRestServiceServer mockServer;
	private KeyPair installationKeyPair;
	private Path reportsPath;
	private byte[] message;
	private long reportFirstUnixTimestamp;
	private String username;
	private long userId;
	private String installationName;
	private long installationId;
	private String encodedCredentials;

	@Before
	public void setup() throws InterruptedException {
		serDe = new TixPacketSerDe();
		mockServer = MockRestServiceServer.createServer(tixReceiver.getApiClient());
		installationKeyPair = TixCoreUtils.NEW_KEY_PAIR.get();
		reportsPath = Paths.get(reportsPathString);
		message = TestTixReceiver.generateMessage();
		reportFirstUnixTimestamp = TestTixReceiver.getReportFirstUnixTimestamp(message);
		username = "test-user";
		userId = 1L;
		installationName = "test-installation";
		installationId = 1L;
		encodedCredentials = encodeToString(format("%s:%s", apiUser, apiPassword).getBytes());
	}

	@After
	public void teardown() throws IOException {
		if (reportsPath.resolve(Long.toString(userId)).toFile().exists()) {
			Files.walk(reportsPath.resolve(Long.toString(userId)))
					.sorted(Comparator.reverseOrder())
					.map(Path::toFile)
					.peek(System.out::println)
					.forEach(File::delete);
		}
		rabbitAdmin.purgeQueue(receivingQueueName, true);
	}

	private void sendTixPacket(TixDataPacket packet) throws InterruptedException, JsonProcessingException {
		rabbitTemplate.convertAndSend(receivingQueueName, serDe.serialize(packet));
		Thread.sleep(5000L);
	}

//	@Test
//	public void testHealthCheck() {
//		ResponseEntity<String> response = restTemplate.getForEntity("/health", String.class);
//		assertThat(response.getStatusCode()).isEqualByComparingTo(HttpStatus.OK);
//		String health = response.getBody();
//		assertThat(health).isNotNull();
//		assertThat(health).isNotEmpty();
//		String status = JsonPath.read(health, "$.status");
//		assertThat(status).isNotEmpty();
//		assertThat(status).isNotNull();
//		assertThat(status).isEqualToIgnoringCase("UP");
//	}

	@Test
	@DirtiesContext
	public void testValidPacket() throws InterruptedException, IOException {
		TixDataPacket packet = TestTixReceiver.createNewPacket(message, userId, installationId, installationKeyPair);
		ObjectMapper mapper = new ObjectMapper();
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d", useHttps ? "s" : "", apiHost, apiPort, userId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(userId, username, true)), MediaType.APPLICATION_JSON));
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d/installation/%d", useHttps ? "s" : "", apiHost, apiPort, userId, installationId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(
						mapper.writeValueAsString(new TixInstallation(installationId, installationName,TixCoreUtils.ENCODER.apply(installationKeyPair.getPublic().getEncoded()))),
						MediaType.APPLICATION_JSON));
		sendTixPacket(packet);
		mockServer.verify();
		Path expectedReportPath = reportsPath.resolve(Long.toString(userId)).resolve(Long.toString(installationId));
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
							TixDataPacket filePacket = serDe.deserialize(reportLine.getBytes());
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
	@DirtiesContext
	public void testInvalidUser() throws JsonProcessingException, InterruptedException, UnknownHostException {
		long otherUserId = userId + 1L;
		TixDataPacket packet = TestTixReceiver.createNewPacket(message, otherUserId, installationId, installationKeyPair);
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d", useHttps? "s": "", apiHost, apiPort, otherUserId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withStatus(HttpStatus.NOT_FOUND));
		sendTixPacket(packet);
		rabbitTemplate.convertAndSend(receivingQueueName, serDe.serialize(packet));
		sendTixPacket(packet);
		mockServer.verify();
		Path expectedReportPath = reportsPath.resolve(Long.toString(otherUserId)).resolve(Long.toString(installationId));
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	@DirtiesContext
	public void testDisabledUser() throws JsonProcessingException, InterruptedException, UnknownHostException {
		long otherUserId = userId + 1L;
		TixDataPacket packet = TestTixReceiver.createNewPacket(message, otherUserId, installationId, installationKeyPair);
		ObjectMapper mapper = new ObjectMapper();
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d", useHttps? "s": "", apiHost, apiPort, otherUserId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(otherUserId, username, false)), MediaType.APPLICATION_JSON));
		sendTixPacket(packet);
		mockServer.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(reportsPath, packet);
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	@DirtiesContext
	public void testInvalidInstallation() throws InterruptedException, UnknownHostException, JsonProcessingException {
		long otherInstallationId = installationId + 1L;
		TixDataPacket packet = TestTixReceiver.createNewPacket(message, userId, otherInstallationId, installationKeyPair);
		ObjectMapper mapper = new ObjectMapper();
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d", useHttps? "s": "", apiHost, apiPort, userId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(userId, username, true)), MediaType.APPLICATION_JSON));
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d/installation/%d", useHttps ? "s" : "", apiHost, apiPort, userId, otherInstallationId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withStatus(HttpStatus.NOT_FOUND));
		sendTixPacket(packet);
		mockServer.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(reportsPath, packet);
		assertThat(expectedReportPath).doesNotExist();
	}

	@Test
	@DirtiesContext
	public void testInstallationPublicKey() throws InterruptedException, UnknownHostException, JsonProcessingException {
		KeyPair otherKeyPair = TixCoreUtils.NEW_KEY_PAIR.get();
		TixDataPacket packet = TestTixReceiver.createNewPacket(message, userId, installationId, otherKeyPair);
		ObjectMapper mapper = new ObjectMapper();
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d", useHttps? "s": "", apiHost, apiPort, userId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(mapper.writeValueAsString(new TixUser(userId, username, true)), MediaType.APPLICATION_JSON));
		mockServer.expect(requestTo(format("http%s://%s:%d/api/user/%d/installation/%d", useHttps ? "s" : "", apiHost, apiPort, userId, installationId)))
				.andExpect(method(HttpMethod.GET))
				.andExpect(header("Authorization", "Basic " + encodedCredentials))
				.andRespond(withSuccess(
						mapper.writeValueAsString(new TixInstallation(installationId, installationName,TixCoreUtils.ENCODER.apply(installationKeyPair.getPublic().getEncoded()))),
						MediaType.APPLICATION_JSON));
		sendTixPacket(packet);
		mockServer.verify();
		Path expectedReportPath = TixReceiver.generateReportPath(reportsPath, packet);
		assertThat(expectedReportPath).doesNotExist();
	}
}
