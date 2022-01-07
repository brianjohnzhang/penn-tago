# penn-tago
An AI for playing Pentago, for CIS 519 in Spring 2018 at the University of Pennsylvania. Developed with Miranda Cravetz ([@mcravetz](https://github.com/mcravetz)). 

In late 2017, [AlphaGo Zero's release](https://www.nature.com/articles/nature24270) marked a culmination of efforts in machine learning to compete with humans in strategic thinking for board games. As students being newly introduced to ML, we decided to follow these footsteps with the game of Pentago, a variation on Connect 4 with a shifting board and goal of 5 instead of a 4. While more complex than Connect 4, Pentago was already a [strongly solved game](https://perfect-pentago.net/details.html) for us to compare and learn from for the creation of a neural network-based solution.

We implemented Monte Carlo tree search with neural networks, patterning off of [Alpha Go](https://www.nature.com/articles/nature16961). Our solution learned, evidenced by increasingly high win rates against a random player. Unfortunately, we ran out of time to complete the interface for a human player comparison!

Apologies in advance for a lack of proper formatting and comments - I learned Python through this course, which was probably not optimal. 
