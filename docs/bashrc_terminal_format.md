### Terminal Customization via .bashrc

```
RED="\[\033[0;31m\]"
GREEN="\[\033[0;32m\]"
YELLOW="\[\033[0;33m\]"
BLUE="\[\033[1;34m\]"
MAGENTA="\[\033[1;35m\]"
CYAN="\[\033[1;36m\]"
WHITE="\[\033[1;37m\]"
RESET="\[\033[0m\]"

# Git branch parser
parse_git_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null
}

# Prompt symbol changes on success/failure
PROMPT_SYMBOL_SUCCESS="${GREEN}✔${RESET}"
PROMPT_SYMBOL_ERROR="${RED}✖${RESET}"

# Set PS1
PS1="\${debian_chroot:+(\$debian_chroot)}"\
"${CYAN}\u${WHITE}@${MAGENTA}\h${RESET}:"\
"${BLUE}\w${RESET}"\
"${GREEN} \$(parse_git_branch)${RESET}"\
'\n'"\
\$(if [[ \$? == 0 ]]; then echo \"${PROMPT_SYMBOL_SUCCESS}\"; else echo \"${PROMPT_SYMBOL_ERROR}\"; fi) "\
"${YELLOW}\\$ ${RESET}"
```
