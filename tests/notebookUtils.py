import json
import logging
import os
import pytest
import random
import requests_mock
import string
import tempfile

from notebookUtils import compressFolder, notebookSetup, saveFile, saveFolder, \
    scriptPostSave, updateApiTimestamp, _get_internal_save_url

def generate_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

class TestNotebookUtils():

    def test_notebookSetup(self):
        os.environ['PASSWORD'] = 'token'
        os.environ['HOSTNAME'] = 'host'
        os.environ['ROOT_DIR'] = '/data'
        c = type('', (), {})()
        c.ServerApp = type('', (), {})()
        c.Session = type('', (), {})()
        c.FileContentsManager = type('', (), {})()

        notebookSetup(c)

        assert c.ServerApp.ip == 'host'
        assert c.ServerApp.port == 8888
        assert c.ServerApp.root_dir == '/data/'
        assert c.ServerApp.allow_root is True
        assert c.ServerApp.token == 'token'
        assert c.ServerApp.base_url == '/data'
        assert c.FileContentsManager.post_save_hook
        with pytest.raises(AttributeError) as attribute_error:
            assert c.ServerApp.password
        assert "object has no attribute 'password'" in str(attribute_error.value)

    def test_scriptPostSave(self):
        """Test that scriptPostSave calls the internal save endpoint."""
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'

            autosaveMock = m.post('http://dataloader/data-loader-api/internal/save', json={'status': 'ok'})

            contentsManager = type('', (), {})()
            contentsManager.log = logging
            scriptPostSave({'type': 'notebook'}, '/data/notebook.ipynb', contentsManager)

            assert autosaveMock.call_count == 1
            request_json = json.loads(autosaveMock.last_request.text)
            assert request_json['file_path'] == '/data/notebook.ipynb'

    def test_scriptPostSave_skipsNonNotebook(self):
        """Test that scriptPostSave skips non-notebook files."""
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'

            autosaveMock = m.post('http://dataloader/data-loader-api/internal/save', json={'status': 'ok'})

            contentsManager = type('', (), {})()
            contentsManager.log = logging
            scriptPostSave({'type': 'file'}, '/data/script.py', contentsManager)

            assert autosaveMock.call_count == 0

    def test_scriptPostSave_handlesError(self):
        """Test that scriptPostSave handles errors gracefully."""
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'

            autosaveMock = m.post('http://dataloader/data-loader-api/internal/save', status_code=500)

            contentsManager = type('', (), {})()
            contentsManager.log = logging
            # Should not raise, just log the error
            scriptPostSave({'type': 'notebook'}, '/data/notebook.ipynb', contentsManager)

            assert autosaveMock.call_count == 1

    def test_get_internal_save_url_with_env(self):
        """Test URL construction with DATA_LOADER_API_URL set."""
        os.environ['DATA_LOADER_API_URL'] = 'custom-api-host'
        url = _get_internal_save_url()
        assert url == 'http://custom-api-host/data-loader-api/internal/save'

    def test_get_internal_save_url_default(self):
        """Test URL construction with default value."""
        if 'DATA_LOADER_API_URL' in os.environ:
            del os.environ['DATA_LOADER_API_URL']
        url = _get_internal_save_url()
        assert url == 'http://data-loader-api/data-loader-api/internal/save'

    def test_updateApiTimestamp(self):
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'
            url = 'http://dataloader/data-loader-api/internal/activity'
            dataLoaderActivityMock = m.post(url, json={'result': 'ok'})

            updateApiTimestamp('123', logging)

            assert dataLoaderActivityMock.call_count == 1

    def test_saveFile(self):
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'
            dataLoaderMock = m.post('http://dataloader/data-loader-api/internal/save', json={'result': 'ok'})

            saveFile('/file/path', '123', logging)

            assert dataLoaderMock.call_count == 1
            response = json.loads(dataLoaderMock.last_request.text)
            assert 'file' in response
            assert 'source' in response['file']
            assert response['file']['source'].startswith('../')
            assert 'tags' in response['file']
            assert 'autosave' in response['file']['tags']
            assert 'sandbox-123' in response['file']['tags']

    def test_compressFolder(self):
        folder_prepare = tempfile.mkdtemp() + '/.git'
        os.mkdir(folder_prepare)
        f = open(folder_prepare + '/file.txt', 'a')
        f.write('content')
        f.close()

        gzip_file = compressFolder(folder_prepare)
        folder_result = tempfile.mkdtemp()
        os.system(f'tar xzf {gzip_file} -C {folder_result}')
        assert '.git' in os.listdir(folder_result)
        assert 'file.txt' in os.listdir(f'{folder_result}/.git')

    def test_saveFolder(self):
        with requests_mock.Mocker() as m:
            os.environ['DATA_LOADER_API_URL'] = 'dataloader'
            dataLoaderMock = m.post('http://dataloader/data-loader-api/internal/save', json={'result': 'ok'})

            folder_prepare = tempfile.mkdtemp() + '/.git'
            os.mkdir(folder_prepare)
            f = open(folder_prepare + '/file.txt', 'a')
            f.write('content')
            f.close()
            saveFolder(folder_prepare, '123', logging)

            assert dataLoaderMock.call_count == 1
            response = json.loads(dataLoaderMock.last_request.text)
            assert 'file' in response
            assert 'source' in response['file']
            assert response['file']['source'].startswith('../')
            assert 'tags' in response['file']
            assert 'autosave' in response['file']['tags']
            assert 'sandbox-123' in response['file']['tags']
            assert 'git' in response['file']['tags']
