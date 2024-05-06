# chat-doc-v1

## Environment Setup

### Python Streamlit Frontend Application

python -m venv .venv-rh1

source .venv-rh1/bin/activate

pip install -r requirements.txt

### Redis Vector Database Application

- Enter the [redis-data](./redis-data/) directory: `cd redis-data`
- Build the container: `podman build . -t redis-vector-db`
- Run the container:

```sh
podman run --rm -d --network redis-net --name redis_vector_db -v $PWD/redis.conf:/usr/local/etc/redis/redis.conf:Z -p 6379:6379 redis-vector-db:latest
```

- Run Redis Insights container to view the data in the db:

```sh
podman run -d --rm --network redis-net -v redisinsight:/db -p 5540:5540 redislabs/redisinsight:latest
```

To connect Redis Insights, simply use `redis_vector_db` as the host with 6379 as the port and the password that is specified in redis.conf

## Application Setup

Update config.yaml and, if necessary, replace the hashed password with your preferred password (use bcrypt to hash).

## Run

### Open browser window by default

streamlit run app.py

### Headless

streamlit run app.py --server.headless true

## Usage

### Create a new chat
