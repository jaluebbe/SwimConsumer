FROM openjdk:alpine as builder

WORKDIR /build/

COPY RedisOutput.java .

RUN apk update \
    && apk upgrade \
    && apk add git curl maven \
    && rm -f /var/cache/apk/* \
    && curl -LOs https://files.swim.faa.gov/jumpstart/jumpstart-latest.tar.gz \
    && mkdir jumpstart-latest \
    && tar xfvz jumpstart-latest.tar.gz -C jumpstart-latest/ \
    && rm jumpstart-latest.tar.gz \
    && git clone https://github.com/drm/java-redis-client.git \
    && mv java-redis-client/src/nl jumpstart-latest/src/main/java/ \
    && rm -fr java-redis-client \
    && mv RedisOutput.java jumpstart-latest/src/main/java/com/harris/cinnato/outputs/ \
    && cd jumpstart-latest \
    && mvn package -q \
    && mv target/jumpstart-jar-with-dependencies.jar .. \
    && cd .. \
    && rm -fr jumpstart-latest

# Build final image
FROM openjdk:alpine as consumer

WORKDIR /app/

COPY --from=builder  /build/jumpstart-jar-with-dependencies.jar .

CMD ["java", "-Dconfig.file=swim_consumer.conf", "-jar", "jumpstart-jar-with-dependencies.jar"]    
