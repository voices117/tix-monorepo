package com.github.tix_measurements.time.server.utils;

import com.github.tix_measurements.time.core.util.TixCoreUtils;

import java.nio.ByteBuffer;
import java.security.KeyPair;

public enum TestDataUtils {
	INSTANCE;

	private final KeyPair keyPair;

	private TestDataUtils() {
		this.keyPair = TixCoreUtils.NEW_KEY_PAIR.get();
	}

	public byte[] generateMessage() throws InterruptedException {
		int reports = 10;
		int timestamps = 4;
		int timestampSize = Long.BYTES;
		int rowSize = timestamps * timestampSize;
		byte[] message = new byte[reports * rowSize];
		for (int i = 0; i < reports; i++) {
			for (int j = 0; j < timestamps; j++) {
				byte[] nanosInBytes = ByteBuffer.allocate(timestampSize).putLong(TixCoreUtils.NANOS_OF_DAY.get()).array();
				for (int k = 0; k < timestampSize; k++) {
					message[i * rowSize + j * timestampSize + k] = nanosInBytes[k];
				}
				Thread.sleep(5L);
			}
		}
		return message;
	}

	public byte[] getPublicKey() {
		return this.keyPair.getPublic().getEncoded();
	}

	public byte[] getSignature(byte[] message) {
		return TixCoreUtils.sign(message, this.keyPair);
	}
}
