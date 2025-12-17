# API de Preparação - SOAT Tech Challenge

Este repositório contém o **microsserviço de preparação** desenvolvido como parte da pós-graduação em **Arquitetura de Software** da **FIAP**. Este serviço é responsável por gerenciar todo o fluxo de preparação de pedidos, desde o recebimento de notificações de pagamento confirmado até o controle da fila de preparação e finalização dos pedidos.

## 📌 Menu

- [Integrantes](#integrantes)
- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
  - [Arquitetura Hexagonal](#arquitetura-hexagonal)
  - [Domain-Driven Design (DDD)](#domain-driven-design-ddd)
  - [Comunicação Assíncrona](#comunicação-assíncrona)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração e Execução](#configuração-e-execução)
  - [Pré-requisitos](#pré-requisitos)
  - [Variáveis de Ambiente](#variáveis-de-ambiente)
  - [Build das Imagens](#build-das-imagens)
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

### Arquitetura Hexagonal

O projeto segue os princípios da **Arquitetura Hexagonal** (Ports and Adapters), organizando o código em camadas bem definidas com foco no domínio e isolamento de dependências externas:

```
preparation_api/
├── domain/                                      # Hexágono - Núcleo da aplicação
│   ├── entities/                                # Entidades de domínio (Preparation)
│   ├── value_objects/                           # Objetos de valor (PreparationStatus, OrderInfo)
│   └── ports/                                   # Todas as portas (interfaces do hexágono)
│       ├── preparation_repository.py            # Interface para persistência
│       └── order_info_provider.py               # Interface para obter informações de pedidos
│
├── application/                                 # Casos de uso e orquestração
│   ├── commands/                                # Comandos de entrada (DTOs)
│   └── use_cases/                               # Implementação dos casos de uso
│
├── adapters/                                    # Adaptadores (Ports & Adapters)
│   ├── inbound/                                 # Adaptadores condutores (driving)
│   │   ├── rest/                                # API REST (FastAPI)
│   │   └── listeners/                           # Consumer SQS (PaymentClosedListener)
│   └── outbound/                                # Adaptadores conduzidos (driven)
│       ├── sa_preparation_repository.py         # Implementação da porta PreparationRepository
│       └── http_order_info_provider.py          # Implementação da porta OrderInfoProvider
│
├── infrastructure/                              # Configurações e detalhes técnicos
│   ├── alembic/                                 # Migrations de banco de dados
│   ├── orm/                                     # Modelos SQLAlchemy
│   ├── config.py                                # Configurações da aplicação
│   └── factory.py                               # Injeção de dependências
│
└── entrypoints/                                 # Pontos de entrada da aplicação
    ├── api.py                                   # FastAPI application
    └── payment_closed_listener.py               # Consumer de eventos
```

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

O microsserviço se comunica de forma assíncrona com outros serviços através de **AWS SNS/SQS**:

**Consumo de Eventos (SQS):**
- **PaymentClosedEvent**: Recebe notificações de pagamentos confirmados para iniciar preparações

```
┌─────────────────┐     PaymentClosed       ┌───────────────────┐
│   Payment API   │─────────(SQS)──────────>│  Preparation API  │
└─────────────────┘                         └───────────────────┘
                                                      │
                                             Consulta via HTTP
                                                      │
                                                      v
                                            ┌───────────────────┐
                                            │ Shopping Cart API │
                                            └───────────────────┘
```

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

- **Python 3.14**: Linguagem de programação
- **Poetry**: Gerenciador de dependências e empacotamento
- **FastAPI**: Framework web assíncrono para REST API
- **Pydantic**: Validação de dados e serialização
- **SQLAlchemy + Asyncpg**: ORM assíncrono com PostgreSQL
- **Alembic**: Migrations de banco de dados
- **HTTPX**: Cliente HTTP assíncrono para Order API
- **AIOBoto3**: Cliente assíncrono AWS (SQS)
- **Pytest**: Framework de testes
- **Docker**: Containerização
- **Kubernetes**: Orquestração de containers
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD

## Estrutura do Projeto

```
preparation-api/
├── preparation_api/                 # Código fonte principal
│   ├── adapters/                    # Camada de adaptadores
│   ├── application/                 # Casos de uso
│   ├── domain/                      # Domínio do negócio
│   ├── entrypoints/                 # Pontos de entrada
│   └── infrastructure/              # Configurações e infra
│
├── tests/                           # Testes unitários e integração
│   ├── unit/                        # Testes unitários
│   └── integration/                 # Testes de integração
│
├── terraform/                       # Infrastructure as Code
│   ├── k8s_*.tf                     # Recursos Kubernetes
│   ├── data.tf                      # Data sources
│   ├── locals.tf                    # Variáveis locais
│   ├── providers.tf                 # Providers Terraform
│   └── vars.tf                      # Variáveis de entrada
│
├── docker-entrypoint/               # Scripts de inicialização
├── settings/                        # Arquivos de configuração
├── .github/workflows/               # Pipelines CI/CD
│   ├── ci_cd.yml                    # Pipeline principal
│   └── destroy.yml                  # Destruição de infraestrutura
│
├── Dockerfile                       # Multi-stage build
├── docker-compose.yml               # Desenvolvimento local
├── docker-compose.test.yml          # Ambiente de testes
├── pyproject.toml                   # Dependências Poetry
├── alembic.ini                      # Configuração Alembic
└── pytest.ini                       # Configuração Pytest
```

## Configuração e Execução

### Pré-requisitos

- Docker e Docker Compose
- Python 3.14+ (para desenvolvimento local sem Docker)
- Poetry (para gerenciamento de dependências)
- AWS CLI configurado (para implantação)

### Variáveis de Ambiente

O projeto utiliza múltiplos arquivos de configuração na pasta `settings/`. Crie os arquivos baseados nos exemplos (`.env.example`):

**settings/app.env**
```env
APP_TITLE="SOAT Tech Challenge Preparation Api"
APP_VERSION="1.0.0"
APP_ENVIRONMENT="PRD"
APP_ROOT_PATH="/"
```

**settings/database.env**
```env
DATABASE_DSN="postgresql+asyncpg://user:password@host:5432/dbname"
DATABASE_ECHO=False
```

**settings/aws.env**
```env
AWS_REGION_NAME="us-east-1"
AWS_ACCOUNT_ID="your-account-id"
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"
```

**settings/order_api.env**
```env
ORDER_API_BASE_URL="http://order-api.service.local"
ORDER_API_TIMEOUT=10.0
```

**settings/payment_closed_listener.env**
```env
PAYMENT_CLOSED_LISTENER_QUEUE_NAME="payment-closed.fifo"
PAYMENT_CLOSED_LISTENER_WAIT_TIME_SECONDS=5
PAYMENT_CLOSED_LISTENER_MAX_NUMBER_OF_MESSAGES_PER_BATCH=5
PAYMENT_CLOSED_LISTENER_VISIBILITY_TIMEOUT_SECONDS=60
```

### Build das Imagens

#### Desenvolvimento / Teste
```sh
docker build --target development -t preparation-api:dev .
```

#### Produção
```sh
docker build --target production -t preparation-api:latest .
```

### Execução Local com Docker Compose

1. **Configure as variáveis de ambiente**:
   ```sh
   cp docker-compose-env/app.env.example docker-compose-env/app.env
   cp docker-compose-env/database.env.example docker-compose-env/database.env
   ```

2. **Inicie os serviços**:
   ```sh
   docker compose up -d
   ```

3. **Execute as migrations**:
   ```sh
   docker compose exec api alembic upgrade head
   ```

4. **Acesse a API**:
   - API: http://localhost:8000
   - Documentação Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

5. **Pare os serviços**:
   ```sh
   docker compose down
   ```



## Testes

### Executar todos os testes
```sh
docker compose -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml exec api pytest
```

### Executar com cobertura
```sh
docker compose -f docker-compose.test.yml exec api pytest --cov=preparation_api --cov-report=html
```

### Estrutura de Testes

- **Testes Unitários** (`tests/unit/`): Testam componentes isoladamente
- **Testes de Integração** (`tests/integration/`): Testam integrações com banco de dados e APIs externas

## CI/CD

O projeto possui pipeline completa no **GitHub Actions** com as seguintes etapas:

### Pipeline Principal (ci_cd.yml)

1. **Test**: Execução de testes unitários e de integração
2. **SonarQube**: Análise de qualidade de código e cobertura
3. **Build and Push**: Build da imagem Docker e push para ECR público
4. **Deploy**: Implantação no Kubernetes via Terraform

**Trigger**: Push em qualquer branch ou manualmente

### Pipeline de Destruição (destroy.yml)

Permite destruir a infraestrutura de forma controlada.

**Trigger**: Manual (workflow_dispatch)

## Implantação na AWS

A infraestrutura é provisionada utilizando **Terraform** e implantada em **Amazon EKS**.

### Recursos Kubernetes

- **Namespace**: `tech-challenge-preparation-api`
- **Deployment**: `preparation-api-deployment` (API REST)
- **Deployment**: `payment-closed-listener-deployment` (Consumer SQS)
- **Service**: `preparation-api-service` (ClusterIP)
- **Ingress**: Roteamento via NGINX Ingress Controller
- **HPA**: Auto-scaling baseado em CPU e memória (1-3 replicas)
- **ConfigMap**: Configurações não sensíveis
- **Secret**: Credenciais e tokens

### Implantação Manual

1. **Configure backend do Terraform**:
   ```sh
   cd terraform
   cp backend.hcl.example backend.hcl
   # Edite backend.hcl com suas configurações
   ```

2. **Inicialize o Terraform**:
   ```sh
   terraform init -backend-config=backend.hcl
   ```

3. **Execute o plan**:
   ```sh
   terraform plan -var-file=terraform.tfvars
   ```

4. **Aplique as mudanças**:
   ```sh
   terraform apply -var-file=terraform.tfvars
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

Este projeto está licenciado sob a **Apache License 2.0**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

Desenvolvido para fins educacionais como parte da pós-graduação em Arquitetura de Software da FIAP.

---

**Documentação complementar**: Para entender o sistema completo, consulte os repositórios dos demais microsserviços listados na seção [Sobre o Projeto](#sobre-o-projeto).
