#########################################################################################
#                                Twitch ChatBot module                                  #
#########################################################################################
# Building a Twitch Chat Bot
#
# ChatBot class creates an instance of a Bot that connects to the specified Twitch
# chat channel using a socket.   Once connected the Bot can read and log live chat
# from the selected Twitch channel.  The bot can also disconnect from the current
# channel and reconnect to another without closing the bot instance.
#
#   Methods:  - __init__ : Setup credentials for the ChatBot object.
#
#             - connect_socket : Connects a socket to irc using credentials.
#
#             - change_socket : Closes current socket, modifies credentials,
#                               and reconnects to the new channel.
#
#             - read_chat : Prints chat to console with no logging and no runtime.
#
#             - write_chat : Logs chat to #channel_chat.log over the runtime.
#
#             - vote_counter : Using a predefined voteLibrary.txt (csv), counter will 
#                              log chat messages then load a data frame and check
#                              messages for instances of voteLibrary.txt strings.
#                              Votes can be counted by unique user or all together.
#
#             - contest : Using a predefined winningPhrase this parses messages 
#                         and returns the username, message if the string matches.
#                         Can also specify a number of winners.
#
#
#               **** Only reads messages that are timestamped ****
#
# When the reader is activated the first batch of messages are not timestamped and will
# not be caught by the logger due to the specific syntax.  Given these missed 
# messages are in such a small amount for longer logging sessions I am just ignoring
# it for the time being.
#
#########################################################################################
#########################################################################################



import socket
import logging
from emoji import demojize
import time
import progressbar
from datetime import datetime
import re
import pandas as pd
from processChat import get_chat_dataframe



class ChatBot:
    def __init__(self, nickname, channel,
                 server = 'irc.chat.twitch.tv',
                 port = 6667,
                 token = None,
                 ):
        '''
        - Sets up login credentials.  Server, port, token are all presaved.  This bot
          is for twitch so this data does not need to change for a given user.

        - Currently a single ChatBot instance should be used for a single channel,
          you can start and stop chat once the bot has been enabled but it cannot
          change channels.

        - init creates a specific string title for files created by the bot instance,
          the form of these files is '#channel_chat.log'.
        '''
        # Credentials Data
        self.nickname = nickname
        self.channel = channel
        self.server = server
        self.port = port

        if token == None:
            print('\n\n*** Specificy an OAuth Token ***\n\n')
            return
        else:
            self.token = token



    def connect_socket(self):
        '''
        Connect a socket to the specified twitch channel using the given credentials.
        To change channel or credentials use change_socket()
        '''
        # Add prefix for channel specific logFile
        self.logFile = self.channel + '_chat.log'

        # Create and connect a socket
        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))

        # Connect the socket
        self.sock.send(f"PASS {self.token}\n".encode('utf-8'))
        self.sock.send(f"NICK {self.nickname}\n".encode('utf-8'))
        self.sock.send(f"JOIN {self.channel}\n".encode('utf-8'))

        print('\nConnection Successful')



    def change_socket(self, nickname, channel,
                      server = 'irc.chat.twitch.tv',
                      port = 6667,
                      token = None,
                      ):
        '''
        Closes current socket and changes to the new channel.
        '''
        try:
            self.sock.close()

            # Reassignment for new Credentials Data
            self.nickname = nickname
            self.channel = channel
            self.server = server
            self.port = port
            
            if token == None:
                print('\n\n*** Specificy an OAuth Token ***\n\n')
                return
            else:
                self.token = token

            self.connect_socket()
        except:
            print('\nNo socket to change')

        

    def read_chat(self):
        '''
        Simply reads chat and prints raw output to console with no logging.
        '''
        while True:
            try:
                resp = self.sock.recv(2048).decode('utf-8')
                print(resp)
            except:
                print('\nChat reading canceled.')
                return



    def write_chat(self, runtime, showProgress=True, showChat=False):
        '''
        Logs chat over the runtime to the channel's logFile in the directory.
        '''
        # Set up logging, for loop required, wasnt working without it
        # Could also define my own file rather than using a handler
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d_%H:%M:%S',
                            handlers=[logging.FileHandler(self.logFile, encoding='utf-8')])

        input('\nPress Enter to begin logging\n')
        timer_start = time.time()

        # Setup progressbar
        if showProgress == True:
            widgets = ['Processed messages:  ', progressbar.Counter('%(value)05d'),
                       '     (', progressbar.Timer(), ')']
            bar = progressbar.ProgressBar(widgets=widgets)

        while True:
            # Loop during runtime and log messages as they come in
            try:
                resp = self.sock.recv(4096).decode('utf-8')

                if showChat == True:
                    print(resp)
                elif showProgress == True:
                    bar += 1  

                if resp.startswith('PING'):
                    self.sock.send('PONG\n'.encode('utf-8'))
                elif len(resp) > 0:
                    logging.info(demojize(resp))

            except:
                logging.shutdown()
                print('\nChat logging canceled')
                if showProgress == True:
                    bar.finish()
                return

            # Return after runtime and progressbar update
            if abs(timer_start - time.time()) >= runtime:
                logging.shutdown()
                if showProgress == True:
                    bar.finish()
                print('\n%d seconds of chat logged from' % (runtime), self.channel + '\n')
                return

            
          

    def vote_counter(self, runtime, voteLibrary='voteLibrary.txt',
                     showProgress=True, showChat=False, uniqueUsers=True):
        '''
        Counts votes for entries specified in the voteLibrary file.
        Votes can be counted by only uniqueUserss or all votes total.
        Returns a dictionary with vote Library keys to tallied values.
        '''
        # Run a logging session and get the data frame
        self.write_chat(runtime, showProgress, showChat)
        chatLog = get_chat_dataframe(self.logFile)
        chatLog.set_index('dt', inplace=True)

        with open(voteLibrary, 'r') as f:
            talliedVotes = {key:0 for key in f.read().split(', ')}

        keys = list(talliedVotes)
        messages = chatLog.values[:,1]

        if uniqueUsers == True:
            users = chatLog.values[:,2]
            user_cache = []

        for i in range(len(messages)):
            for key in keys:
                
                # Unique votes
                if uniqueUsers == True:
                    if users[i] not in user_cache and key in messages[i]:
                        talliedVotes[key] += 1
                        user_cache.append(users[i])
                
                # All votes, maximum of 1 per message
                else:
                    if key in messages[i]:
                        talliedVotes[key] += 1

        return talliedVotes
    
    

    def contest(self, winningPhrase, showProgress=True, showChat=False, winners=1):
        '''
        Reads incoming messages looking for a specific phrase, when found
        a winner is chosen and the message is printed.
        '''
        matches = 0

        if showProgress == True:
            print()
            bar = progressbar.ProgressBar(widgets=['Working: ', progressbar.AnimatedMarker()])

        while True:
            # Process raw chat inputs as they come in
            try:
                resp = self.sock.recv(2048).decode('utf-8')
                username, message = re.search(':(.*)\\!.* :(.*)', resp).groups()

                if winningPhrase in message:
                    print('\n\nWe have a winner :  ' + username + '  : ' + message)
                    matches += 1
                    if matches == winners:
                        return

                if showChat == True:
                    print(resp)
                if showProgress == True:
                    bar += 1

            except:
                print('\nContest canceled')
                return


