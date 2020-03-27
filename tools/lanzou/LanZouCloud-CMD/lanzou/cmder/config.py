from pickle import load, dump
import os

__all__ = ['config']


class Config:

    def __init__(self):
        self._data = "%s/.lanzou" % os.getenv("HOME")
        self._config = {'cookie': None, 'path': './', 'max_size': 100, 'reader_mode': False}

        if os.path.isfile(self._data):
           with open(self._data, 'rb') as c:
              self._config = load(c)
#              print(self._config)
        else:
#           print("%s not exist!" %self._data)
           pass

    def _save(self):
        with open(self._data, 'wb') as c:
            dump(self._config, c)

    @property
    def cookie(self):
        return self._config.get('cookie')

    @cookie.setter
    def cookie(self, value):
        self._config['cookie'] = value
        self._save()

    @property
    def save_path(self):
        path = os.getenv('LANZOU_SAVE_PATH')
        if path is not None and os.path.exists(path):
           return path
        else:
           return self._config.get('path')

    @save_path.setter
    def save_path(self, value):
        self._config['path'] = value
        self._save()

    @property
    def max_size(self):
        return self._config.get('max_size')

    @max_size.setter
    def max_size(self, value):
        self._config['max_size'] = value
        self._save()

    @property
    def reader_mode(self):
        return self._config.get('reader_mode')

    @reader_mode.setter
    def reader_mode(self, value: bool):
        self._config['reader_mode'] = value
        self._save()


# 全局配置对象
config = Config()
