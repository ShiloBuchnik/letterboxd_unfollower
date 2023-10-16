from bs4 import BeautifulSoup # For searching in HTML file
import requests # For requesting HTML file
import re # For regex
import sys
from colorama import Fore # For coloring output text

url = sys.argv[1]
# Demanding a valid letterboxd user link. '^' means match from start, '$' means match from end
if not re.search('^https://letterboxd.com/\w+/$', url):
	print("Invalid address, try again")
	exit(-1)

# Checking if user exists
user_html = requests.get(url)
soup = BeautifulSoup(user_html.text, 'html.parser')
if soup.find(string="Sorry, we can’t find the page you’ve requested."):
	print("User doesn't exist, try again")
	exit(-1)

i = 1
followers_list = []
# We iterate in this loop over the pages in "followers" section
while 1:
	followers_html = requests.get(url + "followers/page/" + str(i)) # This holds the raw HTML of current page
	soup = BeautifulSoup(followers_html.text, 'html.parser')

	curr_page_list = soup.find_all(attrs={'class': 'avatar -a40'}) # Each line in here contains one follower's name
	if not curr_page_list: # If it's empty, that means we ran out of pages, and we break
		break

	# We parse that line with regex to get only the name
	for line in curr_page_list:
		temp = re.search('/\w+/', str(line))
		temp = temp.group()
		followers_list.append(temp[1:-1]) # We remove first and last character (which is '\' in this case)

	i += 1

i = 1
following_list = []
# This the same, only for the "following" section
while 1:
	following_html = requests.get(url + "following/page/" + str(i))
	soup = BeautifulSoup(following_html.text, 'html.parser')

	curr_page_list = soup.find_all(attrs={'class': 'avatar -a40'})
	if not curr_page_list:
		break

	for line in curr_page_list:
		temp = re.search('/\w+/', str(line))
		temp = temp.group()
		following_list.append(temp[1:-1])

	i += 1


# Prints 'amount_per_line' names per line, then prints a newline and so on
def printFormattedList(arg_list, amount_per_line):
	for j in range(0, len(arg_list), amount_per_line):
		names_to_print = arg_list[j: j + amount_per_line]
		print(*names_to_print, sep=", ")


names_amount_per_line = 10
print(Fore.RED + "Don't follow back:" + Fore.RESET)
dont_follow_back = list(set(following_list) - set(followers_list)) # Set subtraction makes it easy
printFormattedList(dont_follow_back, names_amount_per_line)

print(Fore.GREEN + "\nFans (you're not following them back):" + Fore.RESET)
not_following_back = list(set(followers_list) - set(following_list))
printFormattedList(not_following_back, names_amount_per_line)

print(Fore.RED + "\nFollowers:" + Fore.RESET)
printFormattedList(followers_list, names_amount_per_line)
print("Sum: " + str(len(followers_list)) + "\n")

print(Fore.GREEN + "Following:" + Fore.RESET)
printFormattedList(following_list, names_amount_per_line)
print("Sum: " + str(len(following_list)))
