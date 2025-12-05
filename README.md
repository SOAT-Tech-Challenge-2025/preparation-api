# API de Preparação - SOAT Tech Challenge

Este repositório contém o **microsserviço de preparação** desenvolvido como parte da pós-graduação em **Arquitetura de Software** da **FIAP**. Este serviço é responsável por gerenciar todo o fluxo de preparação de pedidos, desde o recebimento de notificações de pagamento confirmado até o controle da fila de preparação e finalização dos pedidos.

## 📌 Menu

- [Integrantes](#integrantes)
- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
  - [Clean Architecture](#clean-architecture)
  - [Domain-Driven Design (DDD)](#domain-driven-design-ddd)
  - [Comunicação Assíncrona](#comunicação-assíncrona)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração e Execução](#configuração-e-execução)
  - [Pré-requisitos](#pré-requisitos)
  - [Variáveis de Ambiente](#variáveis-de-ambiente)
  - [Execução Local com Docker Compose](#execução-local-com-docker-compose)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Implantação na AWS](#implantação-na-aws)
- [Endpoints da API](#endpoints-da-api)
- [Licença](#licença)

## Integrantes

| Nome                                       | RM       | Discord                   |
| ------------------------------------------ | -------- | ------------------------- |
| Carlos Eduardo Bastos Laet                 | RM361151 | CarlosLaet                |
| Karen Lais Martins Pontes de Fávere Orrico | RM361158 | Karen Pontes              |
| Lucas Martins Barroso                      | RM362732 | Lucas Barroso - RM362732  |
| Raphael Oliver                             | RM362129 | Raphael Oliver - RM362129 |

## Sobre o Projeto

Na **Fase 4** da pós-graduação, o projeto passou por uma transformação arquitetural significativa: a API monolítica original foi decomposta em uma **arquitetura de microsserviços**. Esta API é o microsserviço responsável exclusivamente pela gestão da preparação de pedidos.

O sistema completo é composto por:
- **[Lambda de Autenticação](https://github.com/SOAT-Tech-Challenge-2025/lambda-identification-auth)**: Autenticação e identificação de usuários
- **[Carrinho de Compras](https://github.com/SOAT-Tech-Challenge-2025/ms-shopping-cart)**: Gerenciamento de pedidos e produtos
- **[API de Pagamentos](https://github.com/SOAT-Tech-Challenge-2025/payment-api)**: Gerenciamento de pagamentos e integração com Mercado Pago
- **[API de Preparação](https://github.com/SOAT-Tech-Challenge-2025/preparation-api)**: Este repositório - gerenciamento da fila de preparação
- **[Infraestrutura](https://github.com/SOAT-Tech-Challenge-2025/infrastructure)**: Terraform para VPC, EKS e API Gateway
- **[Database](https://github.com/SOAT-Tech-Challenge-2025/database)**: Gestão de bancos de dados do projeto

### Motivação da Separação

O módulo de preparação foi modelado desde o início do projeto como um **Bounded Context** independente, seguindo os princípios de Domain-Driven Design. No monolito original, cada contexto já era implementado como um módulo bem isolado, sem relacionamentos entre tabelas de diferentes contextos no banco de dados.

A decomposição em microsserviços na Fase 4 foi uma evolução natural dessa arquitetura, proporcionando:
- **Bounded Contexts bem definidos**: Cada microsserviço representa um contexto delimitado do domínio
- **Autonomia de dados**: Cada contexto possui seu próprio banco de dados, reforçando o isolamento
- **Escalabilidade independente**: Possibilidade de escalar cada serviço conforme sua demanda específica
- **Resiliência**: Falhas em um contexto não afetam diretamente outros contextos
- **Evolução independente**: Times podem evoluir cada bounded context de forma autônoma

## Arquitetura

### Clean Architecture

O projeto segue os princípios da **Clean Architecture** (Arquitetura Limpa), organizando o código em camadas bem definidas:

```
preparation_api/
├── domain/                         # Camada de Domínio (regras de negócio)
│   ├── entities/                   # Entidades do domínio
│   ├── value_objects/              # Objetos de valor
│   ├── ports/                      # Interfaces (portas)
│   └── exceptions.py               # Exceções do domínio
├── application/                    # Camada de Aplicação (casos de uso)
│   ├── use_cases/                  # Implementação dos casos de uso
│   └── commands/                   # Comandos de entrada
├── adapters/                       # Camada de Adaptadores
│   ├── inbound/                    # Adaptadores de entrada
│   │   ├── rest/                   # API REST
│   │   └── listeners/              # Listeners SQS
│   └── outbound/                   # Adaptadores de saída (repositórios, HTTP clients)
├── infrastructure/                 # Camada de Infraestrutura
│   ├── config.py                   # Configurações
│   ├── factory.py                  # Factories de dependências
│   ├── orm/                        # SQLAlchemy models e session manager
│   └── alembic/                    # Migrações de banco de dados
└── entrypoints/                    # Pontos de entrada da aplicação
    ├── api.py                      # FastAPI application
    └── payment_closed_listener.py  # Consumer SQS
```

#### Camadas

1. **Domain (Domínio)**:
   - Contém as regras de negócio puras
   - Entidades: `Preparation` (preparação com status e posição na fila)
   - Value Objects: `PreparationStatus` (RECEIVED, IN_PREPARATION, READY, COMPLETED)
   - Independente de frameworks e tecnologias

2. **Application (Aplicação)**:
   - Casos de uso que orquestram as regras de negócio
   - `CreatePreparationFromPaymentUseCase`: Cria preparação a partir de pagamento confirmado
   - `StartNextPreparationUseCase`: Inicia próxima preparação da fila
   - `MarkPreparationAsReadyUseCase`: Marca preparação como pronta
   - `MarkPreparationAsCompletedUseCase`: Marca preparação como entregue
   - `GetWaitingListUseCase`: Retorna lista de preparações aguardando

3. **Adapters (Adaptadores)**:
   - **Inbound**: REST API (FastAPI) e Listeners SQS (AWS)
   - **Outbound**: Repositórios (SQLAlchemy) e HTTP Client (httpx)

4. **Infrastructure (Infraestrutura)**:
   - Implementações concretas de tecnologias
   - ORM, configurações, factories de dependências

### Domain-Driven Design (DDD)

O domínio de preparação é modelado com:

**Entidades:**
- `Preparation`: Representa uma preparação com ciclo de vida próprio, incluindo posição na fila e tempo estimado

**Value Objects:**
- `PreparationStatus`: Estado da preparação (RECEIVED, IN_PREPARATION, READY, COMPLETED)
- `OrderInfo`: Informações do pedido associado à preparação

**Portas (Interfaces):**
- `PreparationRepository`: Persistência de preparações
- `OrderInfoProvider`: Integração com serviço de pedidos para obter informações

### Comunicação Assíncrona

O microsserviço utiliza **AWS SQS** para comunicação assíncrona:

#### Consumer SQS - Payment Closed

O serviço possui um **consumer** dedicado que escuta mensagens da fila `payment-closed.fifo`:

- **Fila**: `payment-closed.fifo` (SQS FIFO para garantir ordem)
- **Mensagem**: Contém o `payment_id` do pagamento confirmado
- **Processamento**:
  1. Recebe notificação de pagamento aprovado
  2. Busca informações do pedido via HTTP no serviço de pedidos
  3. Cria uma nova preparação com status `RECEIVED`
  4. Calcula tempo estimado de preparo
  5. Define posição na fila
- **Entrypoint**: `payment_closed_listener.py`

```python
# Estrutura da mensagem SQS
{
  "payment_id": "uuid-do-pagamento"
}
```

## Funcionalidades

### 1. Recebimento Automático de Preparações
- Escuta fila SQS para pagamentos confirmados
- Cria automaticamente preparações com status `RECEIVED`
- Calcula tempo estimado de preparo baseado no pedido

### 2. Gestão da Fila de Preparação
- Visualização da lista de espera de preparações
- Controle de posição na fila
- Organização por ordem de chegada

### 3. Controle de Status de Preparação
- **RECEIVED**: Preparação recebida e aguardando início
- **IN_PREPARATION**: Preparação em andamento na cozinha
- **READY**: Preparação pronta para retirada
- **COMPLETED**: Preparação entregue ao cliente

### 4. Operações de Preparação
- Iniciar próxima preparação da fila
- Marcar preparação como pronta
- Marcar preparação como completada/entregue
- Consultar lista de espera

### 5. Integração com Serviço de Pedidos
- Busca informações detalhadas do pedido via HTTP
- Obtém lista de produtos e tempo de preparo

## Tecnologias

### Core
- **Python 3.14**: Linguagem de programação
- **FastAPI**: Framework web moderno e assíncrono
- **Pydantic**: Validação de dados e settings
- **SQLAlchemy**: ORM assíncrono
- **Alembic**: Migrações de banco de dados

### Infraestrutura
- **PostgreSQL**: Banco de dados relacional
- **AWS SQS**: Fila de mensagens para comunicação assíncrona
- **Docker**: Containerização
- **Poetry**: Gerenciamento de dependências

### Integrações
- **aioboto3**: Cliente AWS assíncrono (SQS)
- **httpx**: Cliente HTTP assíncrono (comunicação com Order API)

### Desenvolvimento
- **pytest**: Framework de testes
- **pytest-cov**: Cobertura de testes
- **pytest-asyncio**: Suporte a testes assíncronos
- **pre-commit**: Hooks de qualidade de código
- **black**: Formatação de código
- **isort**: Organização de imports
- **flake8**: Linting
- **mypy**: Type checking

## Estrutura do Projeto

```
preparation-api/
├── preparation_api/           # Código fonte principal
│   ├── adapters/              # Adaptadores (REST, SQS)
│   │   └── inbound/
│   │       ├── rest/          # API REST endpoints
│   │       └── listeners/     # SQS consumers
│   ├── application/           # Casos de uso
│   │   ├── commands/          # DTOs de comando
│   │   └── use_cases/         # Lógica de aplicação
│   ├── domain/                # Lógica de negócio
│   │   ├── entities/          # Entidades
│   │   ├── ports/             # Interfaces
│   │   └── value_objects/     # Value objects
│   ├── entrypoints/           # Pontos de entrada
│   ├── infrastructure/        # Infraestrutura
│   │   ├── alembic/           # Migrações
│   │   └── orm/               # Models SQLAlchemy
├── tests/                     # Testes unitários e integração
│   ├── unit/
│   └── integration/
├── terraform/                 # Infraestrutura como código
├── docker-compose.yml         # Desenvolvimento local
├── Dockerfile                 # Imagem Docker
├── pyproject.toml             # Dependências Poetry
└── README.md                  # Este arquivo
```

## Configuração e Execução

### Pré-requisitos

- Docker e Docker Compose
- Python 3.14+ (para desenvolvimento local sem Docker)
- Poetry (para gerenciamento de dependências)
- AWS CLI configurado (para implantação)

### Variáveis de Ambiente

O projeto utiliza arquivos de configuração na pasta `settings/`:

#### `settings/app.env`
```bash
APP_TITLE="SOAT Tech Challenge Preparation Api"
APP_VERSION="1.0.0"
APP_ENVIRONMENT="PRD"
APP_ROOT_PATH="/"
```

#### `settings/database.env`
```bash
DATABASE_DSN="postgresql+asyncpg://user:password@host:5432/dbname"
DATABASE_ECHO=False
```

#### `settings/aws.env`
```bash
AWS_REGION_NAME="us-east-1"
AWS_ACCOUNT_ID="your-account-id"
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"
```

#### `settings/order_api.env`
```bash
ORDER_API_BASE_URL="http://order-api.service.local"
ORDER_API_TIMEOUT=10.0
```

#### `settings/payment_closed_listener.env`
```bash
PAYMENT_CLOSED_LISTENER_QUEUE_NAME="payment-closed.fifo"
PAYMENT_CLOSED_LISTENER_WAIT_TIME_SECONDS=5
PAYMENT_CLOSED_LISTENER_MAX_NUMBER_OF_MESSAGES_PER_BATCH=5
PAYMENT_CLOSED_LISTENER_VISIBILITY_TIMEOUT_SECONDS=60
```

### Execução Local com Docker Compose

1. **Clone o repositório**:
```bash
git clone https://github.com/SOAT-Tech-Challenge-2025/preparation-api.git
cd preparation-api
```

2. **Configure as variáveis de ambiente**:
```bash
# Copie os arquivos de exemplo
cp settings/app.env.example settings/app.env
cp settings/database.env.example settings/database.env
cp settings/aws.env.example settings/aws.env
cp settings/order_api.env.example settings/order_api.env
cp settings/payment_closed_listener.env.example settings/payment_closed_listener.env

# Configure os valores adequados em cada arquivo
```

3. **Configure o Docker Compose**:
```bash
cp .env.example .env
# Edite as portas se necessário
```

4. **Inicie os serviços**:
```bash
docker-compose up -d
```

5. **Verifique os logs**:
```bash
# API
docker-compose logs -f api

# Consumer SQS
docker-compose logs -f payment-closed-listener
```

6. **Execute as migrações do banco**:
```bash
docker-compose exec api alembic upgrade head
```

7. **Acesse a documentação da API**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Execução dos Serviços

O projeto possui dois serviços principais:

#### API REST
```bash
docker-compose up api
```
Expõe endpoints REST na porta 8000 (configurável via `PREPARATION_API_HTTP_PORT`)

#### Consumer SQS (Payment Closed Listener)
```bash
docker-compose up payment-closed-listener
```
Processa mensagens da fila `payment-closed.fifo`

## Testes

O projeto possui testes unitários e de integração com cobertura de código.

### Executar todos os testes
```bash
docker-compose exec api pytest
```

### Executar testes com cobertura
```bash
docker-compose exec api pytest --cov=preparation_api --cov-report=html
```

### Executar testes específicos
```bash
# Testes unitários
docker-compose exec api pytest tests/unit/

# Testes de integração
docker-compose exec api pytest tests/integration/

# Teste específico
docker-compose exec api pytest tests/unit/application/use_cases/test_start_next_preparation.py
```

### Visualizar relatório de cobertura
Após executar os testes com cobertura, abra o arquivo `htmlcov/index.html` no navegador.

## CI/CD

O projeto utiliza **GitHub Actions** para CI/CD automatizado:

### Pipeline de CI/CD (`.github/workflows/ci_cd.yml`)

1. **Test**:
   - Executa testes unitários e de integração
   - Gera relatório de cobertura
   - Roda em todas as branches

2. **Build**:
   - Constrói imagem Docker
   - Push para Amazon ECR (Public)
   - Apenas em push para branch `main`

3. **Deploy**:
   - Aplica configurações Terraform
   - Atualiza deployment no EKS
   - Atualiza ConfigMaps e Secrets
   - Apenas em push para branch `main`

### Pipeline de Destroy (`.github/workflows/destroy.yml`)

- Remove recursos da infraestrutura AWS
- Execução manual via workflow dispatch
- Útil para ambientes de teste

### Variáveis de CI/CD

Configuradas nos **Secrets** do GitHub:

- `AWS_ACCESS_KEY_ID`: Credencial AWS
- `AWS_SECRET_ACCESS_KEY`: Credencial AWS
- `AWS_REGION`: Região AWS (us-east-1)
- `TF_VAR_*`: Variáveis do Terraform

## Implantação na AWS

A infraestrutura é provisionada via **Terraform** na AWS:

### Recursos Criados

1. **Amazon EKS**:
   - Namespace: `preparation`
   - Deployment: `preparation-api` (API REST)
   - Deployment: `payment-closed-listener` (Consumer SQS)
   - Service: `preparation-service` (ClusterIP)
   - HPA: Auto-scaling baseado em CPU/memória

2. **Amazon RDS**:
   - PostgreSQL para persistência
   - Gerenciado pelo repositório [Database](https://github.com/SOAT-Tech-Challenge-2025/database)

3. **Amazon SQS**:
   - Fila FIFO `payment-closed.fifo`
   - Integração com serviço de pagamentos

4. **Amazon ECR**:
   - Repositório público para imagens Docker
   - `public.ecr.aws/p6c0d2v5/fiap-soat-techchallenge-preparation:latest`

5. **API Gateway**:
   - Roteamento de requisições para o serviço
   - Gerenciado pelo repositório [Infrastructure](https://github.com/SOAT-Tech-Challenge-2025/infrastructure)

### Deploy Manual

```bash
cd terraform

# Inicializar Terraform
terraform init -backend-config=backend.hcl

# Planejar mudanças
terraform plan

# Aplicar mudanças
terraform apply
```

## Endpoints da API

Base URL: `/api/v1/preparation`

### 1. Iniciar Próxima Preparação
```http
POST /api/v1/preparation/start-next
```

Inicia a preparação do próximo pedido na fila (status RECEIVED → IN_PREPARATION).

**Resposta de Sucesso (200)**:
```json
{
  "id": "uuid-da-preparacao",
  "preparation_position": null,
  "preparation_time": 15,
  "estimated_ready_time": "2025-12-04T10:30:00Z",
  "preparation_status": "IN_PREPARATION",
  "created_at": "2025-12-04T10:15:00Z",
  "timestamp": "2025-12-04T10:15:00Z"
}
```

**Erros**:
- `400`: Nenhuma preparação disponível na fila
- `500`: Erro interno do servidor

---

### 2. Marcar Preparação como Pronta
```http
POST /api/v1/preparation/{preparation_id}/ready
```

Marca uma preparação em andamento como pronta para retirada (IN_PREPARATION → READY).

**Parâmetros**:
- `preparation_id` (path): UUID da preparação

**Resposta de Sucesso (200)**:
```json
{
  "id": "uuid-da-preparacao",
  "preparation_position": null,
  "preparation_time": 15,
  "estimated_ready_time": "2025-12-04T10:30:00Z",
  "preparation_status": "READY",
  "created_at": "2025-12-04T10:15:00Z",
  "timestamp": "2025-12-04T10:30:00Z"
}
```

**Erros**:
- `400`: Preparação não está em andamento
- `404`: Preparação não encontrada
- `500`: Erro interno do servidor

---

### 3. Marcar Preparação como Completada
```http
POST /api/v1/preparation/{preparation_id}/complete
```

Marca uma preparação pronta como entregue ao cliente (READY → COMPLETED).

**Parâmetros**:
- `preparation_id` (path): UUID da preparação

**Resposta de Sucesso (200)**:
```json
{
  "id": "uuid-da-preparacao",
  "preparation_position": null,
  "preparation_time": 15,
  "estimated_ready_time": "2025-12-04T10:30:00Z",
  "preparation_status": "COMPLETED",
  "created_at": "2025-12-04T10:15:00Z",
  "timestamp": "2025-12-04T10:35:00Z"
}
```

**Erros**:
- `400`: Preparação não está pronta
- `404`: Preparação não encontrada
- `500`: Erro interno do servidor

---

### 4. Consultar Lista de Espera
```http
GET /api/v1/preparation/waiting-list
```

Retorna todas as preparações que estão aguardando ou em preparo.

**Resposta de Sucesso (200)**:
```json
{
  "items": [
    {
      "id": "uuid-preparacao-1",
      "preparation_position": null,
      "preparation_time": 15,
      "estimated_ready_time": "2025-12-04T10:30:00Z",
      "preparation_status": "IN_PREPARATION",
      "created_at": "2025-12-04T10:15:00Z",
      "timestamp": "2025-12-04T10:15:00Z"
    },
    {
      "id": "uuid-preparacao-2",
      "preparation_position": 1,
      "preparation_time": 20,
      "estimated_ready_time": null,
      "preparation_status": "RECEIVED",
      "created_at": "2025-12-04T10:20:00Z",
      "timestamp": "2025-12-04T10:20:00Z"
    }
  ]
}
```

**Erros**:
- `500`: Erro interno do servidor

---

### Status da Preparação

| Status | Descrição |
|--------|-----------|
| `RECEIVED` | Preparação recebida, aguardando início |
| `IN_PREPARATION` | Preparação em andamento na cozinha |
| `READY` | Preparação pronta para retirada |
| `COMPLETED` | Preparação entregue ao cliente |

### Fluxo de Estados

```
RECEIVED → IN_PREPARATION → READY → COMPLETED
```

## Licença

Este projeto está licenciado sob a **Apache License 2.0** - veja o arquivo [LICENSE](LICENSE) para detalhes.
