![Not available](https://user-images.githubusercontent.com/33762/190890947-fae23b13-1149-4572-a967-46575b2031c0.png)
### This is a small web-scraping and web-automation tool for [Letterboxd](https://letterboxd.com), written in Python3

Utilising BeautifulSoup for web-scraping and Selenium for web-automation;  
this script gives you info about your followers\following, and allows you to automatically unfollow the ~~bastards~~ users who don't follow back.

Namely, the subsequent stats are shown:
- Users that don't follow you back.
- Fans (users that **you** don't follow back).
- List of users that follow you.
- List of users you follow.<br><br>

To run it, go to your Letterboxd user page and copy *exactly* the link above.  
Then, you can run the script in one of two ways:
- **With .exe file**: Run `main.exe` and enter the link in the prompt.
- **With CLI\terminal**: Type `python main.py <link>` in your favorite CLI.

After the stats are shown, you can use the automation tool to unfollow back.  
For that you'll need to input username and password in order to login.  
**Those are not saved anywhere, and are used solely by the script.**

Lastly, let the automation tool run for several minutes, and you're all done :D