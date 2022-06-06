package com.github.tix_measurements.time.server.util.jackson;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.tix_measurements.time.core.data.TixDataPacket;

import java.io.IOException;

public class TixPacketSerDe {
	private final ObjectMapper mapper;

	public TixPacketSerDe() {
		this.mapper = new ObjectMapper().addMixIn(TixDataPacket.class, TixDataPacketMixin.class);
	}

	public byte[] serialize(TixDataPacket packet) throws JsonProcessingException {
		return mapper.writeValueAsBytes(packet);
	}

	public TixDataPacket deserialize(byte[] bytes) throws IOException {
		return mapper.readValue(bytes, TixDataPacket.class);
	}
}
