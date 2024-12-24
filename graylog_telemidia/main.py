import os
import logging
import graypy
import json
import traceback
from datetime import datetime

class GraylogFilter(logging.Filter):
    """Classe de filtro para logging no Graylog."""
    
    def filter(self, record):
        """Sobrescreve o método de filtro para permitir todos os logs."""
        return True

class GraylogTelemidia:
    """Classe Singleton para logging no Graylog."""
    
    _instance = None

    def __new__(cls, graylog_config=None):
        """Cria uma nova instância de GraylogTelemidia ou retorna a existente."""
        if cls._instance is None:
            cls._instance = super(GraylogTelemidia, cls).__new__(cls)
            logger_config = cls.merge_configs(cls, graylog_config)
            cls.validate_config(logger_config)
            cls._instance.initialize_logger(logger_config)
        return cls._instance

    @staticmethod
    def merge_configs(self, graylog_config):
        """Mescla a configuração padrão com a configuração fornecida."""
        default_config = self.get_default_config()
        logger_config = {**default_config, **(graylog_config or {})}
        return self.process_config(logger_config)

    @staticmethod
    def get_default_config():
        """Recupera a configuração padrão a partir das variáveis de ambiente."""
        return {
            'server': os.getenv('GRAYLOG_SERVER'),
            'inputPort': os.getenv('GRAYLOG_INPUT_PORT'),
            'appName': os.getenv('GRAYLOG_APP_NAME'),
            'appVersion': os.getenv('GRAYLOG_APP_VERSION'),
            'environment': os.getenv('GRAYLOG_ENVIRONMENT'),
            'showConsole': os.getenv('GRAYLOG_SHOW_CONSOLE', True)
        }

    @staticmethod
    def process_config(logger_config):
        """Processa a configuração do logger."""
        logger_config['showConsole'] = logger_config.get('showConsole', True)
        if isinstance(logger_config['showConsole'], str):
            logger_config['showConsole'] = logger_config['showConsole'].lower() != 'false'
        logger_config['inputPort'] = int(logger_config['inputPort']) if isinstance(logger_config['inputPort'], str) else logger_config['inputPort']
        return logger_config

    @staticmethod
    def validate_config(config):
        """Valida o dicionário de configuração.
        
        Args:
            config (dict): O dicionário de configuração a ser validado.
        
        Raises:
            Exception: Se alguma chave obrigatória estiver faltando ou se o ambiente for inválido.
        """
        required_keys = ['server', 'inputPort', 'appName', 'appVersion', 'environment']
        
        # Verifica se as chaves obrigatórias estão presentes
        for key in required_keys:
            if key not in config or not config[key]:
                raise Exception(f"A configuração '{key}' é obrigatória.")
        
        allowed_environments = ['PROD', 'DEV', 'STAGING']
        
        # Verifica se o ambiente é válido
        if config['environment'] not in allowed_environments:
            raise Exception(
                f"A configuração 'environment' deve ser uma das seguintes: {', '.join(allowed_environments)}"
            )

    def initialize_logger(self, graylog_config):
        self.app_name = graylog_config['appName']
        self.app_version = graylog_config['appVersion']
        self.environment = graylog_config['environment']
        self.show_console = graylog_config['showConsole']

        # Armazena mensagens de erro e tracebacks
        self.error_messages = []
        self.trace_backs = []
        self.arguments = [] # Armazenamento global de argumentos

        """Inicializa o logger com a configuração fornecida do Graylog."""
        self.logger = logging.getLogger('graylog')
        self.logger.setLevel(logging.DEBUG)

        handler = graypy.GELFUDPHandler(graylog_config['server'], graylog_config['inputPort'], facility=self.app_name)
        handler.addFilter(GraylogFilter())
        self.logger.addHandler(handler)

    def __getattr__(self, name):
        """Redireciona o acesso a atributos para os métodos do logger."""
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(self.logger, name):
            return lambda *args: self.log(name, *args)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def log(self, level, *args):
        """Registra uma mensagem no nível especificado."""
        payload = self.prepare_payload(args)
        message = self.extract_message(args)

        if hasattr(self.logger, level):
            getattr(self.logger, level)(message, extra=payload)
        else:
            raise ValueError(f"Method '{level}' does not exist.")
        
        # Exibe detalhes do log no console se especificado
        if self.show_console:
            self.log_to_console(level, message, payload)
        
        return self.build_response_payload(level, message, payload)

    def extract_message(self, args):
        """Extrai a mensagem de log dos argumentos."""
        return str(args[0]) if args else "Nenhuma mensagem fornecida"

    def process_array(self, array):
        """Processa um array recursivamente, lidando com erros e exceções."""
        for key in list(array.keys()):
            value = array[key]
            if isinstance(value, dict):
                # Processa sub-arrays recursivamente
                self.process_array(value)
            elif isinstance(value, (Exception, BaseException)):
                # Lida com o erro e remove o índice
                self.handle_error(value)
                del array[key]

    def handle_array_argument(self, arg):
        """Lida com argumentos de array, processando-os e armazenando se não estiverem vazios."""
        self.process_array(arg)

        if arg:  # Se o array não estiver vazio após o processamento
            self.arguments.append(arg)

    def prepare_payload(self, args):
        """Prepara o payload para logging."""
        self.arguments = []  # Reseta os argumentos para cada chamada de log
        self.error_messages = []
        self.trace_backs = []

        for index, arg in enumerate(args):
            if index == 0 and not isinstance(arg, Exception):
                continue  # Ignora o primeiro parâmetro se não for uma mensagem de log

            if isinstance(arg, Exception):
                self.handle_error(arg)
                continue
            elif isinstance(arg, (dict, list)):
                self.handle_array_argument(arg)
            else:
                self.arguments.append(str(arg))

        return self.build_payload(self.arguments)

    def build_payload(self, arguments):
        """Constrói o payload para a entrada de log."""
        payload = {
            'app_language': 'Python',
            'facility': self.app_name,
            'app_version': self.app_version,
            'environment': self.environment
        }

        if self.error_messages:
            payload['error_message'] = self.format_error_messages(self.error_messages)
        if self.trace_backs:
            payload['error_stack'] = self.format_trace_backs(self.trace_backs, self.error_messages)
        if arguments:
            payload['extra_info'] = json.dumps(arguments, indent=4)

        return payload

    def format_error_messages(self, error_messages):
        """Formata mensagens de erro para logging."""
        return ' | '.join(f"[Error #{i + 1}]: {msg}" if len(error_messages) > 1 else msg for i, msg in enumerate(error_messages))

    def format_trace_backs(self, trace_backs, error_messages):
        """Formata tracebacks para logging."""
        return ''.join(
            f"[Traceback do erro #{i + 1} \"{error_messages[i]}\"]:\n{bt}\n" if len(trace_backs) > 1 else f"{bt}\n"
            for i, bt in enumerate(trace_backs)
        )
    
    def handle_error(self, exception):
        """Lida com o logging de exceções."""
        error_message = str(exception)
        _traceback = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        self.error_messages.append(error_message)
        self.trace_backs.append(_traceback)

    def build_response_payload(self, level, message, payload):
        """Constrói o payload de resposta para o log."""
        response_payload = {
            'timestamp': self.timestamp,
            'level': level,
            'message': message
        }
        response_payload.update(payload)
        return response_payload

    def log_to_console(self, level, message, payload):
        """Registra detalhes da mensagem no console."""
        console_message = f"========= GRAYLOG MESSAGE [{self.timestamp}]: =========\n"

        console_message += f"Application: {self.app_name} | Version: {self.app_version} | Environment: {self.environment}\n"

        console_message += f"[{level}] \"{message}\"\n"

        if 'error_message' in payload and payload['error_message']:
            console_message += f"Error message: \"{payload['error_message'].strip()}\"\n"

        if 'error_stack' in payload and payload['error_stack']:
            console_message += f"Traceback:\n{payload['error_stack'].strip()}\n"

        if 'extra_info' in payload and payload['extra_info']:
            console_message += f"Extra info:\n{payload['extra_info'].strip()}\n"

        console_message += '================= END OF GRAYLOG MESSAGE ================='
        print(console_message)