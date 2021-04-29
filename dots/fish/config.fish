set fish_greeting

status is-interactive && nvm use lts
status is-interactive && zoxide init fish | source

set -Up fish_user_paths ~/.cargo/bin

