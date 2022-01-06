package com.harris.cinnato.outputs;

import com.typesafe.config.Config;
import org.slf4j.Logger;   
import org.slf4j.LoggerFactory;
import nl.melp.redis.Redis;
import java.net.Socket;
                                          
/**                                       
 * Outputs the messages to a Redis channel
 *                                       
 */                                      
public class RedisOutput extends Output {
    private static final Logger logger = LoggerFactory.getLogger(RedisOutput.class);             
    private static Redis redis_connection;                                                 
                                                                                                 
    public RedisOutput(Config config) {                                                          
        super(config);                                                                
        try {                                                                         
            redis_connection = new Redis(new Socket(                                      
                config.getString("redisHost"), 6379));
        } catch (Exception e) {           
            logger.error("Failed to connect to Redis", e);
            System.exit(-1);              
        }                                 
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
        catch(java.io.IOException e) {
            logger.error("Failed to insert message into Redis", e);
        };
    }
}
