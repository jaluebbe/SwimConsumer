package com.harris.cinnato.outputs;

import com.typesafe.config.Config;
import nl.melp.redis.Redis;
import java.net.Socket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Outputs the messages to a Redis channel
 *
 */
public class RedisOutput extends Output {
    private static final Logger logger = LoggerFactory.getLogger(RedisOutput.class);
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
    public void output(String message, String header) {
        try {
            redis_connection.call("PUBLISH", "SWIM", this.convert(message));
        }
        catch(java.io.IOException e) {
            logger.error("Redis connection failed", e);
            System.exit(-1);
        };
    }
}
