#!/bin/bash

firstBot="LeftToRight.py"
secondBot="ShortBot.py"
thirdBot="WeakestPlanetBot.py"
fourthBot="LongBot.py"

rm regexText.txt
touch regexText.txt

for i in {1..10}
	do
		./halite -d "240 160" "python3 $firstBot" "python3 $secondBot" "python3 $thirdBot" "python3 $fourthBot" >> regexText.txt
	done

python3 regexParser.py $firstBot $secondBot $thirdBot $fourthBot
