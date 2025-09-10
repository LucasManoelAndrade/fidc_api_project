import os
import random
import redis

# Conexão Redis para rate limit
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    db=0
)

def get_asset_price(asset_code):
    """
    Simula consulta de preço de ativo com rate limit por ativo.
    - Limite: 10 requisições por minuto por ativo.
    - 30% de chance de falha.
    - Preço aleatório entre 10 e 100.
    """
    key = f"asset_price_rate_limit:{asset_code}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    if current > 10:
        raise Exception("Rate limit excedido para este ativo (10 req/min)")
    if random.random() < 0.3:
        raise Exception("Falha ao consultar preço do ativo")
    return round(random.uniform(10, 100), 2)