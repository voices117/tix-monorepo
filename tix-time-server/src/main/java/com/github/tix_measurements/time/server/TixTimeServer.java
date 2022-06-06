package com.github.tix_measurements.time.server;

import com.github.fnmartinez.jmicroconfigs.ConfigurationManager;
import com.github.tix_measurements.time.core.decoder.TixMessageDecoder;
import com.github.tix_measurements.time.core.encoder.TixMessageEncoder;
import com.github.tix_measurements.time.server.handler.TixHttpServerHandler;
import com.github.tix_measurements.time.server.handler.TixUdpServerHandler;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import io.netty.bootstrap.Bootstrap;
import io.netty.bootstrap.ServerBootstrap;
import io.netty.buffer.PooledByteBufAllocator;
import io.netty.channel.*;
import io.netty.channel.epoll.Epoll;
import io.netty.channel.epoll.EpollChannelOption;
import io.netty.channel.epoll.EpollDatagramChannel;
import io.netty.channel.epoll.EpollEventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.DatagramChannel;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioDatagramChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.http.HttpObjectAggregator;
import io.netty.handler.codec.http.HttpServerCodec;
import io.netty.util.concurrent.Future;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.config.Configuration;

import java.io.IOException;
import java.net.ConnectException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeoutException;

import static java.lang.String.format;

public class TixTimeServer {

	private static final int BUFFER_ALLOCATION_SIZE = 4096 + 1024; // XXX: https://stackoverflow.com/questions/13086564/netty-increase-channelbuffer-size?answertab=votes#tab-top

	private final Logger logger = LogManager.getLogger(this.getClass());

	private final String queueHost;

	private final String queueUser;

	private final String queuePassword;

	private final String queueName;

	private final Connection queueConnection;

	private final int workerThreadsQuantity;

	private final int udpPort;

	private final int httpPort;

	private final ChannelFuture[] udpFutures;

	private final Bootstrap udpBootstrap;

	private final ServerBootstrap httpBootstrap;

	private EventLoopGroup udpWorkerGroup = null;

	private ChannelFuture httpFuture = null;
	private EventLoopGroup httpMasterGroup = null;
	private EventLoopGroup httpWorkerGroup = null;

	private static void setLogLevel(String logLevel) {
		Level level = Level.getLevel(logLevel);
		LoggerContext ctx = LoggerContext.getContext(false);
		Configuration config = ctx.getConfiguration();
		config.getLoggers().forEach((s, loggerConfig) -> loggerConfig.setLevel(level));
		ctx.updateLoggers();
	}

	public static void main(String[] args) {
		Logger mainLogger = LogManager.getLogger();
		TixTimeServer server = null;
		try {
			ConfigurationManager configs = new ConfigurationManager("TIX");
			configs.loadConfigs();
			server = new TixTimeServer(configs.getString("queue.host"),
					configs.getString("queue.user"),
					configs.getString("queue.password"),
					configs.getString("queue.name"),
					configs.getInt("worker-threads-quantity"),
					configs.getInt("udp-port"),
					configs.getInt("http-port"));
			server.start();
			setLogLevel(configs.getString("log-level"));
			System.out.println("Press enter to terminate");
			while(System.in.available() == 0) {
				Thread.sleep(10);
			}
			server.stop();
		} catch (Throwable t) {
			mainLogger.catching(t);
			mainLogger.fatal("Unexpected exception", t);
		}
	}

	public TixTimeServer(String queueHost, String queueUser, String queuePassword,
	                     String queueName, int workerThreadsQuantity, int udpPort, int httpPort) throws ConnectException, InterruptedException {
		logger.entry(queueHost, queueUser, queuePassword, queueName, workerThreadsQuantity, udpPort, httpPort);
		this.queueHost = queueHost;
		this.queueUser = queueUser;
		this.queuePassword = queuePassword;
		this.queueName = queueName;
		this.workerThreadsQuantity = workerThreadsQuantity;
		this.udpPort = udpPort;
		this.httpPort = httpPort;
		this.udpFutures = new ChannelFuture[this.workerThreadsQuantity];
		this.udpBootstrap = new Bootstrap();
		this.httpBootstrap = new ServerBootstrap();
		this.queueConnection = getQueueConnection();
		logger.exit(this);
	}

	private Connection getQueueConnection() throws InterruptedException, ConnectException {
		ConnectionFactory connectionFactory = new ConnectionFactory();
		connectionFactory.setHost(queueHost);
		connectionFactory.setUsername(queueUser);
		connectionFactory.setPassword(queuePassword);
		connectionFactory.setAutomaticRecoveryEnabled(true);
		Connection queueConnection = null;
		int retries = 5;
		long backoff = 20000L;
		while (queueConnection == null && retries > 0) {
			try {
				queueConnection = connectionFactory.newConnection();
			} catch (IOException | TimeoutException e) {
				logger.warn("Error while trying to connect with the queue.", e);
				logger.info(format("Retrying in %d seconds. %d retries left.", backoff / 1000, retries));
				Thread.sleep(backoff);
				retries--;
				backoff *= 1.5;
			}
		}
		if (retries == 0) {
			throw new ConnectException("Could not connect to the RabbitMQ Broker!");
		}
		return queueConnection;
	}

	private void startTixServer() throws InterruptedException {
		Class<? extends Channel> datagramChannelClass;
		if (Epoll.isAvailable()) {
			logger.info("epoll available");
			udpWorkerGroup = new EpollEventLoopGroup(workerThreadsQuantity);
			datagramChannelClass = EpollDatagramChannel.class;
		} else {
			logger.info("epoll unavailable");
			logger.warn("epoll unavailable performance may be reduced due to single thread scheme.");
			udpWorkerGroup = new NioEventLoopGroup(workerThreadsQuantity, Executors.privilegedThreadFactory());
			datagramChannelClass = NioDatagramChannel.class;
		}

		logger.info("Setting up");
		udpBootstrap.group(udpWorkerGroup)
				.channel(datagramChannelClass)
				.option(ChannelOption.SO_RCVBUF, BUFFER_ALLOCATION_SIZE)
				.option(ChannelOption.RCVBUF_ALLOCATOR, new FixedRecvByteBufAllocator(BUFFER_ALLOCATION_SIZE))
				.option(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
				.handler(new ChannelInitializer<DatagramChannel>() {
					@Override
					protected void initChannel(DatagramChannel ch)
							throws Exception {
						logger.info("Connection with queue server established.");
						com.rabbitmq.client.Channel queueChannel = queueConnection.createChannel();
						queueChannel.queueDeclare(queueName, true, false, false, null); //Create or attach to the queue queueName, that is durable, non-exclusive and non auto-deletable1
						logger.info("Queue connected successfully");
						ch.pipeline().addLast(new TixMessageDecoder());
						ch.pipeline().addLast(new TixUdpServerHandler(queueChannel, queueName));
						ch.pipeline().addLast(new TixMessageEncoder());
					}
				});
		if (Epoll.isAvailable()) {
			udpBootstrap.option(EpollChannelOption.SO_REUSEPORT, true);
		}
		logger.info("Binding UDP into port {}", udpPort);
		for (int i = 0; i < udpFutures.length; i++) {
			udpFutures[i] = udpBootstrap.bind(udpPort).sync().channel().closeFuture();
		}
	}

	private void startHttpServer() throws InterruptedException {
		httpMasterGroup = new NioEventLoopGroup(1);
		httpWorkerGroup = new NioEventLoopGroup();
		httpBootstrap
				.group(httpMasterGroup, httpWorkerGroup)
				.channel(NioServerSocketChannel.class)
				.option(ChannelOption.SO_BACKLOG, 128)
				.childOption(ChannelOption.SO_KEEPALIVE, true)
				.childHandler(new ChannelInitializer<SocketChannel>() {
					@Override
					protected void initChannel(SocketChannel ch) throws Exception {
						ch.pipeline().addLast(new HttpServerCodec());
						ch.pipeline().addLast(new HttpObjectAggregator(512 * 1024));
						ch.pipeline().addLast(new TixHttpServerHandler());
					}
				});
		httpFuture = httpBootstrap.bind(httpPort).sync().channel().closeFuture();
	}

	public void start() {
		logger.info("Starting Server");
		try {
			startTixServer();
			startHttpServer();
		} catch (InterruptedException e) {
			logger.fatal("Interrupted", e);
			logger.catching(e);
			this.stop();
		}
	}

	private void shutdownGroup(EventLoopGroup group) {
		if (group != null) {
			Future f = group.shutdownGracefully().awaitUninterruptibly();
			if (!f.isSuccess()) {
				logger.warn("Could not shutdown group");
				throw new Error("Could not shutdown group");
			}
		}
	}

	private void stopUdpServer() {
		logger.info("Shutting down UDP server");
		if (udpWorkerGroup != null) {
			try {
				shutdownGroup(udpWorkerGroup);
			} catch (Error e) {
				logger.error("Could not shutdown UDP Server");
				throw new Error("Could not shutdown UDP Server", e);
			}
			for (int i = 0; i < workerThreadsQuantity; i++) {
				udpFutures[i].awaitUninterruptibly();
				if (!udpFutures[i].isSuccess()) {
					logger.error("Channel Future {} did not succeed", udpFutures[i]);
					throw new Error("Channel Future did not succeed");
				}
			}
		}
		logger.info("UDP server shutdown");
	}

	private void stopHttpServer() {
		logger.info("Shutting down HTTP server");
		try {
			shutdownGroup(httpWorkerGroup);
			shutdownGroup(httpMasterGroup);
		} catch (Error e) {
			logger.error("Could not shutdown HTTP Server");
			throw new Error("Could not shutdown HTTP Server", e);
		}
		if (httpFuture != null) {
			httpFuture.awaitUninterruptibly();
			if (!httpFuture.isSuccess()) {
				logger.error("Channel Future {} did not succeed", httpFuture);
				throw new Error("Channel Future did not succeed");
			}
		}
		logger.info("HTTP server shutdown");
	}

	public void stop() {
		logger.info("Shutting down");
		stopUdpServer();
		stopHttpServer();
		try {
			logger.info("Closing queue connection.");
			queueConnection.close();
		} catch (IOException e) {
			logger.catching(e);
			logger.warn("Error while closing queue connection.", e);
		}
		logger.info("Server shutdown");

	}

	public int getPort() {
		return this.udpPort;
	}
}
