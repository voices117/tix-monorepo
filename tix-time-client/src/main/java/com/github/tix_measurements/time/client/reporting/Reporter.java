package com.github.tix_measurements.time.client.reporting;

import com.github.tix_measurements.time.client.handler.TixUdpClientHandler;
import com.github.tix_measurements.time.client.reporting.utils.TixPacketSerDe;
import com.github.tix_measurements.time.core.data.TixDataPacket;
import com.github.tix_measurements.time.core.data.TixPacket;
import com.github.tix_measurements.time.core.data.TixPacketType;
import com.github.tix_measurements.time.core.decoder.TixMessageDecoder;
import com.github.tix_measurements.time.core.encoder.TixMessageEncoder;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
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
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.UnknownHostException;
import java.nio.channels.SocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.KeyPair;
import java.util.Collections;
import java.util.Enumeration;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.Executors;

public class Reporter {

    private static final int WORKER_THREADS;
    private static final String SERVER_IP;
    private static final int DEFAULT_CLIENT_PORT;
    private static final int DEFAULT_SERVER_PORT;
    private static final int MAX_UDP_PACKET_SIZE;
    private static final int LONG_PACKET_MAX_RETRIES; /* how many times will payload with measurement data be sent after every minute */
    private static final String FILE_EXTENSION;
    private static boolean longPacketReceived;
    private static Path tempFile;
    //    private static Path permPath;
    private static String permPathString;

    static {
        WORKER_THREADS = 1;
        SERVER_IP = "200.10.202.29";
        DEFAULT_CLIENT_PORT = 4501;
        DEFAULT_SERVER_PORT = 4500;

        MAX_UDP_PACKET_SIZE = 4096 + 1024;
        LONG_PACKET_MAX_RETRIES = 5;
        longPacketReceived = false;

        FILE_EXTENSION = ".tix";
    }

    private final int CLIENT_PORT;
    private final InetSocketAddress DEFAULT_SERVER_ADDRESS;
    private final long USER_ID;
    private final long INSTALLATION_ID;
    private final KeyPair KEY_PAIR;
    private final boolean SAVE_LOGS_LOCALLY;
    private final Logger logger = LogManager.getLogger();
    private final Timer timer = new Timer();

    public Reporter(final long USER_ID, final long INSTALLATION_ID, final KeyPair KEY_PAIR, final int CLIENT_PORT, final boolean SAVE_LOGS_LOCALLY) {
        this.USER_ID = USER_ID;
        this.INSTALLATION_ID = INSTALLATION_ID;
        this.KEY_PAIR = KEY_PAIR;
        this.CLIENT_PORT = CLIENT_PORT > 0 ? CLIENT_PORT : DEFAULT_CLIENT_PORT;
        try {
            DEFAULT_SERVER_ADDRESS = new InetSocketAddress(SERVER_IP, DEFAULT_SERVER_PORT);
        } catch (Exception e) {
            logger.catching(e);
            logger.fatal("Could not initialize the default server address");
            throw new Error();
        }
        this.SAVE_LOGS_LOCALLY = SAVE_LOGS_LOCALLY;
    }

    public static void setLongPacketReceived(boolean value) {
        longPacketReceived = value;
    }

    public static Path getTempFile() {
        return tempFile;
    }

    private void writePackets(final int delay, final int period, final InetSocketAddress clientAddress, final InetSocketAddress serverAddress, final Channel channel, final Path tempFile) {
        timer.scheduleAtFixedRate(new TimerTask() {
            int i = 0;
            TixPacket shortPacket;
            TixDataPacket longPacketWithData;
            byte[] mostRecentData;
            byte[] signature;
            Long nanosOfDay;

            @Override
            public void run() {
                // sending short message every second, no matter what
                shortPacket = new TixPacket(clientAddress, serverAddress, TixPacketType.SHORT, TixCoreUtils.NANOS_OF_DAY.get());
                channel.writeAndFlush(shortPacket);

                if (i == 60) {
                    // send long packet once every minute, after short packet
                    try {
                        mostRecentData = Files.readAllBytes(tempFile);
                        System.out.println("Temp file path: " + tempFile.toAbsolutePath());
                    } catch (IOException e) {
                        logger.fatal("Could not read data from temp file", e);
                        logger.catching(Level.FATAL, e);
                    }
                    if (mostRecentData == null || mostRecentData.length < 1) {
                        logger.error("No measurements recorded in the last minute");
                    } else {
                        signature = TixCoreUtils.sign(mostRecentData, KEY_PAIR);
                        nanosOfDay = TixCoreUtils.NANOS_OF_DAY.get();
                        longPacketWithData = new TixDataPacket(clientAddress, serverAddress, nanosOfDay, USER_ID, INSTALLATION_ID, KEY_PAIR.getPublic().getEncoded(), mostRecentData, signature);
                        channel.writeAndFlush(longPacketWithData);
                        if (SAVE_LOGS_LOCALLY) {
                            try {
                                Path permPathForFile = FileSystems.getDefault().getPath(permPathString + System.getProperty("file.separator") + nanosOfDay + "-tix-log.json");
                                if (!Files.exists(permPathForFile)) {
                                    permPathForFile = Files.createFile(permPathForFile);
                                }
                                TixPacketSerDe packetSerDe = new TixPacketSerDe();
                                Files.write(permPathForFile, new String(packetSerDe.serialize(longPacketWithData)).getBytes("UTF-8"), StandardOpenOption.WRITE, StandardOpenOption.SYNC);
                            } catch (IOException e) {
                                logger.fatal("Could not create permanent log file", e);
                                logger.catching(Level.FATAL, e);
                            }
                        }
                        try {
                            byte[] emptyByteArray = new byte[0];
                            Files.write(tempFile, emptyByteArray, StandardOpenOption.TRUNCATE_EXISTING);
                        } catch (IOException e) {
                            logger.fatal("Could not empty contents of temp file", e);
                            logger.catching(Level.FATAL, e);
                        }
                        longPacketReceived = false;
                    }
                } else if (i > 60 && i < (60 + LONG_PACKET_MAX_RETRIES)) {
                    // resend long packet if needed, a limited number of times
                    if (longPacketReceived) {
                        mostRecentData = null;
                        signature = null;
                        i = 0;
                    } else if (mostRecentData != null && mostRecentData.length > 0) {
                        longPacketWithData = new TixDataPacket(clientAddress, serverAddress, TixCoreUtils.NANOS_OF_DAY.get(), USER_ID, INSTALLATION_ID, KEY_PAIR.getPublic().getEncoded(), mostRecentData, signature);
                        channel.writeAndFlush(longPacketWithData);
                    }
                } else if (i == (60 + LONG_PACKET_MAX_RETRIES)) {
                    // long packet could not be sent, discard temporary copy
                    mostRecentData = null;
                    signature = null;
                    i = 0;
                }
                i++;

            }
        }, delay, period);
    }

    private InetSocketAddress getClientAddress() throws IOException {

        Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
        for (NetworkInterface networkInterface : Collections.list(interfaces)) {

            if (networkInterface.isLoopback() || !networkInterface.isUp())
                continue;

            Enumeration<InetAddress> addresses = networkInterface.getInetAddresses();
            for (InetAddress address : Collections.list(addresses)) {
                if (!address.isReachable(3000))
                    continue;

                try (SocketChannel socket = SocketChannel.open()) {
                    socket.socket().setSoTimeout(3000);

                    socket.bind(new InetSocketAddress(address, 8080));
                    socket.connect(new InetSocketAddress("tix.innova-red.net", 80));
                    logger.info("Network Interface: {}, Address: {}", networkInterface, address);

                    return new InetSocketAddress(address, CLIENT_PORT);
                } catch (IOException ex) {
                    continue;
                }
            }
        }
        return new InetSocketAddress(InetAddress.getLocalHost(), CLIENT_PORT);
    }

    public Void run() {
        logger.info("Starting Client");
        logger.info("Server Address: {}:{}", DEFAULT_SERVER_ADDRESS.getHostName(), DEFAULT_SERVER_ADDRESS.getPort());

        EventLoopGroup workerGroup;
        Class<? extends Channel> datagramChannelClass;
        if (Epoll.isAvailable()) {
            logger.info("epoll available");
            workerGroup = new EpollEventLoopGroup(WORKER_THREADS);
            datagramChannelClass = EpollDatagramChannel.class;
        } else {
            logger.info("epoll unavailable");
            logger.warn("epoll unavailable performance may be reduced due to single thread scheme.");
            workerGroup = new NioEventLoopGroup(WORKER_THREADS, Executors.privilegedThreadFactory());
            datagramChannelClass = NioDatagramChannel.class;
        }

        try {
            logger.info("Setting up");
            InetSocketAddress clientAddress = getClientAddress();
            logger.info("My Address: {}:{}", clientAddress.getAddress(), clientAddress.getPort());

            tempFile = Files.createTempFile("tix-temp-log", FILE_EXTENSION);
            System.out.println(tempFile.toString());
            tempFile.toFile().deleteOnExit();

            permPathString = System.getProperty("user.home") + System.getProperty("file.separator") + "tix-client-logs";
            final Path permPath = FileSystems.getDefault().getPath(permPathString);
            final Path permDir = Files.createDirectories(permPath);

            Bootstrap b = new Bootstrap();
            b.group(workerGroup)
                    .channel(datagramChannelClass)
                    .option(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
                    .option(ChannelOption.SO_RCVBUF, MAX_UDP_PACKET_SIZE)
                    .option(ChannelOption.RCVBUF_ALLOCATOR, new FixedRecvByteBufAllocator(MAX_UDP_PACKET_SIZE))
                    .handler(new ChannelInitializer<DatagramChannel>() {
                        @Override
                        protected void initChannel(DatagramChannel ch)
                                throws Exception {
                            ch.pipeline().addLast(new TixMessageDecoder());
                            ch.pipeline().addLast(new TixUdpClientHandler());
                            ch.pipeline().addLast(new TixMessageEncoder());
                        }
                    });
            if (Epoll.isAvailable()) {
                b.option(EpollChannelOption.SO_REUSEPORT, true);
            }
            logger.info("Binding into port {}", clientAddress.getPort());
            Channel channel = b.bind(clientAddress).sync().channel();

            writePackets(0, 1000, clientAddress, DEFAULT_SERVER_ADDRESS, channel, tempFile);

            ChannelFuture future = channel.closeFuture().await();
            if (!future.isSuccess()) {
                logger.error("Error while transmitting");
            }
        } catch (InterruptedException e) {
            logger.fatal("Interrupted", e);
            logger.catching(Level.FATAL, e);
        } catch (UnknownHostException e) {
            logger.fatal("Cannot retrieve local host address", e);
            logger.catching(Level.FATAL, e);
        } catch (IOException e) {
            logger.fatal("Cannot persist incoming message data", e);
            logger.catching(Level.FATAL, e);
        } finally {
            logger.info("Shutting down");
            timer.cancel();
            workerGroup.shutdownGracefully();
        }
        return null;
    }

}