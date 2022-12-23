#!/bin/sh
cp assembler.py myAssembler.py
chmod +x myAssembler.py

mv myAssembler.py myAssembler

mkdir -p ~/bin

cp myAssembler ~/bin

# export PATH=$PATH":$HOME/bin"