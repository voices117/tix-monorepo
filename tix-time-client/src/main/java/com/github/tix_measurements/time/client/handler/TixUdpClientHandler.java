package com.github.tix_measurements.time.client.handler;

import com.github.tix_measurements.time.client.reporting.Reporter;
import com.github.tix_measurements.time.core.data.TixPacket;
import com.github.tix_measurements.time.core.data.TixPacketType;
import com.github.tix_measurements.time.core.util.TixCoreUtils;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;

public class TixUdpClientHandler extends ChannelInboundHandlerAdapter {

    private final Logger logger = LogManager.getLogger();

    public TixUdpClientHandler() {
    }

    @Override
    public void channelRead(final ChannelHandlerContext ctx, final Object msg) throws Exception {
        logger.entry(ctx, msg);
        final TixPacket incomingMessage = (TixPacket) msg;
        logger.info("Received package {} from {}", incomingMessage, incomingMessage.getFrom());
        if (incomingMessage.getReceptionTimestamp() > 0) {
            incomingMessage.setFinalTimestamp(TixCoreUtils.NANOS_OF_DAY.get());
        }
        persistTixPacket(incomingMessage);
        super.channelRead(ctx, msg);
        logger.exit();
    }

    @Override
    public void exceptionCaught(final ChannelHandlerContext ctx, final Throwable cause) throws Exception {
        logger.entry(ctx, cause);
        logger.catching(cause);
        logger.error("exception caught", cause);
        logger.exit();
    }

    private void persistTixPacket(final TixPacket packet) {
        try {
            if (packet.getType() == TixPacketType.LONG) {

                Reporter.setLongPacketReceived(true);

            } else if (packet.getFinalTimestamp() > 0) {

                final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
                final ByteBuffer intBuffer = ByteBuffer.allocate(Integer.BYTES);
                final ByteBuffer longBuffer = ByteBuffer.allocate(Long.BYTES);

                final long unixTime = System.currentTimeMillis() / 1000L; // seconds passed since UNIX epoch

                outputStream.write(longBuffer.putLong(unixTime).array());
                longBuffer.clear();

                outputStream.write(packet.getType() == TixPacketType.LONG ? (byte) 'L' : (byte) 'S'); //char to byte cast should be OK for ASCII chars

                outputStream.write(intBuffer.putInt(packet.getType().getSize()).array());
                intBuffer.clear();

                outputStream.write(longBuffer.putLong(packet.getInitialTimestamp()).array());
                longBuffer.clear();

                outputStream.write(longBuffer.putLong(packet.getReceptionTimestamp()).array());
                longBuffer.clear();

                outputStream.write(longBuffer.putLong(packet.getSentTimestamp()).array());
                longBuffer.clear();

                outputStream.write(longBuffer.putLong(packet.getFinalTimestamp()).array());
                longBuffer.clear();

                Files.write(Reporter.getTempFile(), outputStream.toByteArray(), StandardOpenOption.CREATE, StandardOpenOption.APPEND, StandardOpenOption.WRITE, StandardOpenOption.SYNC);
            }

        } catch (IOException e) {
            logger.error("exception caught", e);
            logger.exit();
        }

    }
}