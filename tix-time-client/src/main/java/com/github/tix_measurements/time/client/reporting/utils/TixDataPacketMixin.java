package com.github.tix_measurements.time.client.reporting.utils;

import com.fasterxml.jackson.annotation.JsonIgnore;

public abstract class TixDataPacketMixin {
    @JsonIgnore
    abstract boolean isValid();
}