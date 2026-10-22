# Chat com busca semântica em PDF

Aplicação de linha de comando que consulta o conteúdo de um PDF usando embeddings, PostgreSQL com pgVector e um modelo Gemini. As respostas são geradas com base nos trechos encontrados no documento.

## Pré-requisitos

- Python 3
- Docker e Docker Compose
- Uma chave de API do Google AI

## Configuração

Na raiz do projeto, crie e ative um ambiente virtual e instale as dependências:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No Windows, ative o ambiente virtual com:

```powershell
venv\Scripts\Activate.ps1
```

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Preencha no `.env` as configurações utilizadas pela aplicação:

```env
GOOGLE_API_KEY=sua-chave-do-google
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documents
PDF_PATH=./document.pdf
```

O arquivo PDF definido em `PDF_PATH` deve existir no caminho informado. O nome do modelo de embeddings pode ser configurado em `GOOGLE_EMBEDDING_MODEL`; o modelo de chat pode ser configurado em `GOOGLE_LLM_MODEL`.

## Executar

1. Inicie o banco de dados:

   ```bash
   docker compose up -d
   ```

2. Inicie o chat:

   ```bash
   python src/chat.py
   ```

Na inicialização, o chat verifica se o PDF já foi ingerido. Se não houver documentos correspondentes no banco, ele executa a ingestão automaticamente. Se a quantidade de chunks armazenados for diferente da quantidade de chunks gerados a partir do PDF, ele executa a ingestão novamente.

Essa verificação compara a quantidade de chunks, não o conteúdo deles. Portanto, alterações no PDF que mantenham a mesma quantidade de chunks não são detectadas automaticamente.

Durante a ingestão, os chunks são enviados ao banco em lotes de cinco, com uma pausa de 3 segundos entre os lotes para ajudar a respeitar os limites de uso gratuito da API de embeddings. Se ocorrer um erro ao processar um lote, o script aguarda 15 segundos e tenta enviá-lo novamente.

Digite uma pergunta no terminal para consultar o PDF. Digite `sair` para encerrar o chat.

## Prompt usado na consulta

Para cada pergunta, a aplicação busca os 10 trechos mais relevantes no banco vetorial e envia o contexto recuperado e a pergunta ao modelo usando este prompt:

```text
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
```
