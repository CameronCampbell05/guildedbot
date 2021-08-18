# guilded.py imports
import guilded
from guilded.ext import commands
# mysql imports
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
# other imports
import time, random

# Connects To Database Via Connection Pool ################################################
try:
    connection_pool = pooling.MySQLConnectionPool(pool_name="connection_pool",
        pool_size=32,
        pool_reset_session=True,
        host="REDACTED",
        user="REDACTED",
        password="REDACTED",
        database="REDACTED"
    )
except Error as e:
    print("Error while connecting to MySQL using Connection pool ", e)
###########################################################################################

# Function That Gets Connection From Connection Pool ######################################
def get_connection():
    connection_object = None
    while connection_object is None:
        try:
            connection_object = connection_pool.get_connection()
        except Error as e:
           print(e)

    try:
        if connection_object.is_connected():
            return connection_object, connection_object.cursor()
    except Error as e:
        print(e)
###########################################################################################

# Sets Up Misc Stuff ######################################################################
client = guilded.Client()
earningTimeoutDict = dict()
###########################################################################################

@client.event
async def on_ready():
    print('Ready')

# sees if a user exists in the database - returns user's row or false
async def getExistingUser(userID):
    doesExist = False

    try:
        connection_object, cursor = get_connection()
    except: pass
    finally:
        if connection_object.is_connected():
            sql = f"SELECT * FROM currency_data WHERE GuildedID='{userID}'"
            cursor.execute(sql)
            result = cursor.fetchone()

            if result != None:
                doesExist = result
            
            cursor.close()
            connection_object.close()

    return doesExist

            

# adds cash onto existing user in the database
async def addCashOntoExistingUser(userID, cashAmount):
    try:
        connection_object, cursor = get_connection()
    except: pass
    finally:
        if connection_object.is_connected():
            
            prevCash = (await getExistingUser(userID))[1]

            sql = f"UPDATE currency_data SET cash = '{str(int(prevCash)+cashAmount)}' WHERE GuildedID ='{userID}'"
            cursor.execute(sql)
            connection_object.commit()
            
            cursor.close()
            connection_object.close()

# creates a new row in the database for the user - adds the cash into it
async def addCashOntoNewUser(userID, cashAmount):
    try:
        connection_object, cursor = get_connection()
    except: pass
    finally:
        if connection_object.is_connected():
            sql = "INSERT INTO currency_data (GuildedID, Cash) VALUES (%s, %s)"
            val = (userID, cashAmount)
            cursor.execute(sql, val)
            connection_object.commit()
            
            cursor.close()
            connection_object.close()

@client.event
async def on_message(message):
    if message.author.bot == False and message.author != client.user:
        
        # configures cooldown
        msgTime = time.time()
        prevTime = earningTimeoutDict.get(message.author.id) or msgTime - 15
        elapsedTime = msgTime - prevTime

        # if the user hasn't chatted within the last 15 seconds
        if elapsedTime >= 15:
            
            # if user doesnt exist in the database
            if await getExistingUser(message.author.id) == False:

                # creates a new row for them with the cash they earnt
                await addCashOntoNewUser(message.author.id, random.randint(10, 25))

            # if the user does exist in the database
            else:

                # adds users cash to their row in the database
                await addCashOntoExistingUser(message.author.id, random.randint(10, 25))

            # sets the last time they chatted in the timeout dict
            earningTimeoutDict[message.author.id] = msgTime

    if message.content == "!balance":

        cash = (await getExistingUser(message.author.id))[1]

        await message.reply(f"You have {cash} Cash!")

# runs bot
client.run('tink7239@gmail.com', '322005Bday*')

