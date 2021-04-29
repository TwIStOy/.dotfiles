import os
import subprocess
import sys
from subprocess import DEVNULL, CalledProcessError, check_call
from typing import Any, Dict, List, Sequence, Union, Optional
from collections import namedtuple

sys.path.append(os.path.realpath(
  os.path.join(os.path.dirname(__file__), '..', '..', 'pythonx')))

import dotbot
from dotfiles import shell


class Git(dotbot.Plugin):
  _directive = 'git'

  path_vars = {
      'HOME': os.path.expanduser('~')
  }

  class Repository(object):
    def __init__(self, _context, _log, vars: Dict[str, Any]):
      self._context = _context
      self._log = _log

      self.url = vars['url']
      self.path = vars['path'].format(**Git.path_vars)
      self.method = vars.get('method', 'clone-or-pull')
      self.submodule = vars.get('sub_module', True)
      self.rev = vars.get('rev', 'master')
      self.post_commands = vars.get('post', [])

    def exists(self):
      if self.path is None:
        raise ValueError('Expect path not is None')
      return os.path.isdir(os.path.join(self.path, '.git'))

    def _clone_or_pull_cmd(self):
      if self.method == 'clone':
        method = 'clone'
        if self.exists():
          self._log.lowinfo(f"Repository already exists! Won't clone {self.url} to {self.path}")
          return method, []
      elif self.method == 'pull':
        method = 'pull'
        if self.exists():
          self._log.lowinfo(f"Repository doesn't exists! Won't pull {self.url} in {self.path}")
          return method, []
      elif self.method == 'clone-or-pull':
        if not self.exists():
          method = 'clone'
        else:
          method = 'pull'
      else:
        raise ValueError(f'Unexpect method: {self.method}')

      if method == 'clone':
        return method, ['git', 'clone', '--quiet', self.url, self.path]
      elif method == 'pull':
        return method, ['git', '--work-tree', self.path, '--git-dir',
                os.path.join(self.path, '.git'), 'pull', '--quiet']
      else:
        return method, []

    def _check_out_cmd(self) -> List[str]:
      return ['git', '--work-tree', self.path, '--git-dir',
              os.path.join(self.path, '.git'), 'checkout', '--quiet',
              '--force', self.rev]

    def _submodule_cmd(self) -> List[str]:
      if self.submodule:
        return ['git', 'submodule', '--quiet', 'update', '--init', '--recursive']
      return []

    def init(self) -> bool:
      m, cmd = self._clone_or_pull_cmd()
      if m == 'clone' and cmd:
        self._log.lowinfo(f'Cloning Repository from {self.url} into {self.path}')
      elif m == 'pull' and cmd:
        self._log.lowinfo(f'Pulling Repository from {self.url} into {self.path}')
      if cmd:
        _, _, rc = shell(cmd)
        if rc != 0:
          return False
      cmd = self._check_out_cmd()
      self._log.lowinfo(f'Checkout: {self.rev}')
      if cmd:
        _, _, rc = shell(cmd)
        if rc != 0:
          return False
      cmd = self._submodule_cmd()
      if self.submodule:
        self._log.lowinfo(f'Updating sub-modules')
      if cmd:
        _, _, rc = shell(cmd, cwd=self.path)
        if rc != 0:
          return False
      return True

  def can_handle(self, directive):
    return directive == self._directive

  def handle(self, directive: str, data: List[Dict]):
    if isinstance(data, list):
      for repo_var in data:
        repo = self.Repository(self._context, self._log, repo_var)
        self._log.info(f'Init or update repo {repo.path}({repo.url})')
        if not repo.init():
          return False
        for cmd in repo.post_commands:
          self._log.lowinfo(f'Post command: {cmd}')
          shell(cmd, shell=True, cwd=repo.path)
      return True
    else:
      return False

# vim: ts=2 et sw=2 ts=2
