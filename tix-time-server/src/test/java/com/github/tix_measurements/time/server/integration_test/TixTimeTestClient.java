package com.github.tix_measurements.time.server.integration_test;

import com.github.tix_measurements.time.core.data.TixPacket;
import com.github.tix_measurements.time.core.decoder.TixMessageDecoder;
import com.github.tix_measurements.time.core.encoder.TixMessageEncoder;
import io.netty.bootstrap.Bootstrap;
import io.netty.buffer.PooledByteBufAllocator;
import io.netty.channel.*;
import io.netty.channel.epoll.Epoll;
import io.netty.channel.epoll.EpollChannelOption;
import io.netty.channel.epoll.EpollDatagramChannel;
import io.netty.channel.epoll.EpollEventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.DatagramChannel;
import io.netty.channel.socket.nio.NioDatagramChannel;

import java.net.InetSocketAddress;
import java.util.concurrent.Executors;

public class TixTimeTestClient {

	private Bootstrap bootstrap;

	private EventLoopGroup workerGroup;

	private InetSocketAddress serverAddress;

	private InetSocketAddress clientAddress;

	private ThreadLocal<Channel> channel;

	private int workerThreadsQuantity = 1;

	TixTimeTestClient(int serverPort) {
		this.bootstrap = new Bootstrap();
		this.serverAddress = new InetSocketAddress("localhost", serverPort);
		this.clientAddress = new InetSocketAddress("localhost", serverPort + 1);
		this.channel = ThreadLocal.withInitial(() -> null);
	}

	public InetSocketAddress getClientAddress() {
		return clientAddress;
	}

	public InetSocketAddress getServerAddress() {
		return serverAddress;
	}

	public void start(final ChannelInboundHandlerAdapter handlerAdapter) {
		Class<? extends Channel> datagramChannelClass;
		if (Epoll.isAvailable()) {
			workerGroup = new EpollEventLoopGroup(workerThreadsQuantity);
			datagramChannelClass = EpollDatagramChannel.class;
		} else {
			workerGroup = new NioEventLoopGroup(workerThreadsQuantity, Executors.privilegedThreadFactory());
			datagramChannelClass = NioDatagramChannel.class;
		}
		try {
			bootstrap.group(workerGroup)
					.channel(datagramChannelClass)
					.option(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
					.handler(new ChannelInitializer<DatagramChannel>() {
						@Override
						protected void initChannel(DatagramChannel ch)
								throws Exception {
							ch.pipeline().addLast(new TixMessageDecoder());
							ch.pipeline().addLast(handlerAdapter);
							ch.pipeline().addLast(new TixMessageEncoder());
						}
					});
			if (Epoll.isAvailable()) {
				bootstrap.option(EpollChannelOption.SO_REUSEPORT, true);
			}
			this.channel.set(bootstrap.bind(clientAddress).sync().channel());
		} catch (InterruptedException ignored) {

		} finally {

		}
	}

	public void stop() throws InterruptedException {
		ChannelFuture future = this.channel.get().closeFuture().await();
		if (!future.isSuccess()) {
			throw new Error("unsuccessful channel closure");
		}
		workerGroup.shutdownGracefully();
	}

	public void send(TixPacket packet) throws InterruptedException {
		ChannelFuture future = channel.get().writeAndFlush(packet).await();
		if (!future.isSuccess()) {
			throw new Error("unsuccessful channel closure");
		}
	}
}