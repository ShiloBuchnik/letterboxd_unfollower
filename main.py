from bs4 import BeautifulSoup # For searching in HTML file
import requests # For requesting HTML file
import re # For regex
import sys
from colorama import Fore # For coloring output text
import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

# Prints 'amount_per_line' names per line, then prints a newline and so on
def printFormattedList(arg_list, amount_per_line):
	for i in range(0, len(arg_list), amount_per_line):
		names_to_print = arg_list[i: i + amount_per_line]
		print(*names_to_print, sep=", ")

def verifyURL():
	try:  # For running through the CLI
		url = sys.argv[1]
	except IndexError:  # For running through the .exe
		url = input("Please enter your Letterboxd user URL: ")

	# Demanding a valid letterboxd user link. '^' means match from start, '$' means match from end
	if not re.search(r'^https://letterboxd.com/\w+/$', url):
		input(Fore.RED + "Invalid address, terminating..." + Fore.RESET)
		exit(-1)

	return url

# Get all followers or following, depend on 3rd argument
def getAllUsers(session, url, follower_following):
	i = 1
	users_list = []
	# We iterate in this loop over the pages in "followers" section
	while 1:
		followers_html = session.get(f"{url}{follower_following}/page/{i}")  # This holds the raw HTML of current page
		soup = BeautifulSoup(followers_html.text, 'html.parser')

		curr_page_elements = soup.find_all('a', class_='name')  # Each line in here contains one follower's name
		if not curr_page_elements:  # If it's empty, that means we ran out of pages, and we break
			break

		# We parse that line with regex to get only the name
		for element in curr_page_elements:
			temp = element.get("href")
			users_list.append(temp[1:-1])

		i += 1

	users_list.sort()
	return users_list

def follow_scraping():
	url = verifyURL()
	session = requests.Session() # Sessions are REALLY efficient if we want to make several requests to the same domain
	user_html = session.get(url)
	soup = BeautifulSoup(user_html.text, 'html.parser')
	if soup.find(string="Sorry, we can’t find the page you’ve requested."): # Checking if user exists
		input(Fore.RED + "User doesn't exist, terminating..." + Fore.RESET)
		exit(-1)

	followers_list = getAllUsers(session, url, "followers")
	following_list = getAllUsers(session, url, "following")

	names_amount_per_line = 10
	print(Fore.RED + "Don't follow back:" + Fore.RESET)
	dont_follow_back = list(set(following_list) - set(followers_list)) # Set subtraction makes it easy
	dont_follow_back.sort()
	printFormattedList(dont_follow_back, names_amount_per_line)
	print(Fore.RED + "Sum: " + str(len(dont_follow_back)) + Fore.RESET)

	print(Fore.GREEN + "\nFans (you don't follow them back):" + Fore.RESET)
	not_following_back = list(set(followers_list) - set(following_list))
	not_following_back.sort()
	printFormattedList(not_following_back, names_amount_per_line)
	print(Fore.GREEN + "Sum: " + str(len(not_following_back)) + Fore.RESET)

	print(Fore.RED + "\nFollowing:" + Fore.RESET)
	printFormattedList(following_list, names_amount_per_line)
	print(Fore.RED + "Sum: " + str(len(following_list)) + Fore.RESET + "\n")

	print(Fore.GREEN + "Followers:" + Fore.RESET)
	printFormattedList(followers_list, names_amount_per_line)
	print(Fore.GREEN + "Sum: " + str(len(followers_list)) + Fore.RESET)

	return dont_follow_back

# Rule of thumb, fastest selectors are (by order): ID, name, link text, CSS selector or class, XPATH
def unfollow(username, password, dont_follow_back):
	options = Options()
	# Ignoring a certificate parsing problem that extended login duration.
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# Disabling loading images, to make the script run faster.
	options.add_argument('--blink-settings=imagesEnabled=false')
	# Headless browsing. It became more stable after adding eager page loading, so it's enabled for now.
	options.add_argument("--headless=new")
	# Helps a bit with performance
	options.add_argument("--disable-gpu")
	# By default, the page load strategy is set to 'normal',
	# which means the WebDriver waits until the entire page loads (HTML file and sub-resources are downloaded).
	# We set it to 'eager', in which the WebDriver waits only until the element itself appears (HTML file is downloaded only).
	# It makes a BIG difference in performance. Before this addition, the script would get stuck a lot, by waiting for the entire page.
	options.page_load_strategy = 'eager'

	driver = webdriver.Chrome(options=options)
	# Using EC (wait until...) over sleep() makes the code much more efficient. We set the timeout limit to 10.
	wait = WebDriverWait(driver, 10)
	driver.get("https://letterboxd.com/sign-in")

	# Logging in
	username_field = wait.until(EC.element_to_be_clickable((By.ID, "signin-username")))
	password_field = wait.until(EC.element_to_be_clickable((By.ID, "signin-password")))
	username_field.send_keys(username)
	password_field.send_keys(password)
	password_field.send_keys(Keys.RETURN) # Submitting the input fields by pressing 'Enter' on the password field

	try:
		# Makes us wait for the login to complete (this arbitrary element is visible only after a successful login)
		# We use 'presence' and not 'visibility' because we only care if the element is present on the DOM.
		# This makes things a *bit* faster
		wait.until(EC.presence_of_element_located((By.ID, "add-new-button")))
		# If the 'EC' above doesn't work, replace it with the 'EC' below
		#wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.avatar.-a24")))
	except TimeoutException:
		print(Fore.RED + "Wrong username or password" + Fore.RESET)
		driver.quit()
		return

	# In this loop we unfollow every username
	for username in dont_follow_back:
		driver.get(f"https://letterboxd.com/{username}")
		button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.js-button-following")))
		button.click()
		# Without 'sleep', sometimes the driver won't be able to find the button for some reason
		time.sleep(0.5)

	driver.quit() # Close the driver instance completely. The script ends right after, but to be on the safe side...

def verifyYesNo():
	character = input("\nDo you want to unfollow the users who don't follow you back? [Y/N] ")
	while character != 'Y' and character != 'y' and character != 'N' and character != 'n':
		character = input("Invalid input, please try again: ")

	return True if character == 'Y' or character == 'y' else False

def main():
	dont_follow_back = follow_scraping()

	# We only enter if list is not empty and the user wished to proceed
	# If the list is empty, we don't ask for proceeding, utilising short-circuiting
	if dont_follow_back and verifyYesNo():
		username = input("Please enter your username or email: ")
		# getpass doesn't allow ctrl+c to be read, but it does allow right click pasting for some reason...
		password = getpass.getpass("Please enter your password (for pasting, use right click, not ctrl+V): ")
		print("Running, please wait...")
		unfollow(username, password, dont_follow_back)

	input("\nDone, Press any key...") # So that the .exe won't close immediately


if __name__ == '__main__':
	main()
