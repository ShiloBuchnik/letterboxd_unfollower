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

def follow_scraping():
	try:  # For running through the CLI
		url = sys.argv[1]
	except IndexError:  # For running through the .exe
		url = input("Please enter your Letterboxd user URL: ")

	# Demanding a valid letterboxd user link. '^' means match from start, '$' means match from end
	if not re.search(r'^https://letterboxd.com/\w+/$', url):
		input(Fore.RED + "Invalid address, terminating..." + Fore.RESET)
		exit(-1)

	session = requests.Session()
	user_html = session.get(url)
	soup = BeautifulSoup(user_html.text, 'html.parser')
	if soup.find(string="Sorry, we can’t find the page you’ve requested."):  # Checking if user exists
		input(Fore.RED + "User doesn't exist, terminating..." + Fore.RESET)
		exit(-1)

	i = 1
	followers_list = []
	# We iterate in this loop over the pages in "followers" section
	while 1:
		followers_html = session.get(url + "followers/page/" + str(i))  # This holds the raw HTML of current page
		soup = BeautifulSoup(followers_html.text, 'html.parser')

		curr_page_list = soup.find_all(attrs={'class': 'avatar -a40'})  # Each line in here contains one follower's name
		if not curr_page_list:  # If it's empty, that means we ran out of pages, and we break
			break

		# We parse that line with regex to get only the name
		for line in curr_page_list:
			temp = re.search(r'/\w+/', str(line))
			temp = temp.group()
			followers_list.append(temp[1:-1])  # We remove first and last character (which is '\' in this case)

		i += 1
	followers_list.sort()

	i = 1
	following_list = []
	# This the same, only for the "following" section
	while 1:
		following_html = session.get(url + "following/page/" + str(i))
		soup = BeautifulSoup(following_html.text, 'html.parser')

		curr_page_list = soup.find_all(attrs={'class': 'avatar -a40'})
		if not curr_page_list:
			break

		for line in curr_page_list:
			temp = re.search(r'/\w+/', str(line))
			temp = temp.group()
			following_list.append(temp[1:-1])

		i += 1
	following_list.sort()

	names_amount_per_line = 10
	print(Fore.RED + "Don't follow back:" + Fore.RESET)
	dont_follow_back = list(set(following_list) - set(followers_list))  # Set subtraction makes it easy
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

def unfollow(username, password, dont_follow_back):
	options = Options()

	# Ignoring a certificate parsing problem that extended login duration.
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# Disabling loading images, to make the script run faster.
	options.add_argument('--blink-settings=imagesEnabled=false')
	driver = webdriver.Chrome(options)
	# Using EC (wait until...) over sleep() makes the code MUCH more efficient. We set the timeout limit to 30.
	wait = WebDriverWait(driver, 15)

	driver.get("https://letterboxd.com")

	# Pressing the login button
	button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "label")))
	button.click()

	username_field = driver.find_element(By.ID, "username")
	password_field = driver.find_element(By.ID, "password")

	username_field.send_keys(username)
	password_field.send_keys(password)

	# Submitting the input fields
	password_field.send_keys(Keys.RETURN)

	try:
		# Makes us wait for the login to complete (this arbitrary element is visible only after a successful login)
		wait.until(EC.visibility_of_element_located((By.ID, "add-new-button")))
	except TimeoutException:
		print(Fore.RED + "Wrong username or password" + Fore.RESET)
		return

	# In this loop we unfollow every username
	for username in dont_follow_back:
		driver.get("https://letterboxd.com/" + username)
		button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-action='/" + username + "/unfollow/']")))
		button.click()
		# When we sleep, we die and born again in the following morning.
		# Anyway, without it, sometimes the driver won't be able to find the button for some reason
		time.sleep(1)

	driver.close()

def verifyInput():
	character = input("\nDo you want to unfollow the users who don't follow you back? [Y/N] ")
	while character != 'Y' and character != 'y' and character != 'N' and character != 'n':
		character = input("Invalid input, please try again: ")

	return True if character == 'Y' or character == 'y' else False

def main():
	dont_follow_back = follow_scraping()

	# We only enter if list is not empty and the user wished to proceed
	# If the list is empty, we don't ask for proceeding, utilising short-circuiting
	if dont_follow_back and verifyInput():
		username = input("Please enter your username or email: ")
		password = getpass.getpass("Please enter your password: ")
		unfollow(username, password, dont_follow_back)

	input("\nPress any key...") # So that the .exe won't close immediately


if __name__ == '__main__':
	main()
