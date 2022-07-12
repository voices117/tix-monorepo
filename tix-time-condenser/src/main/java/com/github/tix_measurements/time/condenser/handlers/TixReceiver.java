package com.github.tix_measurements.time.condenser.handlers;

import com.github.tix_measurements.time.condenser.model.TixInstallation;
import com.github.tix_measurements.time.condenser.model.TixUser;
import com.github.tix_measurements.time.condenser.utils.jackson.TixPacketSerDe;
import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import com.google.common.base.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Arrays;
import java.util.Base64;
import java.util.Collections;
import java.util.Set;

import static java.lang.String.format;
import static org.assertj.core.api.Assertions.assertThat;

@Component
public class TixReceiver {
	private static final Set<PosixFilePermission> REPORTS_DIRECTORIES_PERMISSIONS = Collections.unmodifiableSet(PosixFilePermissions.fromString("rwxr-x---"));
	public static final String USER_TEMPLATE = "%s/user/%d";
	public static final String INSTALLATION_TEMPLATE = "%s/installation/%d";
	public static final String REPORTS_FILE_SUFFIX = "tix-report";
	public static final String REPORTS_FILE_EXTENSION = "json";
	public static final String REPORTS_FILE_NAME_TEMPLATE = format("%s-%%d.%s", REPORTS_FILE_SUFFIX, REPORTS_FILE_EXTENSION);

	private final Logger logger = LoggerFactory.getLogger(TixReceiver.class);
	private final TixPacketSerDe packetSerDe;
	private final RestTemplate apiClient;
	private final Path baseReportsPath;
	private final String apiPath;
	private final HttpHeaders headers;

	public TixReceiver(@Value("${tix-condenser.reports.path}") String reportsPath,
	                   @Value("${tix-condenser.tix-api.https}") boolean useHttps,
	                   @Value("${tix-condenser.tix-api.host}") String apiHost,
	                   @Value("${tix-condenser.tix-api.port}") int apiPort,
	                   @Value("${tix-condenser.tix-api.user}") String apiUser,
	                   @Value("${tix-condenser.tix-api.password}") String apiPassword) {
		logger.info("Creating TixReceiver");
		logger.trace("reportsPath={} useHttps={} apiHost={} apiPort={} apiUser={} apiPassword={}", reportsPath, useHttps, apiHost, apiPort, apiUser, apiPassword);
		try {
			assertThat(reportsPath).isNotEmpty().isNotNull();
			assertThat(apiHost).isNotEmpty().isNotEmpty();
			assertThat(apiPort).isPositive();
			assertThat(apiUser).isNotEmpty().isNotNull();
			assertThat(apiPassword).isNotEmpty().isNotNull();
		} catch (AssertionError ae) {
			throw new IllegalArgumentException(ae);
		}
		this.packetSerDe = new TixPacketSerDe();
		this.apiClient = new RestTemplate();
		this.baseReportsPath = Paths.get(reportsPath).toAbsolutePath();
		this.apiPath = format("http%s://%s:%d/api", useHttps ? "s" : "", apiHost, apiPort);
		this.headers = new HttpHeaders();
		String credentials = format("%s:%s", apiUser, apiPassword);
		String base64Credentials = Base64.getEncoder().encodeToString(credentials.getBytes());
		headers.add("Authorization", "Basic " + base64Credentials);
	}

	public static Path generateReportPath(Path baseReportsPath, TixDataPacket packet) {
		return baseReportsPath.resolve(Long.toString(packet.getUserId()))
				.resolve(Long.toString(packet.getInstallationId()));
	}

	private boolean validUser(TixDataPacket packet) {
		HttpEntity<String> request = new HttpEntity<>(this.headers);
		ResponseEntity<TixUser> userResponseEntity = apiClient.exchange(format(USER_TEMPLATE, apiPath, packet.getUserId()), HttpMethod.GET, request, TixUser.class);
		boolean okResponseStatus = userResponseEntity.getStatusCode() == HttpStatus.OK;
		boolean userEnabled = userResponseEntity.getBody().isEnabled();
		if (!okResponseStatus) {
			logger.warn("Response status is not 200 OK");
		}
		if (!userEnabled) {
			logger.warn("User is disabled");
		}
		return  okResponseStatus && userEnabled;
	}

	private boolean validInstallation(TixDataPacket packet) {
		HttpEntity<String> request = new HttpEntity<>(this.headers);
		String userPath = format(USER_TEMPLATE, apiPath, packet.getUserId());
		ResponseEntity<TixInstallation> installationResponseEntity =
				apiClient.exchange(format(INSTALLATION_TEMPLATE, userPath, packet.getInstallationId()), HttpMethod.GET, request, TixInstallation.class);
		String packetPk = TixCoreUtils.ENCODER.apply(packet.getPublicKey());
		boolean okResponseStatus = installationResponseEntity.getStatusCode() == HttpStatus.OK;
		if (!okResponseStatus) {
			logger.warn("Response status is not 200 OK");
			return false;
		}
		if (installationResponseEntity.getBody() == null) {
			logger.warn("Response body is empty!");
			return false;
		}
		boolean publicKeyMatch = !Strings.isNullOrEmpty(installationResponseEntity.getBody().getPublicKey()) &&
				installationResponseEntity.getBody().getPublicKey().equals(packetPk);
		if (!publicKeyMatch) {
			logger.warn(format("Installation Public Key do not match with packet Public Key.\nInstallation Public Key %s\nPacket Public Key %s",
					installationResponseEntity.getBody().getPublicKey(), packetPk));
			return false;
		}
		return true;
	}

	private boolean validUserAndInstallation(TixDataPacket packet) {
		return validUser(packet) && validInstallation(packet);
	}

	@RabbitListener(queues = "${tix-condenser.queues.receiving.name}")
	public void receiveMessage(@Payload byte[] message) {
		logger.info("New message received");
		logger.trace("message={}", message);
		try {
			final TixDataPacket packet = packetSerDe.deserialize(message);
			if (packet.isValid()) {
				if (validUserAndInstallation(packet)) {
					logger.info("New valid packet received");
					logger.debug("packet={}", packet);
					Path reportDirectory = generateReportPath(baseReportsPath, packet);
					logger.debug("reportDirectory={}", reportDirectory);
					if (!Files.exists(reportDirectory)) {
						logger.info("Creating reports directory");
						Files.createDirectories(reportDirectory,
								PosixFilePermissions.asFileAttribute(REPORTS_DIRECTORIES_PERMISSIONS));
					}
					long firstReportTimestamp = getFirstReportTimestamp(packet);
					Path reportPath = reportDirectory.resolve(format(REPORTS_FILE_NAME_TEMPLATE, firstReportTimestamp));
					if (!Files.exists(reportPath)) {
						Files.createFile(reportPath);
						logger.info("Creating report file");
						logger.debug("reportPath={}", reportPath);
						try (BufferedWriter writer = Files.newBufferedWriter(reportPath)) {
							writer.write(new String(packetSerDe.serialize(packet)));
						}
						logger.info("Report file successfully created");
					} else {
						logger.info("Report file already exists. Not writing to disk.");
						logger.info("reportPath={}", reportPath);
					}
				} else {
					logger.warn("Invalid user or installation");
					logger.debug("packet={}", packet);
				}
			} else {
				logger.warn("Invalid packet");
				logger.debug("packet={}", packet);
			}
		} catch (IOException ioe) {
			logger.error("Exception caught", ioe);
			throw new IllegalArgumentException(ioe);
		} catch (HttpClientErrorException hcee) {
			logger.error("Client Error caught", hcee);
			if (hcee.getStatusCode() == HttpStatus.NOT_FOUND) {
				logger.info("Discarding error silently");
			} else {
				logger.warn("Error is not a 404!");
				throw hcee;
			}
		}
	}

	public long getFirstReportTimestamp(TixDataPacket packet) {
		byte[] bytes = Arrays.copyOfRange(packet.getMessage(), 0, Long.BYTES);
		ByteBuffer buffer = ByteBuffer.allocate(Long.BYTES);
		buffer.put(bytes);
		buffer.flip();
		return buffer.getLong();
	}

	public RestTemplate getApiClient() {
		return apiClient;
	}

	public Path getBaseReportsPath() {
		return baseReportsPath;
	}

	public String getApiPath() {
		return apiPath;
	}
}
