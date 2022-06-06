package com.github.tix_measurements.time.server.handler;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.handler.codec.http.*;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.nio.charset.Charset;

import static org.assertj.core.api.Assertions.assertThat;

public class TixHttpServerHandlerTest {

	private EmbeddedChannel testChannel;

	@Before
	public void setup() {
		testChannel = new EmbeddedChannel(
			new TixHttpServerHandler()
		);
	}

	private FullHttpResponse passThroughChannel(FullHttpRequest request) {
		testChannel.writeInbound(request);
		Object returnedMessage = testChannel.readOutbound();
		assertThat(returnedMessage).isInstanceOf(FullHttpResponse.class);
		return (FullHttpResponse) returnedMessage;
	}

	@Test
	public void testValidRequest() throws IOException {
		FullHttpRequest request = new DefaultFullHttpRequest(
				HttpVersion.HTTP_1_1,
				HttpMethod.GET,
				"/health"
		);
		TixHttpServerHandler.StatusMessage expectedStatus = new TixHttpServerHandler.StatusMessage(true);
		FullHttpResponse response = passThroughChannel(request);
		assertThat(response.getStatus()).isEqualTo(HttpResponseStatus.OK);
		ObjectMapper mapper = new ObjectMapper();
		String content = response.content().toString(Charset.defaultCharset());
		assertThat(content).isEqualTo(mapper.writeValueAsString(expectedStatus));
	}

	@Test
	public void testInvalidUri() {
		FullHttpRequest request = new DefaultFullHttpRequest(
				HttpVersion.HTTP_1_1,
				HttpMethod.GET,
				"/invalid"
		);
		FullHttpResponse response = passThroughChannel(request);
		assertThat(response.getStatus()).isEqualTo(HttpResponseStatus.NOT_FOUND);
	}

	@Test
	public void testInvalidMethod() {
		FullHttpRequest request = new DefaultFullHttpRequest(
				HttpVersion.HTTP_1_1,
				HttpMethod.OPTIONS,
				TixHttpServerHandler.HTTP_PATH);
		FullHttpResponse response = passThroughChannel(request);
		assertThat(response.getStatus()).isEqualTo(HttpResponseStatus.METHOD_NOT_ALLOWED);
	}
}
