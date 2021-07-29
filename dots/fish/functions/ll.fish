function ll --wraps=ls --wraps='exa -l' --wraps='exa -l --icons -a --group-directories-first --git' --description 'alias ll=exa -l --icons -a --group-directories-first --git'
  exa -l --icons -a --group-directories-first --git $argv; 
end
