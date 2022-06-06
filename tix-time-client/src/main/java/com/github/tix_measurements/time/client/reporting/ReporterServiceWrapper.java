package com.github.tix_measurements.time.client.reporting;

import javafx.concurrent.Service;
import javafx.concurrent.Task;

public class ReporterServiceWrapper extends Service<Void> {
    private final Reporter reporter;

    public ReporterServiceWrapper(final Reporter reporter) {
        this.reporter = reporter;
    }

    @Override
    protected Task<Void> createTask() {
        return new Task<Void>() {
            protected Void call() {
                reporter.run();
                return null;
            }
        };
    }
}