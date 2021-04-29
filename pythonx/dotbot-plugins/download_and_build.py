import os
import subprocess
import sys
from os.path import join, splitext
from subprocess import DEVNULL, CalledProcessError, check_call
from typing import Any, Dict, List, Sequence, Union

sys.path.append(os.path.realpath(
  os.path.join(os.path.dirname(__file__), '..', '..', 'pythonx')))

import dotbot
from dotfiles import shell


class DownloadAndBuild(dotbot.Plugin):
  _directive = 'self_build'

  DECOMPRESS_CMD = {
      'tar.xz': ['tar', 'xf'],
      'tar.gz': ['tar', 'xf'],
  }

  def can_handle(self, directive):
    return directive == self._directive

  def handle(self, directive, data):
    if directive != self._directive:
      raise ValueError('Can not handle')

    success = True
    for item in data:
      success &= self._process(item)
      if not success:
        break
    return success

  def _process(self, data: dict):
    if not isinstance(data, dict):
      raise ValueError('Data must be dict')
    _vars = data.get('vars', {})
    vars = {}
    for k, v in _vars.items():
      if isinstance(v, str):
        vars[k] = v
      elif isinstance(v, dict):
        vv = v.get(sys.platform)
        if vv:
          vars[k] = vv
    vars['HOME'] = os.path.expanduser('~')

    url = self._get_value(data, 'url').format(**vars)
    format = self._get_value(data, 'format').format(**vars)

    temp_folder = self._mk_temp_folder()

    self._log.lowinfo(f'Downloading package from {url} into {temp_folder}')
    _, _, rc = shell(['curl', '-L', url, '-#', '-o', os.path.join(temp_folder, f'package.{format}')])
    if rc != 0:
      return False

    decompress_cmd = data.get('decompress')
    if not decompress_cmd:
      decompress_cmd = self.DECOMPRESS_CMD[format]
    self._log.lowinfo(f'Decompressing package with {decompress_cmd}')
    _, _, rc = shell(decompress_cmd + [f'package.{format}'], cwd=temp_folder)
    if rc != 0:
      return False

    install_commands = data.get('install', [])
    for cmd in install_commands:
      _, _, rc = shell([x.format(**vars) for x in cmd], cwd=temp_folder, shell=True)
      if rc != 0:
        return False

    export_vars = data.get('export', {})
    if export_vars:
      for k,v in export_vars.items():
        with open(f'dotfiles-var-{k}.fish', 'w') as fp:
          fp.write(f'set -gx {k} {v}')

    return True

  def _get_value(self, data: dict, key: str) -> str:
    if key not in data:
      self._log.warning(f'Expect key {key} in {data} but not found')
      raise ValueError(f'Expect key {key} in {data} but not found')
    return data[key]

  def _mk_temp_folder(self) -> str:
    v, _, _ = shell(['mktemp', '-d', '/tmp/dotfiles-download-and-build-XXXXXXXX'], silence=True)
    return v.strip()

# vim: ts=2 sw=2
