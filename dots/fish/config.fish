set fish_greeting

fish_add_path $HOME/.fnm
fish_add_path $HOME/.cargo/bin
fish_add_path /opt/homebrew/bin

status is-interactive && zoxide init fish | source
status is-interactive && starship init fish | source 

eval (fnm env)


