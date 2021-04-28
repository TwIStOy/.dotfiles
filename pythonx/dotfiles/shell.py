#!/usr/bin/which python3

import fcntl
import os
import errno
import subprocess
import select

def _make_async(fd):
  """
  Make fd non blocking
  """
  fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)


def _read_async(fd):
  try:
    return fd.read()
  except IOError as e:
    if e.errno != errno.EAGAIN:
      raise e

def shell(cmd, cwd=None, silence=None, shell=False, env=None):
  """
  Run command, output stderr and stdout
  """
  if shell is True:
    cmd = ' '.join(cmd)

  process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=shell, cwd=cwd, env=env)

  _make_async(process.stdout)
  _make_async(process.stderr)

  stdout = []
  stderr = []
  return_code = None

  while True:
    select.select([process.stdout, process.stderr], [], [])

    stdout_piece = _read_async(process.stdout)
    stderr_piece = _read_async(process.stderr)

    if stdout_piece and not silence:
      print(stdout_piece.decode(), end='')
    if stderr_piece and not silence:
      print(stderr_piece.decode(), end='')

    if stdout_piece:
      stdout.append(stdout_piece)
    if stderr_piece:
      stderr.append(stderr_piece)

    return_code = process.poll()
    if return_code is not None:
      stdout = ''.join([x.decode() for x in stdout])
      stderr = ''.join([x.decode() for x in stderr])
      return stdout, stderr, return_code


# vim: fdm=marker sw=2 ts=2
