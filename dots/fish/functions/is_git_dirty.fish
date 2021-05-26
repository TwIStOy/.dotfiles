function is_git_dirty
  is_git; and test -z "(git status --porcelain)"
end

