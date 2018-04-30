Objective of the Code:

The .py files each contain a different bot strategy. Six of the bots are
multi-agent based strategies and three are central strategies. MyBot.py was the starting point for the
other strategies and was not included in the experiment. When designing the other, more complex bots, the team
tested against MyBot to ensure that the presumably better strategies would beat MyBot.


How to Run the Code: 

The team used the bash1.sh file to run the matches. In that file, four bots are specified 
and can be changed for each match. The script in the file runs ten games between those bots, adds up their
total scores, and outputs those scores to a file called regexText.txt. There, the winners are listed and the match
information is given.


A single game can be run as well using the run_game.bat file or run_game.sh file. Running those files will
produce am HLT file called "replay-someNumbers.hlt". The game can be visualized on the Halite website at the following
link: https://halite.io/play-programming-challenge#/replay-bot
Open the HLT file on that page and the game will be shown between the four bots listed in the run_game file.
