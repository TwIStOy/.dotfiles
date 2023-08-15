set fish_greeting

fish_add_path $HOME/.fnm
fish_add_path $HOME/.cargo/bin
fish_add_path /opt/homebrew/bin
fish_add_path /opt/homebrew/opt/ruby/bin
fish_add_path /opt/homebrew/lib/ruby/gems/3.2.0/bin/

status is-interactive && zoxide init fish | source
status is-interactive && starship init fish | source 

eval (fnm env)


