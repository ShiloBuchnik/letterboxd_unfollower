from bs4 import BeautifulSoup # For searching in HTML file
import requests # For requesting HTML file
import re # For regex
import sys
from colorama import Fore # For coloring output text

# Prints 'amount_per_line' names per line, then prints a newline and so on
def printFormattedList(arg_list, amount_per_line):
	for i in range(0, len(arg_list), amount_per_line):
		names_to_print = arg_list[i: i + amount_per_line]
		print(*names_to_print, sep=", ")

def main():
	try: # For running through the CLI
		url = sys.argv[1]
	except IndexError: # For running through the .exe
		url = input("Please enter your Letterboxd user URL: ")

	# Demanding a valid letterboxd user link. '^' means match from start, '$' means match from end
	if not re.search(r'^https://letterboxd.com/\w+/$', url):
		print("Invalid address, try again")
		input("Enter any key...")
		exit(-1)

	session = requests.Session()
	user_html = session.get(url)
	soup = BeautifulSoup(user_html.text, 'html.parser')
	if soup.find(string="Sorry, we can’t find the page you’ve requested."): # Checking if user exists
		print("User doesn't exist, try again")
		input("Enter any key...")
		exit(-1)

	i = 1
	followers_list = []
	# We iterate in this loop over the pages in "followers" section
	while 1:
		followers_html = session.get(url + "followers/page/" + str(i)) # This holds the raw HTML of current page
		soup = BeautifulSoup(followers_html.text, 'html.parser')

		curr_page_list = soup.find_all(attrs={'class': 'avatar -a40'}) # Each line in here contains one follower's name
		if not curr_page_list: # If it's empty, that means we ran out of pages, and we break
			break

		# We parse that line with regex to get only the name
		for line in curr_page_list:
			temp = re.search(r'/\w+/', str(line))
			temp = temp.group()
			followers_list.append(temp[1:-1]) # We remove first and last character (which is '\' in this case)

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
	dont_follow_back = list(set(following_list) - set(followers_list)) # Set subtraction makes it easy
	dont_follow_back.sort()
	printFormattedList(dont_follow_back, names_amount_per_line)

	print(Fore.GREEN + "\nFans (you don't follow them back):" + Fore.RESET)
	not_following_back = list(set(followers_list) - set(following_list))
	not_following_back.sort()
	printFormattedList(not_following_back, names_amount_per_line)

	print(Fore.RED + "\nFollowing:" + Fore.RESET)
	printFormattedList(following_list, names_amount_per_line)
	print(Fore.RED + "Sum: " + str(len(following_list)) + Fore.RESET + "\n")

	print(Fore.GREEN + "Followers:" + Fore.RESET)
	printFormattedList(followers_list, names_amount_per_line)
	print(Fore.GREEN + "Sum: " + str(len(followers_list)) + Fore.RESET)

	input("Enter any key...") # So that the .exe won't close immediately


if __name__ == '__main__':
	main()
