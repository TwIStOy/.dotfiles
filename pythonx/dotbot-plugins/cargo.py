import os
import subprocess
import sys
from subprocess import DEVNULL, CalledProcessError, check_call
from typing import Any, Dict, List, Sequence, Union

import dotbot


class Cargo(dotbot.Plugin):
  _directive = 'cargo'
  _cmd_tpl = 'cargo {toolchains} install --force {binary} {options}'
  # _cmd_tpl = ['cargo {toolchains} install --force {binary} {options}']

  def can_handle(self, directive):
    return directive == self._directive

  def handle(self, directive, data):
    if directive != self._directive:
      raise ValueError('Cargo cannot handle directive {}'.format(directive))
    for item in data:
      self._handle_item(item)
    return True

  def _handle_item(self, item):
    if isinstance(item, str):
      # simple binary name
      cmd = self._cmd_tpl.format(toolchains = '', binary = item, options = '')
      binary = item
      self._log.lowinfo(f'Installing rust binary {item} [{cmd}]')
    elif isinstance(item, dict):
      keys = list(item.keys())
      binary = keys[0]
      if len(keys) > 1:
        raise ValueError('DictItem should only contains one key, but got {}'.format(len(item)))
      options = []
      toolchains = ''
      for opt in item[binary]:
        if isinstance(opt, str):
          if opt.startswith('+'):
            toolchains = opt
          else:
            options.append('--{}'.format(opt))
        elif isinstance(opt, dict):
          for k in opt:
            options.append('--{} {}'.format(k, opt[k]))
      print(options)
      cmd = self._cmd_tpl.format(toolchains=toolchains, binary=binary, options=' '.join(options))
      self._log.lowinfo(f'Installing rust binary {binary} [{cmd}]')
    else:
      raise ValueError('Not supported')
    return self._run_cargo(binary, cmd)

  def _run_cargo(self, binary: str, cmd: str):
    with open(os.devnull, 'w') as devnull:
      r = subprocess.run(cmd, shell=True, stdin=devnull, stdout=devnull,
          stderr=subprocess.PIPE, cwd=self._context.base_directory())
      if r.returncode != 0:
        self._log.error(r.stderr.decode())
        self._log.warning('Rust binary {} could not be installed', binary)
        return False
      return True

# vim: ts=2 et sw=2 ts=2
