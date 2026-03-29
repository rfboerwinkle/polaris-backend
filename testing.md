This document is a draft that briefly outlines the testing that will occur across the entire project.

Note that since a large chunk of frontend feature testing is simulation testing (clicking buttons, creating a game, etc) a testing account and a testing account creation process is needed.

Each label is tied to a header in frontend.md (ex: FC \= “Frontend”, AC \= “Account”, and so on). The first number is just a way of numbering the tests, but the second number increases if the feature is tested very similarly or even in the same environment with the previous feature. Each bullet point is tied to one feature, and is in the same order as the feature it is testing for in frontend.md

# **Frontend**

* FR1.1 \- Open the web application on a desktop environment, and ensure that the layout of the display looks correctly aligned.  
  * Change the window size of the web application to also ensure all frontend interactables are appropriately adjusted.

# **Accounts**

* AC1.1 \- Ensure each account created has a proper username and password, and the account is stored properly.  
  * Utilize fuzz testing and/or unit testing to ensure invalid usernames and passwords are handled gracefully.  
  * Create a temporary account, and verify that the account can be successfully logged into after creation (and after signing out).  
* AC2.1 \- Within a testing account, navigate to the account profile and verify that previous games can be viewed.  
  * With a short game in the history, verify that the information about the game is accurate to what had occurred in the game.  
* AC2.2 \- Navigate to the account creation screen and verify that a blurb appears somewhere on the display about data collection.

# **Single Player Games**

* SP1.1 \- Without signing into an account, navigate to game creation and verify that you can create a single player game.  
* SP1.2 \- Within a single player game, change the number of bots and verify that you can start the game.  
  * Verify that the started game contains the correct amount of bots.  
* SP1.3 \- Within a single player game, change the difficulty of the bots.  
  * Unit testing will need to be used to verify each difficulty correctly identifies the algorithm used for the bot of that game.  
* SP2.1 \- Create a single player game and play through the round without any internet access.  
  * Verify the performance of the game (is it running slow? Do bots take a while to move?) as desktop environments should be able to handle playing a single player game with minimal resources needed.  
* SP3.1 \- With unit testing, assert that a finished single player game does not affect the testing account’s ELO.

# **Multiplayer Party Games**

* MP1.1 \- Go to multiplayer game creation and joining, and verify that the user cannot continue without being signed into an account.  
  * Additionally, ensure that users already signed into an account have no issues in proceeding using a test account.  
* MP2.1 \- In a testing account, go through the multiplayer game creation process and ensure that the player moves into a game lobby.  
* MP3.1 \-  Following MP1.2, a second testing account will be used to join the game.  
  * Test that the player can leave and rejoin the lobby before the game starts.  
  * If an account attempts to join multiple games at the same time, ensure that the account is kicked from all games except one.  
* MP3.2 \- Following MP1.3, pick a color and ensure that color stays the same for all users within the game.  
  * Test that if a user tries to pick a color that is already taken, they are unable to obtain it.  
* MP3.3 \- Following MP1.3, test on both accounts that either can add or remove bots to the game.  
* MP3.4 \- Following MP1.3, complete a match and check that the ELO of both testing accounts do not change.

# **Multiplayer Assigned Games**

* MA1.1 \- Go to multiplayer game creation and joining, and verify that the user cannot continue without being signed into an account.  
  * Additionally, ensure that users already signed into an account have no issues in proceeding using a test account.  
* MA2.1 \- Verify that the testing account can successfully join the game matchmaking cue and be placed into a game with other players.  
* MA3.1 \- After completing a game, verify that the testing account’s ELO was affected by the match outcome.
