# graylog-telemidia-py

Uma abstração da biblioteca [**graypy**](https://github.com/severb/graypy).

# Índice
- [Sobre](#sobre)
- [Instalação](#instalação)
- [Inicialização](#inicialização)
- [Utilização](#utilização)
- [Métodos suportados](#métodos-suportados)
- [Campos do Graylog](#campos-do-graylog)
- [Configuração de alertas do Graylog](#configuração-de-alertas-do-graylog)
- [Licença](#licença)

## Sobre

Este pacote fornece uma interface simples e eficiente para enviar mensagens de log para o Graylog, seguindo o padrão utilizado pela Telemidia.

## Instalação

Para instalar a biblioteca, utilize o pip:

```bash
pip install graylog-telemidia
```

## Inicialização

Para inicializar a biblioteca, você deve configurar as informações do Graylog. Existem duas abordagens para realizar essa configuração:

### 1. Configuração via dicionário

Você pode configurar a biblioteca utilizando um dicionário. Veja um exemplo abaixo:

```python
from graylog_telemidia import GraylogTelemidia

GRAYLOG_CONFIG = {
    "server": "graylog.myserver.com", # Endereço do servidor Graylog (obrigatório)
    "inputPort": 12201, # Porta do input que receberá a mensagem (obrigatório)
    "appName": "my-app", # Nome exibido no campo "facility" do Graylog (obrigatório)
    "appVersion": "1.0.0", # Versão da aplicação (obrigatório)
    "environment": "PROD", # Ambiente da aplicação: "PROD", "DEV" ou "STAGING" (obrigatório)
    "showConsole": False # Define se o log será exibido no console da aplicação (opcional, padrão: True)
}

graylog = GraylogTelemidia(GRAYLOG_CONFIG)
```
### 2. Configuração via variáveis de ambiente

Como alternativa, você pode definir a configuração através de variáveis de ambiente. As respectivas variáveis são:

* GRAYLOG_SERVER
* GRAYLOG_INPUT_PORT
* GRAYLOG_APP_NAME
* GRAYLOG_APP_VERSION
* GRAYLOG_ENVIRONMENT
* GRAYLOG_SHOW_CONSOLE

Neste caso, o objeto pode ser inicializado sem a necessidade de passar um parâmetro de configuração:

```python
graylog = GraylogTelemidia()
```

As duas abordagens de configuração podem ser combinadas, de forma que os valores do parâmetro de configuração enviado terão preferência sobre os valores definidos através de variáveis de ambiente.

## Utilização

A biblioteca permite o envio de mensagens de log de forma simples e eficiente. Veja alguns exemplos de uso:

### Enviar uma mensagem simples

```python
graylog.error('Ocorreu um erro horrível!')
```

### Informações adicionais

Para enriquecer as mensagens de log, você pode adicionar informações adicionais. Isso é útil para fornecer contexto sobre o erro:

```python
user_info = {
    "isUserAuthenticated": True,
    "isUserAdmin": False,
}
graylog.error('Ocorreu um erro horrível!', user_info)
```

### Traceback

É possível registrar o traceback de erros ou exceções. Para isso, basta passar o objeto de erro:

```python
try:
    raise Exception('Ocorreu um erro horrível!')
except Exception as e:
    graylog.error(e)
```

Você também pode personalizar a mensagem do erro, mantendo a mensagem original visível no Graylog:

```python
try:
    raise Exception('Ocorreu um erro horrível!')
except Exception as e:
    graylog.error('Ocorreu um erro em foo bar', e)
```

### Combinação de informações

Também é possível enviar múltiplos parâmetros, permitindo um contexto mais detalhado:

```python
try:
    raise Exception('Ocorreu um erro horrível!')
except Exception as e:
    user_info = {
        "isUserAuthenticated": True,
        "isUserAdmin": False,
    }
    graylog.error('Ocorreu um erro em foo bar', e, user_info)
```

### Retorno

Os métodos retornam o payload com todas as informações que foram enviadas ao servidor Graylog.

## Métodos suportados

A biblioteca suporta diversos métodos para registrar logs, cada um correspondente a um nível de severidade no Graylog. Os métodos disponíveis são:

Método | Nível Graylog
--- | ---
critical | 2
error | 3
warning | 4
info | 6
debug | 7

## Campos do Graylog

Os campos enviados ao Graylog são os seguintes:

Campo | Descrição
--- | ---
app_language | linguagem de programação utilizada pela aplicação (Python)
app_version | versão da aplicação - configurada durante a inicialização
environment | ambiente de execução da aplicação - configurado durante a inicialização
error_message | mensagem(ns) de erro coletada(s) através dos parâmetros extras (exceptions)
error_stack | traceback(s) do(s) erro(s) coletado(s)
extra_info | JSON contendo informações adicionais, enviadas como parâmetros extras
facility | nome da aplicação - configurado durante a inicialização
level | nível de severidade do log
message | mensagem principal do log
source | hostname do servidor que gerou o log
timestamp | carimbo de data e hora do log

## Configuração de alertas do Graylog

Para otimizar os alertas dos logs recebidos por meio desta biblioteca, recomendamos a implementação de algumas configurações específicas em relação aos alertas do Graylog. [Clique aqui para visualizar as recomendações de configuração](https://github.com/telemidia-isp/graylog-telemidia-py/blob/main/docs/GraylogAlerts.md).

## Licença
Este projeto está licenciado sob a Licença MIT.