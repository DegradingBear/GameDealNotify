This program webscrapes the prices of games from isthereanydeal.com, it uses the gained prices and compares them to the 'desired prices' of games in a database
that can be edited by the user. the user can add, remove and update games and the prices they want for games and when the game goes on sale, the program
will use pushovers api to send a notification to the users phone

Note:
 - for this program to work, you will have to put both you api key and user key from pushover.
 - the api key can be obtained by registering your 'project' on the pushover website
 - the user key can be obtained by downloading the pushover app on the phone that you wish to get the notifications on, the key will be in the app
 
 extra note:
  - this project is at its fullest when you create a .exe file that runs the autoCheck.CheckPrices function and add this file to your windows computers startup folder
    this will make the program check and send notifications of sales everytime the computer boots up, without you having to open the gui and press the notify button
