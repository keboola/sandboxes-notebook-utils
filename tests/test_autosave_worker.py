import os
import pytest
import sys
from unittest.mock import patch, MagicMock


class TestAutosaveWorker:

    def test_missing_file_path_argument(self):
        """Test that missing --file-path argument causes exit"""
        with patch.object(sys, 'argv', ['autosave_worker']):
            with pytest.raises(SystemExit) as exc_info:
                from autosave_worker import main
                main()
            assert exc_info.value.code == 2  # argparse exits with 2 for missing required args

    def test_missing_sandbox_id_env_var(self):
        """Test that missing SANDBOX_ID env var causes exit"""
        env = {}
        with patch.dict(os.environ, env, clear=True):
            with patch.object(sys, 'argv', ['autosave_worker', '--file-path=/data/notebook.ipynb']):
                with pytest.raises(SystemExit) as exc_info:
                    from autosave_worker import main
                    main()
                assert exc_info.value.code == 1

    def test_persistent_storage_enabled_skips_file_operations(self):
        """Test that HAS_PERSISTENT_STORAGE=true only calls updateApiTimestamp"""
        env = {
            'SANDBOX_ID': 'test-sandbox',
            'HAS_PERSISTENT_STORAGE': 'true',
            'DATA_LOADER_API_URL': 'dataloader',
        }

        mock_update = MagicMock()
        mock_save_file = MagicMock()
        mock_save_folder = MagicMock()

        with patch.dict(os.environ, env, clear=True):
            with patch.object(sys, 'argv', ['autosave_worker', '--file-path=/data/notebook.ipynb']):
                with patch('autosave_worker.updateApiTimestamp', mock_update):
                    with patch('autosave_worker.saveFile', mock_save_file):
                        with patch('autosave_worker.saveFolder', mock_save_folder):
                            from autosave_worker import main
                            main()

        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == 'test-sandbox'
        mock_save_file.assert_not_called()
        mock_save_folder.assert_not_called()

    def test_persistent_storage_disabled_calls_all_functions(self):
        """Test that HAS_PERSISTENT_STORAGE=false calls all save functions"""
        env = {
            'SANDBOX_ID': 'test-sandbox',
            'HAS_PERSISTENT_STORAGE': 'false',
            'DATA_LOADER_API_URL': 'dataloader',
        }

        mock_update = MagicMock()
        mock_save_file = MagicMock()
        mock_save_folder = MagicMock()

        with patch.dict(os.environ, env, clear=True):
            with patch.object(sys, 'argv', ['autosave_worker', '--file-path=/data/notebook.ipynb']):
                with patch('autosave_worker.updateApiTimestamp', mock_update):
                    with patch('autosave_worker.saveFile', mock_save_file):
                        with patch('autosave_worker.saveFolder', mock_save_folder):
                            from autosave_worker import main
                            main()

        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == 'test-sandbox'

        mock_save_file.assert_called_once()
        assert mock_save_file.call_args[0][0] == '/data/notebook.ipynb'
        assert mock_save_file.call_args[0][1] == 'test-sandbox'

        mock_save_folder.assert_called_once()
        assert mock_save_folder.call_args[0][0] == '/data/.git'
        assert mock_save_folder.call_args[0][1] == 'test-sandbox'

    def test_no_persistent_storage_env_defaults_to_false(self):
        """Test that missing HAS_PERSISTENT_STORAGE defaults to false (calls all functions)"""
        env = {
            'SANDBOX_ID': 'test-sandbox',
            'DATA_LOADER_API_URL': 'dataloader',
        }

        mock_update = MagicMock()
        mock_save_file = MagicMock()
        mock_save_folder = MagicMock()

        with patch.dict(os.environ, env, clear=True):
            with patch.object(sys, 'argv', ['autosave_worker', '--file-path=/data/notebook.ipynb']):
                with patch('autosave_worker.updateApiTimestamp', mock_update):
                    with patch('autosave_worker.saveFile', mock_save_file):
                        with patch('autosave_worker.saveFolder', mock_save_folder):
                            from autosave_worker import main
                            main()

        mock_update.assert_called_once()
        mock_save_file.assert_called_once()
        mock_save_folder.assert_called_once()
