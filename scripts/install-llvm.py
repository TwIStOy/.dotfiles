#!/usr/bin/env python3

import os
from os.path import join
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'pythonx')))

from dotfiles import shell

LLVM_VERSION = "12.0.0"

if sys.platform == 'darwin':
  PLATFORM = 'apple-darwin'
elif sys.platform == 'linux':
  PLATFORM = 'linux-gnu-ubuntu-16.04'
else:
  print('NOT SUPPORTED')
  exit(1)


TAR_URL = f'https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.0/clang+llvm-{LLVM_VERSION}-x86_64-{PLATFORM}.tar.xz'
TAR_SIG_URL = f'https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.0/clang+llvm-{LLVM_VERSION}-x86_64-{PLATFORM}.tar.xz.sig'

llvm_path = os.path.join(os.path.expanduser(f'~/.local/share/llvm/{LLVM_VERSION}'))
llvm_installed_path = os.path.join(llvm_path, f'clang+llvm-{LLVM_VERSION}-x86_64-{PLATFORM}')

if os.path.exists(llvm_installed_path):
  if os.getenv('_DOTFILES_AUTOMATIC', 'NO') == 'YES':
    exit(0)
  prompt = f'It seems that LLVM {LLVM_VERSION} is already installed, reinstall? [y/N] '
  text = input(prompt)
  if text != 'y':
    print('Cancel')
    exit(0)

shell(['mkdir', '-p', llvm_path])
temp_folder , _, _ = shell(['mktemp', '-d', '/tmp/dotfiles-llvm-XXXXXXXX'], silence=True)
temp_folder = temp_folder.strip()

print(f'Download llvm package from {TAR_URL} to {temp_folder}')
print(f'Download {TAR_URL}')
shell(['curl', '-L', TAR_URL, '-#', '-o', os.path.join(temp_folder, 'llvm.tar.xz')])
print(f'Download {TAR_SIG_URL}')
shell(['curl', '-L', TAR_SIG_URL, '-#', '-o', os.path.join(temp_folder, 'llvm.tar.xz.sig')])

print(f'Unzip llvm package to {llvm_path}')
shell(['tar', 'xf', 'llvm.tar.xz', '--directory', llvm_path], cwd=temp_folder)

llvm_path_config_path = os.path.expanduser('~/.config/fish/conf.d/dotfiles-llvm-path.fish')
print(f'Dump llvm path to fish config: {llvm_path_config_path}')
with open(llvm_path_config_path, 'w') as fp:
  fp.write(f'set -gx DOTFILES_LLVM_PATH {llvm_installed_path}\n')

print('DONE!')

# vim: fdm=marker sw=2 ts=2
