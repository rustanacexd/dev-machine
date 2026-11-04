syntax on
set tabstop=2
set shiftwidth=2
set expandtab
set ai
set number
set hlsearch
set ruler
highlight Comment ctermfg=green

autocmd FileType markdown syn region markdownItalic start="\*\S" end="\S\*" keepend
autocmd FileType markdown syn region markdownBold start="\*\*\S" end="\S\*\*" keepend
autocmd FileType markdown syntax match Normal "_" containedin=ALL

set clipboard=unnamed
