#!/usr/bin/env python3
"""
Standalone autosave worker script.
Called by data-loader-api with environment variables set.

Usage:
    python -m keboola_notebook_utils.autosave_worker --file-path=/data/notebook.ipynb

Required env vars:
    - SANDBOX_ID: Sandbox identifier
    - DATA_LOADER_API_URL: API base URL (optional, defaults to data-loader-api)
    - HAS_PERSISTENT_STORAGE: If 'true', skip file upload
"""
import argparse
import logging
import os
import sys

try:
    from .notebookUtils import saveFile, saveFolder, updateApiTimestamp
except ImportError:
    from notebookUtils import saveFile, saveFolder, updateApiTimestamp


def main():
    parser = argparse.ArgumentParser(description='Autosave worker for Keboola sandboxes')
    parser.add_argument('--file-path', required=True, help='Path to the notebook file to save')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    log = logging.getLogger('autosave')

    sandbox_id = os.environ.get('SANDBOX_ID')
    if not sandbox_id:
        log.error('SANDBOX_ID environment variable is required')
        sys.exit(1)

    log.info(f'Starting autosave for sandbox {sandbox_id}, file: {args.file_path}')

    updateApiTimestamp(sandbox_id, log)

    has_persistent_storage = os.getenv('HAS_PERSISTENT_STORAGE', 'False').lower() in ('true', '1')
    if not has_persistent_storage:
        saveFile(args.file_path, sandbox_id, log)
        saveFolder('/data/.git', sandbox_id, log)

    log.info('Autosave completed successfully')


if __name__ == '__main__':
    main()
