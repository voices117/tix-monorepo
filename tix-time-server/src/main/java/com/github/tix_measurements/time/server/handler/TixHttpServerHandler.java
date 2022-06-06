package com.github.tix_measurements.time.server.handler;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import io.netty.handler.codec.http.*;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static io.netty.buffer.Unpooled.copiedBuffer;

public class TixHttpServerHandler extends ChannelInboundHandlerAdapter {
	public static final String HTTP_PATH = "/health";

	private final Logger logger = LogManager.getLogger(this.getClass());

	public TixHttpServerHandler() {

	}

	@Override
	public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
		logger.entry(ctx, msg);
		if (msg instanceof FullHttpRequest) {
			logger.debug("full message received");
			final FullHttpRequest request = (FullHttpRequest) msg;
			FullHttpResponse response;
			if (request.getMethod() == HttpMethod.GET) {
				if (request.getUri().equals(HTTP_PATH)) {
					logger.info("health check request");
					final String responseMessage = new ObjectMapper().writeValueAsString(new StatusMessage(true));
					response = new DefaultFullHttpResponse(
							HttpVersion.HTTP_1_1,
							HttpResponseStatus.OK,
							copiedBuffer(responseMessage.getBytes()));
					if (HttpHeaders.isKeepAlive(request)) {
						response.headers().set(HttpHeaders.Names.CONNECTION, HttpHeaders.Values.KEEP_ALIVE);
					}
					response.headers().set(HttpHeaders.Names.CONTENT_TYPE, "application/json");
					response.headers().set(HttpHeaders.Names.CONTENT_LENGTH, responseMessage.length());
					logger.info("health check response = {}", responseMessage);
				} else {
					logger.info("bad request uri");
					response = new DefaultFullHttpResponse(
							HttpVersion.HTTP_1_1,
							HttpResponseStatus.NOT_FOUND);
					logger.info("sending 404");
				}
			} else {
				logger.info("bad request method");
				response = new DefaultFullHttpResponse(
						HttpVersion.HTTP_1_1,
						HttpResponseStatus.METHOD_NOT_ALLOWED);
				logger.info("sending 405");
			}
			ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
		} else {
			super.channelRead(ctx, msg);
		}
		logger.exit();
	}

	@Override
	public void channelReadComplete(ChannelHandlerContext ctx) throws Exception {
		logger.entry(ctx);
		ctx.flush();
		logger.exit();
	}

	@Override
	public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
		logger.entry(ctx, cause);
		logger.error("error caught", cause);
		logger.info("replying with 500");
		ctx.writeAndFlush(new DefaultFullHttpResponse(
				HttpVersion.HTTP_1_1,
				HttpResponseStatus.INTERNAL_SERVER_ERROR,
				copiedBuffer(cause.getMessage().getBytes())
		));
		logger.catching(Level.ERROR, cause);
		logger.exit();
	}

	public static class StatusMessage {
		private final boolean up;

		public StatusMessage(boolean up) {
			this.up = up;
		}

		public boolean isUp() {
			return up;
		}
	}
}
