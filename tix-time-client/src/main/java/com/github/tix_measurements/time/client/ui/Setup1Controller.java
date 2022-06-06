package com.github.tix_measurements.time.client.ui;

import com.github.tix_measurements.time.client.Setup;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.control.Hyperlink;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.text.Text;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.awt.*;
import java.io.IOException;
import java.net.URI;

public class Setup1Controller {

    private static final Logger logger = LogManager.getLogger();
    @FXML
    private TextField email;
    @FXML
    private PasswordField password;
    @FXML
    private Text status;
    @FXML
    private Button connectButton;
    @FXML
    private Hyperlink cancelLink;

    @FXML
    private void connect() {
        final String emailInput = email.getText().trim().replace("\"", "\\\"");
        final String passwordInput = password.getText().trim().replace("\"", "\\\"");
        if (emailInput.isEmpty() || passwordInput.isEmpty()) {
            status.setText("Debe completar ambos campos");
        } else {
            status.setText("Iniciando sesión...");

            final int responseStatusCode = Setup.login(emailInput, passwordInput);
            if (responseStatusCode == 401) {
                // login details are incorrect
                status.setText("Verifique los datos ingresados");
            } else if (responseStatusCode == 200) {
                try {
                    Parent page = FXMLLoader.load(getClass().getResource("/fxml/setup2.fxml"));
                    connectButton.getScene().setRoot(page);
                } catch (IOException e) {
                    logger.error("Cannot load setup 2 screen");
                }
            } else {
                status.setText("Falló la conexión con el servidor");
                logger.error("Cannot connect to server when trying to log in");
            }
        }
    }

    @FXML
    private void help() {
        try {
            Desktop.getDesktop().browse(new URI("http://tix.innova-red.net/"));
        } catch (Exception e) {
            logger.error("Error when opening help URL");
        }
    }

    @FXML
    private void cancel() {
        closeWindow(cancelLink);
    }

    private void closeWindow(Hyperlink link) {
        link.getScene().getWindow().hide();
    }

}
