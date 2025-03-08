#!/bin/bash
set -e

declare -- sharedir=/usr/local/share/md2ansi

if [[ -d "$sharedir" ]]; then
  echo "Directory '$sharedir' already exists."
  echo "This must be deleted first before executing git clone"
  read -r -p "Do you wish to delete this directory? y/n " yn
  [[ $yn == 'y' ]] || exit 1
  sudo rm -rf "$sharedir"
fi

sudo git clone -q https://github.com/Open-Technology-Foundation/md2ansi "$sharedir"

cd "$sharedir"
sudo chmod +x md2ansi.py md2ansi md

sudo ln -sf "$sharedir"/md2ansi /usr/local/bin/md2ansi
sudo ln -sf "$sharedir"/md /usr/local/bin/md

echo
echo "md2ansi has been installed."
echo "md2ansi --help for help"

#fin
