import requests
import urllib,json
from flask import Flask, request
from ciscosparkapi import CiscoSparkAPI, Webhook
import os

#Constants
giphyapikey = os.environ['GIPHY_KEY']
rating = 'pg13'


# Initialize the environment
app = Flask(__name__)             # Create the web application instance
spark_api = CiscoSparkAPI()             # Create the Cisco Spark API connection object
port = int(os.environ["PORT"])

@app.route('/', methods=['GET', 'POST'])
def sparkwebhook():
    """Processes incoming requests to the '/sparkwebhook' URI."""
    if request.method == 'GET':
        return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Spark Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>Your Flask web server is up and running!</strong>
                   </p>
                   </body>
                   </html>
                """)
    elif request.method == 'POST':
        """Respond to inbound webhook JSON HTTP POST from Cisco Spark."""

        json_data = request.json
        print("\n")
        print("WEBHOOK POST RECEIVED:")
        print(json_data)
        print("\n")

        webhook_obj = Webhook(json_data)                                       # Create a Webhook object from the JSON data
        room = spark_api.rooms.get(webhook_obj.data.roomId)                    # Get the room details
        message = spark_api.messages.get(webhook_obj.data.id)                  # Get the message details
        person = spark_api.people.get(message.personId)                        # Get the sender's details

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        print("MESSAGE '{}'\n".format(message.text))

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = spark_api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            return 'OK'

        else:
            # Message was sent by someone else; parse message and respond.
            tag = message.text.replace(" ","+")
            data = json.loads(urllib.request.urlopen("http://api.giphy.com/v1/gifs/random?tag=" + tag + "&api_key=" + giphyapikey + "&rating=" + rating).read())
            api.message.create(roomId=message.roomId, files=data['data']['image_url'])             # Post the gif!
            return 'OK'


# Start the Flask web server
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=port)
