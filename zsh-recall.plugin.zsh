DIR="$( cd "$( dirname "$0" )" && pwd )"

recall () {
    PYTHONPATH="$DIR/lib/python3.7/site-packages/" \
        python3 "$DIR/recall.py" "$@"
    
    tput cnorm # show cursor
    if [[ -a "$HOME/.zsh_next_cmd" ]]; then
        CMD="$(cat $HOME/.zsh_next_cmd)"
        rm $HOME/.zsh_next_cmd
        print -z "$CMD"
    fi
}

alias rec="recall"
