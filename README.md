![Not available](https://user-images.githubusercontent.com/33762/190890947-fae23b13-1149-4572-a967-46575b2031c0.png)

This is a small web-scraper that gives you info about followers and following on [Letterboxd](https://letterboxd.com/)
, namely:
- People that don't follow you back.
- Fans (people that **you** don't follow back).
- List of people that follow you.
- List of people you follow.

To run it, go to your Letterboxd user page and copy *exactly* the link above.\
Then, you can run the script in one of two ways:
- **With .exe file**: Run `main.exe` and enter the link in the prompt.
- **With CLI\terminal**: Type `python main.py <link>` in your favorite CLI.\
If you run with CLI, you need to install 'bs4', 'requests' and 'colorama' Python packages.