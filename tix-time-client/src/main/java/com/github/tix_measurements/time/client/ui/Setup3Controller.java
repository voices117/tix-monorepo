package com.github.tix_measurements.time.client.ui;

import com.github.tix_measurements.time.client.Main;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.text.Text;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.awt.*;
import java.net.URI;

public class Setup3Controller {

    private static final Logger logger = LogManager.getLogger();
    @FXML
    private Text savedUsername;
    @FXML
    private Text savedInstallationName;
    @FXML
    private Button closeSetupButton;
    @FXML
    private CheckBox saveLogsLocallyCheckbox;

    @FXML
    public void initialize() {
        setUsername(Main.preferences.get("username", " "));
        setInstallationName(Main.preferences.get("installationName", ""));
        setSaveLogsCheckbox(Main.preferences.getBoolean("saveLogsLocally", false));
    }

    @FXML
    public void setUsername(String name) {
        savedUsername.setText(name);
    }

    @FXML
    public void setInstallationName(String name) {
        savedInstallationName.setText(name);
    }

    @FXML
    public void setSaveLogsCheckbox(Boolean selected) {
        saveLogsLocallyCheckbox.setSelected(selected);
    }

    @FXML
    private void closeSetup() {
        closeWindow(closeSetupButton);
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
    private void saveLogsLocallyToggle() {
        boolean selected = saveLogsLocallyCheckbox.isSelected();
        Main.preferences.putBoolean("saveLogsLocally", selected);
    }

    private void closeWindow(Button button) {
        button.getScene().getWindow().hide();
    }
}
