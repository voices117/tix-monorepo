package com.github.tix_measurements.time.condenser.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

import static org.assertj.core.api.Assertions.assertThat;

public class TixUser {
	private long id;
	private String username;
	private boolean enabled;

	@JsonCreator
	public TixUser(
			@JsonProperty("id") long id,
			@JsonProperty("username") String username,
			@JsonProperty("enabled") boolean enabled) {
		try {
			assertThat(id).isPositive();
			assertThat(username).isNotNull().isNotEmpty();
		} catch (AssertionError ae) {
			throw new IllegalArgumentException(ae);
		}
		this.id = id;
		this.username = username;
		this.enabled = enabled;
	}

	public long getId() {
		return id;
	}

	public String getUsername() {
		return username;
	}

	public boolean isEnabled() {
		return enabled;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;

		if (!(o instanceof TixUser)) return false;

		TixUser tixUser = (TixUser) o;

		return new EqualsBuilder()
				.append(getId(), tixUser.getId())
				.append(isEnabled(), tixUser.isEnabled())
				.append(getUsername(), tixUser.getUsername())
				.isEquals();
	}

	@Override
	public int hashCode() {
		return new HashCodeBuilder(17, 37)
				.append(getId())
				.append(getUsername())
				.append(isEnabled())
				.toHashCode();
	}
}
