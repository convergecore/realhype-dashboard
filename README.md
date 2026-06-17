# REALHYPE OS â€” Dashboard MVP Gratuito

Painel operacional gratuito para controlar **stock, leads, mensagens, vendas, CTT e financeiro** da RealHype.

## Estrutura gratuita recomendada

- **GitHub**: guardar o cÃ³digo.
- **Streamlit Community Cloud**: hospedar o dashboard.
- **Neon Postgres Free**: banco de dados online para acesso dos sÃ³cios e SDR em dispositivos diferentes.

## 1. Criar repositÃ³rio no GitHub

1. Crie um repositÃ³rio chamado `realhype-dashboard`.
2. Envie estes arquivos para o repositÃ³rio:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `.streamlit/config.toml`
   - `.streamlit/secrets.toml.example`
   - `runtime.txt`
   - `schema.sql`

> NÃ£o envie `.streamlit/secrets.toml` com senha real para o GitHub.

## 2. Criar banco gratuito no Neon

1. Crie uma conta em Neon.
2. Crie um projeto Postgres.
3. Copie a connection string do banco.
4. Ela deve parecer com:

```txt
postgresql://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require
```

## 3. Publicar no Streamlit Community Cloud

1. Entre no Streamlit Community Cloud.
2. Clique em **New app**.
3. Escolha o repositÃ³rio `realhype-dashboard`.
4. Main file path: `app.py`.
5. Antes de publicar, abra **Advanced settings > Secrets**.
6. Cole o conteÃºdo abaixo, trocando URL e senhas:

```toml
[database]
url = "postgresql://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require"

[users.socio1]
password = "trocar-senha-socio-1"
role = "partner"
name = "SÃ³cio 1"

[users.socio2]
password = "trocar-senha-socio-2"
role = "partner"
name = "SÃ³cio 2"

[users.sdr]
password = "trocar-senha-sdr"
role = "sdr"
name = "SDR"
```

7. Clique em **Deploy**.

## 4. Acesso em tempo real

Depois de publicado, o Streamlit gera um link parecido com:

```txt
https://realhype-dashboard.streamlit.app
```

Todos acessam pelo mesmo link:

- SÃ³cio 1: visÃ£o completa.
- SÃ³cio 2: visÃ£o completa.
- SDR: cadastro de leads, mensagens, vendas e stock.

Quando alguÃ©m grava um dado, ele vai para o banco Neon. Outros dispositivos veem a atualizaÃ§Ã£o ao clicar em **Atualizar agora** ou ao trocar de pÃ¡gina.

## 5. Como rodar localmente

Instale as dependÃªncias:

```bash
pip install -r requirements.txt
```

Rode:

```bash
streamlit run app.py
```

Sem secrets configuradas, o app usa banco local SQLite `realhype_local.db`, mas o login exige usuarios definidos em Secrets.

Para rodar localmente, crie `.streamlit/secrets.toml` a partir de `.streamlit/secrets.toml.example` e defina senhas fora do Git.

## 6. PrÃ³ximas melhorias

- Login mais forte com senha criptografada.
- HistÃ³rico completo por cliente.
- PÃ¡gina de encomendas CTT com status detalhado.
- Upload de imagem do produto.
- AutomaÃ§Ã£o futura com Instagram/WhatsApp oficial.
