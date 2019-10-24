#########################################################################################
#                          bot script that runs TwitchChatBot module                    #   
#########################################################################################
# Console interface script that creates a Twitch Chat Bot.
#     - See TwitchChatBot.py for more information on methods
#
# Begin by selecting a nickname and a channel.  Server, Port, Token can also be specified
# but for single user the default information is ok.  Once a channel has been selected
# input a choice from the selection below:
#
# Choices: ['Read Chat', 'Write Chat', 'Count Votes', 'Contest', 'Change Socket', 'Quit']
#
#     - Read Chat reads and displays live twitch chat from the selected channel
#
#     - Write Chat writes chat to a file with an option for displaying live chat
#
#     - Count votes stores chat data over a runtime and compares inputs to a library
#       of keywords and tallies votes by unique user or total votes.
#
#     - Contest uses an input string and reads incoming chat until a matching message
#       is found.
#
#     - Change Socket allows the bot to change nickname and channel
#
#     - Quit will close the bot
#
#########################################################################################
#########################################################################################



from twitchChatBot_git import ChatBot
import os


def show():
    '''
    Returns settings for showProgress and showChat during logging.
    '''
    while True:
        display = input('\nDisplay chat during logging (Y/N): ')
        if display.lower() == 'y':
            showChat = True
            showProgress = False
            break
        elif display.lower() == 'n':
            showChat = False
            showProgress = True
            break
    return showProgress, showChat



if __name__ == '__main__':

    print('\nWelcome to the Twitch chat logger, the wrong way to save cancer.\n')

    # Get nickname, channel, and log display information
    nickname = input('\nSelect a nickname: ')

    while True:
        channel = input('\nSelect a channel: ')
        if channel[0] != '#':
            print('\nIncorrect channel name, use form "#channelname"')
        else:
            break

    # Initialize bot with either default or user selected credentials
    while True:
        defaultCredentials = input('\nUse default credentials (Y/N): ')
        if defaultCredentials.lower() == 'y':
            bot = ChatBot(nickname, channel)
            break
        elif defaultCredentials.lower() == 'n':
            server = input('\nInput server: ')
            port = int(input('\nInput port'))
            token = input('\nInput token')
            bot = ChatBot(nickname, channel, server, port, token)
            break

    # Connect the bot
    bot.connect_socket()


    # Main loop, will run to KeyboardInterrupt or if Quit is selected from choices
    while True:
        # Input a task
        while True:
            choices = ['Read Chat', 'Write Chat', 'Count Votes', 'Contest', 'Change Socket', 'Quit']
            pick = input('\nRead Chat, Write Chat, Count Votes, Contest, Change Socket, or Quit?  ')
            if pick in choices:
                break
        
        if pick == 'Quit':
            break

        elif pick == 'Change Socket':
            nickname = input('\nSelect a nickname: ')
            while True:
                channel = input('\nSelect a channel: ')
                if channel[0] != '#':
                    print('\nIncorrect channel name, use form "#channelname"')
                else:
                    break
            bot.change_socket(nickname, channel)


        elif pick == 'Read Chat':
            bot.read_chat()
        
        if pick not in ['Quit', 'Change Socket', 'Read Chat']:
            # Assign showProgress, showChat for following methods
            showProgress, showChat = show()

            if pick == 'Contest':
                winningPhrase = input('\nInput the winning phrase: ')
                bot.contest(winningPhrase, showProgress, showChat)

            else:
                # Check for #channel_chat.log and choose to delete or not
                if os.path.exists(channel + '_chat.log') == True:
                    new_log = input('\nCreate fresh log file (Y/N): ')
                    if new_log.lower() == 'y':
                        os.remove(channel + '_chat.log')

                runtime = int(input('\nInput runtime in seconds: '))

                if pick == 'Write Chat':
                    bot.write_chat(runtime, showProgress, showChat)

                elif pick == 'Count Votes':
                    voteLibrary = input('\nSpecify file for voteLibrary: ')
                    uniqueVotes = input('\nCount unique user votes (Y/N): ')
                    if uniqueVotes.lower() == 'y':
                        uniqueUsers = True
                    else:
                        uniqueUsers = False

                    talliedVotes = bot.vote_counter(runtime, voteLibrary, showProgress,
                                                    showChat, uniqueUsers)
                    for key in talliedVotes:
                        print(key + ' :  %d' % talliedVotes[key])


