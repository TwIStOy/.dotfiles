#!/usr/bin/env fish

function generate-neovim-init
  set -l python3_path (command -v python3)
  set -l tmp_file (mktemp /tmp/init-XXXXXXXX.lua)

  echo "vim.api.nvim_command [[set runtimepath+=$HOME/.dotvim]]" > $tmp_file
  echo "vim.g.python3_host_prog = '$python3_path'" >> $tmp_file
  echo "vim.g.compiled_llvm_clang_directory = '$DOTFILES_LLVM_PATH'" >> $tmp_file
  echo "require('walnut.init')" >> $tmp_file

  mkdir -p ~/.config/nvim
  mv $tmp_file ~/.config/nvim/init.lua
end

generate-neovim-init

