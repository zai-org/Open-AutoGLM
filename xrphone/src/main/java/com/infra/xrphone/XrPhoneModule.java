package com.infra.xrphone;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.Uri;

import androidx.annotation.NonNull;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.nio.ByteBuffer;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * XR-Phone core module:
 * - Manages XR session state
 * - Streams motion sensor data
 * - Maintains secure WS connection to InfraNet
 *
 * Requires:
 * - Android API 24+; XR devices typically 34+
 * - Manifest internet + sensors permissions
 */
public final class XrPhoneModule implements SensorEventListener {

    public enum SessionState {
        IDLE, INITIALIZING, RUNNING, ERROR, CLOSED
    }

    private final Context appContext;
    private final SensorManager sensorManager;
    private final Sensor rotationVectorSensor;

    private volatile SessionState sessionState = SessionState.IDLE;
    private WebSocketClient wsClient;
    private final AtomicBoolean wsConnected = new AtomicBoolean(false);

    private String deviceId;
    private String infraNetEndpoint;

    public XrPhoneModule(@NonNull Context context,
                         @NonNull String deviceId,
                         @NonNull String infraNetEndpoint) {
        this.appContext = context.getApplicationContext();
        this.deviceId = deviceId;
        this.infraNetEndpoint = infraNetEndpoint;

        this.sensorManager = (SensorManager) appContext.getSystemService(Context.SENSOR_SERVICE);
        this.rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
        if (rotationVectorSensor == null) {
            sessionState = SessionState.ERROR;
        }
    }

    public synchronized SessionState getSessionState() {
        return sessionState;
    }

    public synchronized void startSession() {
        if (sessionState == SessionState.RUNNING || sessionState == SessionState.INITIALIZING) {
            return;
        }
        sessionState = SessionState.INITIALIZING;

        if (rotationVectorSensor != null) {
            sensorManager.registerListener(
                    this,
                    rotationVectorSensor,
                    SensorManager.SENSOR_DELAY_GAME
            );
        }

        connectWebSocket();
    }

    public synchronized void stopSession() {
        sensorManager.unregisterListener(this);
        if (wsClient != null) {
            try {
                wsClient.close();
            } catch (Exception ignored) { }
        }
        wsConnected.set(false);
        sessionState = SessionState.CLOSED;
    }

    private void connectWebSocket() {
        try {
            URI uri = Uri.parse(infraNetEndpoint).buildUpon()
                    .appendQueryParameter("deviceId", deviceId)
                    .build()
                    .buildUpon()
                    .scheme("wss")
                    .build()
                    .toString()
                    .startsWith("wss")
                    ? new URI(infraNetEndpoint)
                    : new URI(infraNetEndpoint);
            wsClient = new WebSocketClient(uri) {
                @Override
                public void onOpen(ServerHandshake handshakedata) {
                    wsConnected.set(true);
                    sessionState = SessionState.RUNNING;
                    sendHello();
                }

                @Override
                public void onMessage(String message) {
                    handleServerMessage(message);
                }

                @Override
                public void onMessage(ByteBuffer bytes) {
                    // Future: handle binary messages (e.g., encoded scene updates)
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    wsConnected.set(false);
                    if (sessionState != SessionState.CLOSED) {
                        sessionState = SessionState.ERROR;
                    }
                }

                @Override
                public void onError(Exception ex) {
                    sessionState = SessionState.ERROR;
                }
            };
            wsClient.connect();
        } catch (Exception e) {
            sessionState = SessionState.ERROR;
        }
    }

    private void sendHello() {
        if (!wsConnected.get()) return;
        String payload = "{\"type\":\"hello\",\"deviceId\":\"" + deviceId + "\"}";
        wsClient.send(payload);
    }

    private void handleServerMessage(@NonNull String message) {
        // Minimal handler for DOM-shift-like commands
        // Expected JSON: {"type":"domShift","targetNode":"CITY_TWIN"}
        // Here you would route to your XR scene/DOM controller
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() != Sensor.TYPE_ROTATION_VECTOR) {
            return;
        }
        if (!wsConnected.get() || sessionState != SessionState.RUNNING) {
            return;
        }

        float[] rv = event.values;
        if (rv == null || rv.length < 3) return;

        long ts = event.timestamp; // ns
        String msg = "{\"type\":\"pose\",\"ts\":" + ts +
                ",\"rv\":[" + rv[0] + "," + rv[1] + "," + rv[2] + "]}";
        try {
            wsClient.send(msg);
        } catch (Exception ignored) { }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Optional: send accuracy updates or adjust filtering
    }

    public synchronized void updateInfraNetEndpoint(@NonNull String newEndpoint) {
        this.infraNetEndpoint = newEndpoint;
        if (wsClient != null && wsConnected.get()) {
            wsClient.close();
        }
        connectWebSocket();
    }

    public synchronized void updateDeviceId(@NonNull String newDeviceId) {
        this.deviceId = newDeviceId;
        if (sessionState == SessionState.RUNNING) {
            sendHello();
        }
    }
}
