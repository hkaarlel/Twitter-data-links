#-*- coding: utf-8 -*- 
# 
# Heikki Kaarlela
# Algorithms and Data Structures
# Final exercise 2014
#
# The purpose of the exercise was to create a program to find out links between different Twitter tweets and users (f.ex. how many users
# are between chosen users, or a chosen user and a hashtag. The exercise also included collecting the data by using Twitter's API,
# but it is not included in this file. This piece of program reads that collected json-data from a txt-file.
#
# The algorithm used in the breadth-first search is from the material:
# V Verkkojen algoritmeja, Osa 1: Leveys- ja syvyyshaku by Ari Vesanen, Tietojenkäsitttelytieteiden laitos
#
# Quicksort and Partition functions are modified versions of ones used in the week 2's exercise

import json
import sys
from collections import deque

def dataCollect(tweets, hashtags, users, usernames, filename):
    """Reads the objects from a given file and adds them into the data structures"""
    data = []
    try:
        file = open(filename, "r")
    except IOError:
        print "No such file in this directory" 
        return tweets, hashtags, users, usernames, False    # Returns that collecting the data didn't work
    for line in file:
            data.append(json.loads(line))                   # The data is loaded into a list
    file.close()
    for i in range(len(data)):
        # User ID:s and their user names are saved in a dictionary
        user_id = data[i]["id"]
        user_name = data[i]["screen_name"]
        usernames[user_id] = user_name
        # Users and their connections are saved in a dictionary
        friends_ids = data[i]["friends_ids"]
        users[user_id] = []
        for k in range(len(friends_ids)):
            users[user_id].append(friends_ids[k])
            try:
                users[friends_ids[k]].append(user_id)       # Adds the user's name into a friend's connection list if it exists
            except KeyError:
                users[friends_ids[k]] = [user_id]           # If it does not exist creates it first and adds the user's name then
        # All the tweets are saved in one list
        tweet = data[i]["last_ten_tweets"]
        for j in range(len(tweet)):
            post = tweet[j]["text"]
            posted_at = tweet[j]["created_at"]
            posted_at = formatTime(posted_at)               # Changes the time format to one easier to sort
            poster_id = tweet[j]["user"]["id_str"]
            post_hashtags = []
            for i in range(len(tweet[j]["entities"]["hashtags"])):
                post_hashtags.append(tweet[j]["entities"]["hashtags"][i]["text"])       # Makes a list of the tweet's hashtags
                # Adding the user in the list of those who have used this hashtag
                try:
                    hashtags[tweet[j]["entities"]["hashtags"][i]["text"]].append(user_id)
                except KeyError:
                    hashtags[tweet[j]["entities"]["hashtags"][i]["text"]] = [user_id]
            tweets.append((posted_at, poster_id, post_hashtags, post))                  # Inserts the relevant data from the tweet into the list 
    return tweets, hashtags, users, usernames, True                                     # Returns the data structures and confirmation of success
    
def formatTime(time):
    """Changes the time from EEE MMM dd HH:mm:ss zzzz yyyy
    to yyyy MM dd HH:mm:ss for sorting purposes"""
    year = time[26:30]
    month = time[4:7]
    day = time[7:11]
    clock = time[11:19]
    if month == "Jan":                                      # Changes the month into a number
        month = "01"
    elif month == "Feb":
        month = "02"
    elif month == "Mar":
        month = "03"
    elif month == "Apr":
        month = "04"
    elif month == "May":
        month = "05"
    elif month == "Jun":
        month = "06"
    elif month == "Jul":
        month = "07"
    elif month == "Aug":
        month = "08"
    elif month == "Sep":
        month = "09"
    elif month == "Oct":
        month = "10"
    elif month == "Nov":
        month = "11"
    elif month == "Dec":
        month = "12"
    newtime = str(year) + " " + str(month) + str(day) + str(clock)
    return newtime
        
def tweetIDSearch(id, tweets):
    """Finds tweets with a given user id"""
    id = str(id)
    tweets_from_id = []
    for i in range(len(tweets)):                                    # Goes through all the tweets, adds right ones in a new list
        if tweets[i][1] == id:                                      # Compares the user id:s
            tweets_from_id.append(tweets[i])
    quickSort(tweets_from_id, 0, (len(tweets_from_id)-1))
    return tweets_from_id                                           # Returns the new sorted list
    
def tweetHashtagSearch(hashtag, tweets):
    """Finds tweets with a given hashtag"""
    tweets_with_hashtag = []
    for i in range(len(tweets)):                                    # Goes through all the tweets, adds ones with the hashtag in a new list
        if hashtag in tweets[i][2]:                                 # Compares the tweet's hashtags
            tweets_with_hashtag.append(tweets[i])
    quickSort(tweets_with_hashtag, 0, (len(tweets_with_hashtag)-1))
    return tweets_with_hashtag                                      # Returns the new sorted list
    
def tweetTimeSearch(starttime, endtime, tweets):
    """Finds tweets with a given date interval"""
    tweets_in_interval = []
    starttime = starttime + " 00:00:00"                             # Adds start and end times by the second to get all the tweets
    endtime = endtime + " 23:59:59"
    for i in range(len(tweets)):                                    # Goes through all the tweets, adds right ones in a new list
        if tweets[i][0] >= starttime and tweets[i][0] <= endtime:   # Compares the tweet's creation time
            tweets_in_interval.append(tweets[i])
    quickSort(tweets_in_interval, 0, (len(tweets_in_interval)-1))
    return tweets_in_interval                                       # Returns the new sorted list

def quickSort(A, first, last):
    """Sorts the list from the smallest value to the largest"""
    if first < last:
        middle = partition(A, first, last)
        quickSort(A, first, middle-1)
        quickSort(A, middle+1, last)
    return A

def partition(A, first, last):
    """Used by quickSort to sort lists by the item's first value"""
    pivot = A[last][0]
    i = first-1
    for j in range(first, last):
        if A[j][0] <= pivot:
            i = i + 1
            A[i], A[j] = A[j], A[i]
    A[i+1], A[last] = A[last], A[i+1]
    return i+1
    
def mostConnected(users, usernames):
    """Return the person with createst number of direct connections"""
    id = []
    id.append(users.keys()[0])
    for i in users:
        if len(users[i]) > len(users[id[0]]):       # If the currently looked at user has more connections than previous ones, delete others and add this user
            id = []
            id.append(i)
        elif len(users[i]) == len(users[id[0]]):    # If the currently looked at user has as much connections as previous ones, add it in the list
            id.append(i)
    id_str = ""
    for i in id:
        try:
            id_str = id_str + usernames[i] + " "    # Adds the most connected users into one line
        except KeyError:
            id_str = id_str + str(i) + " "          # If the username does not exist, adds the id
    return id_str

def BFS(users, start):
    """Breadth first search to create a tree with shortest links"""
    color = {}
    d = {}
    p = {}
    for u in users:
        color[u] = "white"
        d[u] = 0
        p[u] = 0
    d[start] = 0
    color[start] = "gray"
    Q = deque()
    Q.append(start)
    while len(Q) != 0:
        u = Q.popleft()
        for v in range(len(users[u])):
            if color[users[u][v]] == "white":
                color[users[u][v]] = "gray"
                d[users[u][v]] = d[u]+1
                p[users[u][v]] = u
                Q.append(users[u][v])
        color[u] = "black"
    return p
    
def BFSPath(G, start, goal, p, path):
    """Creates the shortest path between users by using the BFS-created tree"""
    if goal == start:
        path.append(goal)
    else:
        if p[goal] == 0:
            return path
        else:
            BFSPath(G, start, p[goal], p, path)
            path.append(goal)
    return path
        
def shortestLink(users, usernames, start, goal):
    """Prints the shortest link between two users"""
    rev_usernames = {v: k for k, v in usernames.items()}        # Creates a reversed dictionary so id can be searched with screen name
    try:                                                        
        start = rev_usernames[start]                            # Gets the id:s from the reversed dictionary
        goal = rev_usernames[goal]
    except KeyError:
        print "There is no user in the data set with that user name"
        return
    path = []
    p = BFS(users, start)                                       # Creates the BFS-tree
    path = BFSPath(users, start, goal, p, path)                 # Finds the shortest path (or one of them)
    pathstr = ""
    for i in range(len(path)):                                  # The path is formatted into a string with "->" between users
        try:
            pathstr = pathstr + usernames[path[i]]              # If there are screen names for the user id:s, they are used
        except KeyError:
            pathstr = pathstr + str(path[i])
        if i != (len(path) - 1):
            pathstr = pathstr + " -> "
    if pathstr != "":
        print "The shortest path or one of the shortest paths is", pathstr  # Prints the path
    else:
        print "There is no link between these users"                        # If the path is empty, there is no link
    
def shortestLinkTweet(users, usernames, hashtags, tweets, start, hashtag):
    """Prints the shortest link between two users"""
    rev_usernames = {v: k for k, v in usernames.items()}                        # Creates a reversed dictionary so id can be searched with screen name
    try:
        start = rev_usernames[start]                                            # Gets the id from the reversed dictionary
    except KeyError:
        print "There is no user in the data set with that user name"
        return
    try:
        hashtags[hashtag]                                                       # Tests if the hashtag has been used in any tweet
    except KeyError:
        print "No one in the data set has used this hashtag"
        return
    paths = []
    p = BFS(users, start)                                                       # Creates the BFS-tree
    for i in range(len(hashtags[hashtag])):
        tweetpath = []
        tweetpath = BFSPath(users, start, hashtags[hashtag][i], p, tweetpath)   # Gets the paths between the given user
        paths.append(tweetpath)                                                 # and every user who has used the hashtag
    shortest, tweet = getShortestPath(paths, tweets, hashtag)                   # Finds the shortest one of these paths and the earliest tweet
    if len(paths[shortest]) == 1:
        print "The given user has used the hashtag"                             # If the shortest path only has one user, he/she has used the hashtag
    else:
        try:
            closest_person = usernames[paths[shortest][len(paths[shortest])-1]] # The closest person is the last person in the path
        except KeyError:
            closest_person = paths[shortest][len(paths[shortest])-1]            # If the person has no screen name, the id is printed
        print "The closest person to use the hashtag is", closest_person
        pathstr = ""
        for i in range(len(paths[shortest])):
            try:                                                                # The path is formatted into a string with "->" between users
                pathstr = pathstr + usernames[paths[shortest][i]]               
            except KeyError:
                pathstr = pathstr + str(paths[shortest][i])                     # If there are screen names for the user id:s, they are used
            if i != (len(paths[shortest]) - 1):
                pathstr = pathstr + " -> "
        if pathstr != "":
            print "The shortest path is", pathstr
        else:
            print "There is no link"""
    print "The tweet:"                                                          # Prints the earliest tweet with the hashtag of the closest person
    try:
        print tweet
    except UnicodeEncodeError:                                                  # Try-except is in case the tweets include special characters
        print tweet.encode('utf-8')

def getShortestPath(paths, tweets, hashtag):
    """Returns the index of the shortest path in the given path list
    and the earliest tweet with the hashtag.
    If there are several equally short paths, returns the index
    of the path where the tweet was created first"""
    index = 0                                                                   # The starting index is 0
    user_id = paths[0][len(paths[0])-1]                                         # The last id in the path is the tweet's writer
    user_tweets = tweetIDSearch(user_id, tweets)                                # Search the user's tweets
    user_tweets = tweetHashtagSearch(hashtag, user_tweets)                      # Search user's tweets which have the hashtag
    tweet = user_tweets[0][3]                                                   # The first tweet with the hashtag is the earliest tweet of the list
    for i in range(len(paths)):
        if len(paths[i]) < len(paths[index]):                                   # If the path is shorter than the currently shortest path
            index = i                                                           # change the index and get the new earliest tweet
            user_id = paths[i][len(paths[i])-1]
            user_tweets = tweetIDSearch(user_id, tweets)
            user_tweets = tweetHashtagSearch(hashtag, user_tweets)
            tweet = user_tweets[0][3]
        if len(paths[i]) == len(paths[index]):                                  # In case the paths are the same length, compare which one's
            useri_id = paths[i][len(paths[i])-1]                                # final user posted first with the hashtag and get that tweet
            useri_tweets = tweetIDSearch(useri_id, tweets)
            useri_tweets = tweetHashtagSearch(hashtag, useri_tweets)
            userindex_id = paths[i][len(paths[i])-1]
            userindex_tweets = tweetIDSearch(userindex_id, tweets)
            userindex_tweets = tweetHashtagSearch(hashtag, userindex_tweets)
            time_i = useri_tweets[0][0]
            tweet_i = useri_tweets[0][3]
            time_index = userindex_tweets[0][0]
            if time_i < time_index:                                             # If the currently looked at poster posted first with the hashtag
                index = i                                                       # his/her path is chosen as the shortest path and the tweet is saved
                tweet = tweet_i
    return index, tweet        
              
def userInterface(tweets, hashtags, users, usernames):
    """User chooses how the data is analysed and the chosen analysis functions are called.
    Between the analyses the program stays in the menu until the program is closed"""
    show_menu = True
    while True:
        if show_menu == True:
            print "\nChoose one of the analysis options by writing the number"
            print "1. Read more data"
            print "2. Output the total number of users in the data"
            print "3. Output the person with the greatest number of direct connections"
            print "4. Find the shortest link between two users"
            print "5. Find the shortest link between an user and an user who has used a hashtag"
            print "6. Print all tweets of a given user in chronological order"
            print "7. Print all tweets with a given hashtag in chronological order"
            print "8. Print all tweets on a given date interval in chronological order"
            print "9. Quit"
        if show_menu != True:                           # After the first time the menu is not shown if the user does not ask for it
            print "\nWrite 0 to show the menu"
        show_menu = False
        input = -1
        while True:
            try:                                        # The input is asked and tested that it is a valid command
                input = int(raw_input("Write a command (0-9): "))
            except ValueError:
                print "Press 0, 1, 2, 3, 4, 5, 6, 7, 8 or 9"
            if input < 0 or input > 9:
                print "Press 0, 1, 2, 3, 4, 5, 6, 7, 8 or 9"
            else:
                break
        if input == 9:                                  # Quit the program with 9
            break
        elif input == 0:                                # Show the menu again with 0
            show_menu = True
        else:                                           # Other commands are in another function
            inputs(tweets, hashtags, users, usernames, input)
        
def inputs(tweets, hashtags, users, usernames, input):
    if input == 1:  # Read more data from a file
        file = raw_input("Give file name (for example UniOulu.json): ")
        tweets, hashtags, users, usernames, success = dataCollect(tweets, hashtags, users, usernames, file)
        if success == True:
            print "\nData set read"
        else:
            print "\nData set couldn't be read"
    if input == 2:  # Print total number of users
        print "\nThe total number of users is", len(users)
    if input == 3:  # Print person with the greatest number of direct connections
        print "\nThe person with the greatest number of direct connections is", mostConnected(users, usernames)
    if input == 4:  # Print the shortest link between two users
        user1 = raw_input("Give the first user (for example UniOulu): ")
        user2 = raw_input("Give the second user (for example UniOulu): ")
        shortestLink(users, usernames, user1, user2)
    if input == 5:  # Print the shortest link between an user an user who has used the hashtag
        user = raw_input("Give the screen name of the user (for example UniOulu): ")
        hashtag = raw_input("Give the hashtag (for example Suomi): ")
        shortestLinkTweet(users, usernames, hashtags, tweets, user, hashtag)
    if input == 6:  # Print user's tweets
        userID = raw_input("Give the user's id (for example 123456789): ")
        try:        # Test if the user gave an id with just numbers
            userID = int(userID)
        except ValueError:
            print "Use the numerical id (for example 123456789)"
        tweets_user = tweetIDSearch(userID, tweets)
        print "\n", len(tweets_user), "tweets of the user in chronological order:"
        for i in range(len(tweets_user)):
            try:                                        # Try-except is in case the tweets include special characters
                print tweets_user[i][3]
            except UnicodeEncodeError:
                print tweets_user[i][3].encode('utf-8')
    if input == 7:  # Print tweets with a given hashtag
        hashtag = raw_input("Give the hashtag (for example Suomi): ")
        tweets_hashtag = tweetHashtagSearch(hashtag, tweets)
        print "\n", len(tweets_hashtag), "tweets with a given hashtag in chronological order:"
        for i in range(len(tweets_hashtag)):
            try:                                        # Try-except is in case the tweets include special characters
                print tweets_hashtag[i][3]
            except UnicodeEncodeError:
                print tweets_hashtag[i][3].encode('utf-8')
    if input == 8:  # Print tweets in a given time interval
        start_time = raw_input("Give the start date in the format YYYY MM DD (for example 2014 12 02): ")
        end_time = raw_input("Give the end date in the format YYYY MM DD (for example 2014 12 05): ")
        tweets_time = tweetTimeSearch(start_time, end_time, tweets)
        print "\n", len(tweets_time), "tweets in a given date interval in chronological order:"
        if len(tweets_time) == 0:
            print "No tweets in a given date interval"
        for i in range(len(tweets_time)):
            try:                                        # Try-except is in case the tweets include special characters
                print tweets_time[i][3]
            except UnicodeEncodeError:
                print tweets_time[i][3].encode('utf-8') 

def main():
    # The name of the file to analyse will be given as a command line argument
    if len(sys.argv) != 2:
        print "Please give the name of the file (for example UniOulu.json) as a command line argument)"
        return
    # Create the four data structures to be filled
    tweets = []                                         # List of all tweets
    users = {}                                          # User id:s and their connections
    usernames = {}                                      # User id:s and their usernames
    hashtags = {}                                       # All hashtags and which user used which
    tweets, hashtags, users, usernames, success = dataCollect(tweets, hashtags, users, usernames, sys.argv[1]) # Reads the data into data structures
    if success == True:
        print "Data set read"
    else:
        print "Data set couldn't be read"
        return
    userInterface(tweets, hashtags, users, usernames)     # Starts the analysis menu
     
if __name__ == '__main__':
    main()