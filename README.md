# REALHYPE OS — Dashboard MVP Gratuito

Painel operacional gratuito para controlar **stock, leads, mensagens, vendas, CTT e financeiro** da RealHype.

## Estrutura gratuita recomendada

- **GitHub**: guardar o código.
- **Streamlit Community Cloud**: hospedar o dashboard.
- **Neon Postgres Free**: banco de dados online para acesso dos sócios e SDR em dispositivos diferentes.

## 1. Criar repositório no GitHub

1. Crie um repositório chamado `realhype-dashboard`.
2. Envie estes arquivos para o repositório:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `.streamlit/config.toml`
   - `.streamlit/secrets.toml.example`
   - `schema.sql`

> Não envie `.streamlit/secrets.toml` com senha real para o GitHub.

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
3. Escolha o repositório `realhype-dashboard`.
4. Main file path: `app.py`.
5. Antes de publicar, abra **Advanced settings > Secrets**.
6. Cole o conteúdo abaixo, trocando URL e senhas:

```toml
[database]
url = "postgresql://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require"

[users.socio1]
password = "trocar-senha-socio-1"
role = "partner"
name = "Sócio 1"

[users.socio2]
password = "trocar-senha-socio-2"
role = "partner"
name = "Sócio 2"

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

- Sócio 1: visão completa.
- Sócio 2: visão completa.
- SDR: cadastro de leads, mensagens, vendas e stock.

Quando alguém grava um dado, ele vai para o banco Neon. Outros dispositivos veem a atualização ao clicar em **Atualizar agora** ou ao trocar de página.

## 5. Como rodar localmente

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode:

```bash
streamlit run app.py
```

Sem secrets configuradas, o app usa banco local SQLite `realhype_local.db` e usuários de teste:

- usuário: `socio1`, senha: `realhype123`
- usuário: `socio2`, senha: `realhype123`
- usuário: `sdr`, senha: `realhype123`

Troque as senhas antes de publicar.

## 6. Próximas melhorias

- Login mais forte com senha criptografada.
- Histórico completo por cliente.
- Página de encomendas CTT com status detalhado.
- Upload de imagem do produto.
- Automação futura com Instagram/WhatsApp oficial.
