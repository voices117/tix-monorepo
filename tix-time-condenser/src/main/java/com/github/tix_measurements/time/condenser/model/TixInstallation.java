package com.github.tix_measurements.time.condenser.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonGetter;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

import static org.assertj.core.api.Assertions.assertThat;

public class TixInstallation {
	private long id;
	private String name;
	private String publicKey;

	@JsonCreator
	public TixInstallation(
			@JsonProperty("id") long id,
			@JsonProperty("name") String name,
			@JsonProperty("publickey") String publicKey) {
		try {
			assertThat(id).isPositive();
			assertThat(name).isNotEmpty().isNotNull();
			assertThat(publicKey).isNotEmpty().isNotNull();
		} catch (AssertionError ae) {
			throw new IllegalArgumentException(ae);
		}
		this.id = id;
		this.name = name;
		this.publicKey = publicKey;
	}

	public long getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	@JsonGetter("publickey")
	public String getPublicKey() {
		return publicKey;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;

		if (!(o instanceof TixInstallation)) return false;

		TixInstallation that = (TixInstallation) o;

		return new EqualsBuilder()
				.append(getId(), that.getId())
				.append(getName(), that.getName())
				.append(getPublicKey(), that.getPublicKey())
				.isEquals();
	}

	@Override
	public int hashCode() {
		return new HashCodeBuilder(17, 37)
				.append(getId())
				.append(getName())
				.append(getPublicKey())
				.toHashCode();
	}
}
