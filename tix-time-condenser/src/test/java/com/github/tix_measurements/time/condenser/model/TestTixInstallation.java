package com.github.tix_measurements.time.condenser.model;

import com.github.tix_measurements.time.core.util.TixCoreUtils;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.Test;

import java.security.KeyPair;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

public class TestTixInstallation {
	private static final long ID = 1L;
	private static final String INSTALLATION_NAME = "installation-test";
	private static final KeyPair KEY_PAIR = TixCoreUtils.NEW_KEY_PAIR.get();
	private static final String PUBLIC_KEY = TixCoreUtils.ENCODER.apply(KEY_PAIR.getPublic().getEncoded());

	private TixInstallation installation;

	@Before
	public void setup() {
		installation = new TixInstallation(ID, INSTALLATION_NAME, PUBLIC_KEY);
	}

	@Test
	public void testConstructor() {
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(0L, INSTALLATION_NAME, PUBLIC_KEY));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(-1L, INSTALLATION_NAME, PUBLIC_KEY));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(ID, null, PUBLIC_KEY));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(ID, StringUtils.EMPTY, PUBLIC_KEY));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(ID, INSTALLATION_NAME, null));
		assertThatExceptionOfType(IllegalArgumentException.class)
				.isThrownBy(() -> new TixInstallation(ID, INSTALLATION_NAME, StringUtils.EMPTY));
	}

	@Test
	public void testEquals() {
		assertThat(installation).isNotEqualTo(null);
		assertThat(installation).isNotEqualTo(new Object());
		assertThat(installation).isEqualTo(installation);
		TixInstallation otherInstallation = new TixInstallation(installation.getId(), installation.getName(), installation.getPublicKey());
		assertThat(installation).isEqualTo(otherInstallation);
		otherInstallation = new TixInstallation(installation.getId() + 1, installation.getName(), installation.getPublicKey());
		assertThat(installation).isNotEqualTo(otherInstallation);
		otherInstallation = new TixInstallation(installation.getId(), RandomStringUtils.randomAlphabetic(installation.getName().length() + 1), installation.getPublicKey());
		assertThat(installation).isNotEqualTo(otherInstallation);
		KeyPair otherKeyPair = TixCoreUtils.NEW_KEY_PAIR.get();
		String otherPublicKey = TixCoreUtils.ENCODER.apply(otherKeyPair.getPublic().getEncoded());
		otherInstallation = new TixInstallation(installation.getId(), installation.getName(), otherPublicKey);
		assertThat(installation).isNotEqualTo(otherInstallation);
	}

	@Test
	public void testHashCode() {
		TixInstallation otherInstallation = new TixInstallation(installation.getId(), installation.getName(), installation.getPublicKey());
		assertThat(installation.hashCode()).isEqualTo(otherInstallation.hashCode());
		otherInstallation = new TixInstallation(installation.getId() + 1, installation.getName(), installation.getPublicKey());
		assertThat(installation.hashCode()).isNotEqualTo(otherInstallation.hashCode());
		otherInstallation = new TixInstallation(installation.getId(), RandomStringUtils.randomAlphabetic(installation.getName().length() + 1), installation.getPublicKey());
		assertThat(installation.hashCode()).isNotEqualTo(otherInstallation.hashCode());
		KeyPair otherKeyPair = TixCoreUtils.NEW_KEY_PAIR.get();
		String otherPublicKey = TixCoreUtils.ENCODER.apply(otherKeyPair.getPublic().getEncoded());
		otherInstallation = new TixInstallation(installation.getId(), installation.getName(), otherPublicKey);
		assertThat(installation.hashCode()).isNotEqualTo(otherInstallation.hashCode());
	}
}
