# FIDC Operations API

API para processamento assíncrono de operações financeiras de FIDC, com cálculo de taxas, integração simulada de preços de ativos, exportação para Minio/S3 e monitoramento de jobs.

---

## 🚀 Tecnologias

- Python 3.11
- Flask
- SQLAlchemy
- Celery + Redis
- Marshmallow
- PostgreSQL
- Minio (S3 compatível)
- Docker Compose
- Pytest (testes unitários)
- Logging estruturado (JSON)

---

## ⚙️ Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/fidc_project.git
cd fidc_project
```

### 2. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto (ou copie de `.env.example`):

```
DB_USER=fidc_user
DB_PASS=fidc_pass
DB_NAME=fidc_db
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio123
MINIO_BUCKET=fidc-exports
MINIO_ENDPOINT=http://minio:9000
```

### 3. Suba o ambiente com Docker Compose

```bash
docker-compose up --build
```

A API Flask estará disponível em [http://localhost:5000](http://localhost:5000).

O Minio Console estará em [http://localhost:9001](http://localhost:9001)  
Usuário: `minio`  
Senha: `minio123`

---

## 📝 Exemplos de uso

### 1. Processar operações (POST `/operations/process`)

```bash
curl -X POST http://localhost:5000/operations/process \
  -H "Content-Type: application/json" \
  -d '{
    "fidc_id": "FIDC001",
    "operations": [
      {
        "id": "op_001",
        "asset_code": "PETR4",
        "operation_type": "BUY",
        "quantity": 1000,
        "operation_date": "2024-09-01"
      }
    ]
  }'
```
**Resposta:**
```json
{
  "job_id": "uuid-gerado",
  "message": "Job criado com sucesso"
}
```

### 2. Consultar status do job (GET `/jobs/<job_id>/status`)

```bash
curl http://localhost:5000/jobs/<job_id>/status
```

### 3. Exportar operações (POST `/operations/export`)

```bash
curl -X POST http://localhost:5000/operations/export \
  -H "Content-Type: application/json" \
  -d '{
    "fidc_id": "FIDC001",
    "start_date": "2024-09-01",
    "end_date": "2024-09-30"
  }'
```

---

## 🧪 Testes

Para rodar os testes unitários:

```bash
# Se estiver usando Docker Compose:
docker-compose exec api pytest

# Ou, localmente (com ambiente virtual ativado):
pytest

# Se precisar ajustar o PYTHONPATH:
set PYTHONPATH=fidc_api && pytest
```

---

## 📁 Estrutura do Projeto

```
fidc_api/
  app/
    db/
    routes/
    schemas/
    utils/
    workers/
  main.py
tests/
  test_health.py
  test_jobs.py
  test_operations.py
docker-compose.yml
Dockerfile
.env.example
README.md
```

---

## 📝 Decisões técnicas

- **Processamento assíncrono:** Celery + Redis, garantindo retry e atomicidade.
- **API de preço de ativo:** Simulada, com falha 30% das vezes e rate limit por ativo.
- **Exportação:** Minio usado como S3 local.
- **Validação:** Marshmallow para entrada e saída.
- **Logging:** Estruturado em JSON para auditoria e observabilidade.
- **Configuração:** Variáveis de ambiente via `.env`.
- **Testes:** Pytest para funções críticas e endpoints.

---

## ❗ Observações

- Não há autenticação/autorização.
- Não há interface web.
- Não recomendado para produção sem ajustes de segurança.
- Para integração com ferramentas como Datadog ou ELK, basta coletar os logs JSON do stdout.

---

## 🏁 Subindo tudo

1. Configure o `.env`
2. Rode `docker-compose up --build`
3. Use os exemplos acima para testar a API!

---

## 🛠️ Troubleshooting

- Se o comando `pytest` não for reconhecido, instale com `pip install pytest`.
- Se der erro de importação, tente rodar: `set PYTHONPATH=fidc_api && pytest`
- Para acessar o Minio, use o console em [http://localhost:9001](http://localhost:9001).

---

## 📚 Referências

- [Flask](https://flask.palletsprojects.com/)
- [Celery](https://docs.celeryq.dev/)
- [Minio](https://min.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Pytest](https://docs.pytest.org/)