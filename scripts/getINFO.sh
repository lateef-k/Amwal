#!/bin/bash
if [ $# -eq 0 ]; then
  echo "No arguments provided"
  exit 1
fi

param=$1
outputDate="${param//\//_}"
# https://stackoverflow.com/questions/13210880/replace-one-substring-for-another-string-in-shell-script
# replace backslash with strings so I can actually save. ${argu/patt/replacement}, but need to escape / so \/, also need all occurrences so /\/

{
  http --body POST https://www.boursakuwait.com.kw/markets/bulletin_data/daily_bulletin/company_statistics.aspx/getData d=$1
} | {
  jq -r '.d' | jq '.aaData'
} > "boursa_${outputDate}.json"
#'.d' to get the d key, which gives us a string that's actually a json, so we treat it as a raw string with -r, removing the quotes at either end
#jq can then parse it, finally we select .aaData which actually has the table info.

