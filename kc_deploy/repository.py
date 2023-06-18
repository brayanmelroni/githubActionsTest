from abc import ABC, abstractmethod
import json
import glob
import requests


class IllegalArgumentError(ValueError):
    pass

class NoConfigsError(FileNotFoundError):
    pass

'''self referring to instance attributes'''

class Repository(ABC):
    """ Abstract base class for a repository of kafka-connect connector configs."""
    @abstractmethod
    def all(self):
        raise NotImplementedError

def read_json_file(path: str):
    with open(path) as f:
        data = json.load(f)
    return data

class FileRepository(Repository):
    """Local file based repository of kafka-connect connector configs."""
    def __init__(self, path: str, read_file=read_json_file):
        self.read_file = read_file
        self.path = path
        self._self_get_paths()

    def _self_get_paths(self):
        paths = glob.glob(f'{self.path}/**/*.json', recursive=True)
        print("loading configs from files: {}".format(", ".join(paths)))
        if not paths:
            raise NoConfigsError
        self.app_json_paths = paths

    def all(self):
        return [self.read_file(p) for p in self.app_json_paths]

class KafkaConnectRepository(Repository):
    """kafka connect api based repository of kafka-connect connector configs."""
    def __init__(self, host: str, port: str, requests=requests):
        self.base_url = f'http://{host}:{port}'
        self.requests = requests

    def __get_json(self, url: str):
        r = self.requests.get(url)
        r.raise_for_status()
        return r.json()
    
    def all(self):
        connectors = self.__get_json(f'{self.base_url}/connectors')                 # ['Test', 'FileStreamSourceConnector']
        connector_urls = [f'{self.base_url}/connectors/{id}' for id in connectors]
        return [self.__get_json(url) for url in connector_urls]
    
def get_repository(host: str = None, port: str = None, path: str=None):
    """Factory method for repositories."""
    if host is not None and port is not None and path is not None:
        raise IllegalArgumentError('host, port and paths cannot all be None')

    if host is not None and port is not None:
        return KafkaConnectRepository(host, port)

    if path is not None:
        # print(read_json_file("/Users/brayanmelroni.gajamu/Documents/githubActionsTest/connectors/snowflake-sink/F1_name_changed_changed_c1_c2.json"))
        # x = FileRepository(path)
        return FileRepository(path)

    raise IllegalArgumentError('bad argument combination.')