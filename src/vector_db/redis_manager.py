class RedisManager:
    @staticmethod
    def build_redis_connection_url(redis_config):
        """Build and return a Redis connection URL from the given configuration."""
        url_format = "redis://{username}:{password}@{host}:{port}"
        return url_format.format(
            username=redis_config["username"],
            password=redis_config["password"],
            host=redis_config["host"],
            port=redis_config["port"]
        )
