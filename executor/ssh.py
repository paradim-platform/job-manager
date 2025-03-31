from typing import Optional, Self

import paramiko
from paramiko.sftp_client import SFTPClient

from . import config


class SSHClient(paramiko.SSHClient):

    def __init__(self):
        super().__init__()
        self.is_ssh = False

        self.is_sftp = False
        self.sftp: Optional[paramiko.SFTPClient] = None

    def as_sftp(self):
        self.is_sftp = True
        return self

    def as_ssh(self):
        self.is_ssh = True
        return self

    def __enter__(self) -> Self | SFTPClient:
        if not self.is_ssh and not self.is_sftp:
            raise ValueError('You must use client.as_ssh() or client.as_sftp() to use the client as a context manager.')

        self.connect(
            hostname=config.SLURM_HOST_NAME,
            username=config.SLURM_USER_NAME,
            key_filename=config.SLURM_PRIVATE_KEYFILE
        )

        if self.is_sftp:
            self.sftp = self.open_sftp()
            return self.sftp

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_sftp:
            self.sftp.close()
            self.sftp = None
            self.is_sftp = False

        elif self.is_ssh:
            self.is_ssh = False

        self.close()


client = SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
