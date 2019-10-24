#########################################################################################

# Collection of functions to process raw Twitch Chat Data.

# The fucntion get_chat_dataframe() is used in the Twitch Chat bot to load data from the
# .log file into a pandas dataframe.

# Other functions are for ways of processing this data and generating vocabularies for 
# use in a Recurrent Neural Network.  

# Most notably the 'clean' functions will read through raw chat data and remove 
# non-standard characters.  This 'cleaning' is necessary for the data to be useable in 
# the Text Generation RNN.

#########################################################################################


import time
import os
import numpy as np
import pandas as pd
from datetime import datetime
import re
import string




def get_chat_dataframe(logFile):
    '''
    Loads the current #channel_chat.log file and returns a pandas dataframe.
    '''
    data = []

    with open(logFile, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n\n\n')
        # Go through lines and extract data by splitting strings appropriately 
        for line in lines:
            try:
                time_logged = line.split(' - ')[0].strip()
                time_logged = datetime.strptime(time_logged, '%Y-%m-%d_%H:%M:%S')

                username_message = line.split(' - ')[1:]
                username_message = ''.join(username_message).strip()

                username, channel, message = re.search(
                    ':(.*)\\!.*@.*\\.tmi\\.twitch\\.tv PRIVMSG #(.*) :(.*)',
                    username_message).groups()

                d = {
                    'dt': time_logged,
                    'channel': channel,
                    'username': username,
                    'message': message
                    }

                data.append(d)

            except Exception:
                pass

    return pd.DataFrame().from_records(data)




def characterVocab(logFile):
    '''
    Opens all messages and writes them to a separate file for storage on 
    new lines in a single string.  Character vocab is created and lookup
    dictionaries are returned.
    '''
    messages = get_chat_dataframe(logFile).values[:,2]

    # Writing to allChat.txt to just keep a running file
    with open('allChat.txt', 'w', encoding='utf-8') as file:
        for message in messages:
            file.write(message + '\n')

    text = open('allChat.txt', 'r', encoding='utf-8').read() 
    
    vocab = sorted(set(text))
    # Dictionary and inverse dictionary for character lookup
    idx2char = {idx : char for idx, char in enumerate(vocab)}

    char2idx = {char : idx for idx, char in idx2char.items()}

    return text, idx2char, char2idx




def clean_messages(logFile, chatText):
    '''
    Scans through logFile and discards messages that use 
    non-standard characters
    '''
    messages = get_chat_dataframe(logFile).values[:,3]
    
    with open(chatText, 'w', encoding='utf-8') as file:
        for message in messages:
            skip = False
            for character in list(message):
                if character not in string.printable:
                    skip = True
                    break

            if skip == False:
                file.write(message + '\n')




def clean_messages_with_users(logFile, chatText):
    '''
    Scans through logFile and discards messages that use 
    non-standard characters
    '''
    users = get_chat_dataframe(logFile).values[:,2]
    messages = get_chat_dataframe(logFile).values[:,3]
    
    with open(chatText, 'w', encoding='utf-8') as file:
        for username, message in zip(users, messages):
            skip = False
            for character in list(message):
                if character not in string.printable:
                    skip = True
                    break

            if skip == False:
                file.write(username + ': ' + message + '\n')




def clean_characterVocab(chatText):
    '''
    Same as character vocab but only keeps messages with standard ascii
    values.
    '''
    text = open(chatText, 'r', encoding='utf-8').read() 
    
    vocab = sorted(set(text))
    # Dictionary and inverse dictionary for character lookup
    idx2char = {idx : char for idx, char in enumerate(vocab)}

    char2idx = {char : idx for idx, char in idx2char.items()}

    return text, idx2char, char2idx





def chatVocabulary(logFile, underUsed=5):
    '''
    Returns a sorted list of tuples showing word usage in descending order.

    Also returns enumerated dictionaries for messages and words as well as
    inverse dictionaries allowing to go from index -> word -> index using 
    two dictionary calls.
    '''
    messages = get_chat_dataframe(logFile).values[:,2]

    wordVocab = dict()
    messageVocab = list()

    for message in messages:
        message = message.lower()
        # Only take messages that have more than 1 word
        if len(message.split()) > 1:
            messageVocab.append(message)

            # Only splits words at spaces, could look at using regex to split at commas, peroids, etc.
            for word in message.split(' '):
                try:
                    wordVocab[word] += 1
                except:
                    wordVocab[word] = 1

    # Remove underused words
    allWords = set(wordVocab)
    for word in allWords:
        if wordVocab[word] < underUsed:
            del wordVocab[word]

    # Sorted dictionary to show occurances, just to check for interest
    occurances = sorted([(value, key) for (key,value) in wordVocab.items()], reverse=True)

    # Make messageVocab an enumerated dictionary
    messageVocab = {index : message for index, message in enumerate(set(messageVocab))}

    # Change wordVocab from a dictionary of occurance to enumerated values
    wordVocab = {index : word for index, word in enumerate(set(wordVocab))}
    
    # Inverse dictionaries to go from a message or word value to the index key
    message_to_index = {message : index for index, message in messageVocab.items()}
    word_to_index = {word : index for index, word in wordVocab.items()}

    return occurances, messageVocab, wordVocab, message_to_index, word_to_index


