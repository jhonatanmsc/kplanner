# Trello Local

Kanban pessoal com FastAPI + Vue 3 + PostgreSQL.

## Visão geral

- Backend: `backend/` com FastAPI, SQLModel, JWT e PostgreSQL.
- Frontend: `frontend/` com Vue 3, Pinia, Vite e Tailwind.
- A aplicação roda em `http://localhost:5173` e a API em `http://localhost:8000`.

## Setup rápido com Docker Compose

No diretório raiz:

```bash
docker compose down -v
docker compose up --build
```

Abra depois em:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Backend local (sem Docker)

1. Crie e ative um ambiente Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale dependências:

```bash
cd backend
pip install -r requirements.txt
```

3. Configure a variável de ambiente `DATABASE_URL` para apontar ao seu PostgreSQL existente.

4. Rode o backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. A API ficará disponível em `http://localhost:8000`.

## Frontend local (sem Docker)

1. Instale dependências:

```bash
cd frontend
npm install
```

2. Rode o frontend:

```bash
npm run dev -- --host
```

3. A interface ficará disponível em `http://localhost:5173`.

## Notas

- O backend espera `DATABASE_URL` apontando para PostgreSQL.
- O Docker Compose já inclui `db`, `backend` e `frontend`.
- O backend cria um usuário admin padrão se nenhum admin existir.
- O frontend usa `localStorage` para manter o token de autenticação.
