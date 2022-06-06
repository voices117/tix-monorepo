package com.github.tix_measurements.time.client.ui;

import javafx.fxml.FXML;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.awt.*;
import java.net.URI;

public class AboutController {

    private static final Logger logger = LogManager.getLogger();

    @FXML
    private void openWebsite() {
        try {
            Desktop.getDesktop().browse(new URI("http://tix.innova-red.net/"));
        } catch (Exception e) {
            logger.error("Error when opening help URL");
        }
    }
}
