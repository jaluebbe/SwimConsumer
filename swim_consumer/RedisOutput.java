package com.harris.cinnato.outputs;

import com.typesafe.config.Config;
import nl.melp.redis.Redis;
import java.net.Socket;

/**
 * Outputs the messages to a Redis channel
 *
 */
public class RedisOutput extends Output {
    private static Redis redis_connection;

    public RedisOutput(Config config) throws java.net.UnknownHostException, java.io.IOException {
        super(config);
        redis_connection = new Redis(new Socket(config.getString("redisHost"), 6379));
    }

    /**
     * Logs message to a Redis channel
     *
     * @param message the incoming message
     */
    @Override
    public void output(String message) {
        try {
            redis_connection.call("PUBLISH", "SWIM", this.convert(message));
        }
        catch(java.io.IOException e) {};
    }
}
