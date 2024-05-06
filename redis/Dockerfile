FROM redis/redis-stack:latest

USER root

RUN mkdir -p /var/lib/redis-stack /data /usr/local/etc/redis && \
    chown -R 1001:0 /var/lib/redis-stack /data /usr/local/etc/redis && \
    chmod -R g+rwX /var/lib/redis-stack /data /usr/local/etc/redis

COPY --chown=1001:0 redis.conf /usr/local/etc/redis/redis.conf

USER 1001

CMD [ "/usr/bin/redis-stack-server", "/usr/local/etc/redis/redis.conf" ]
