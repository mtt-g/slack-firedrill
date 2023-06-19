import os
import logging
import yaml
import sys

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

def configure_logging():
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%M-%d %H:%M:%S",
        level=os.environ.get("FIREDRILL_LOG_LEVEL", "WARN").upper()
    )
    return logging.getLogger("Firedrill")

logger = configure_logging()

try:
   FIREDRILL_APP_TOKEN = os.environ["FIREDRILL_APP_TOKEN"]
except KeyError: 
   logger.error("Environment variable not set: FIREDRILL_APP_TOKEN")
   sys.exit(1)

try:  
   FIREDRILL_BOT_TOKEN = os.environ["FIREDRILL_BOT_TOKEN"]
except KeyError: 
   logger.error("Environment variable not set: FIREDRILL_BOT_TOKEN")
   sys.exit(1)

app = App(token=os.environ.get("FIREDRILL_BOT_TOKEN"))

try:
    f = open("config.yaml", "r")
    with f as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
except OSError:
    logger.error("Could not read config.yaml")
    sys.exit(1)

if config is None:
    logger.error("No configuration present or could not be read")
    sys.exit(1)
else:
    logger.info(f'Running with Config: {config}')

def get_username(role):
    return config['roles'][role]['username']

def get_icon_emoji(role):
    return config['roles'][role]['icon_emoji']

@app.command("/fd")
def echo(ack, command, respond, say):

    logger.info(f'New request received: {command}')

    global username
    global icon_emoji
    global role
    global text

    role = "fd"

    response = {}

    params = command['text'].split(" ", 2)
    
    directive = params[0]

    match directive:
        
        case "help":
            
            response["text"] = """
The `/fd` command helps you to run your firedrill:\n

To assume a role and send a message, use the following command:\n
`fd say [role] [message]`\n

To start or stop the fire drill, use the following command:\n
`/fd [start|stop]`\n

To ping the bot to ensure it's responding, use the following command:\n
`/fd wake`\n

*Available Roles:*\n
alertmanager, cloudwatch, cx, director, firedrill, fd, hosting, ic, info, infra, log, logline, logs, nagios, networks, pagerduty, pd, prodops, techops, techdesk, secops, security, slm, sla, sd, servicedesk, trader, trading, twitter, warn

*Example Usage:*\n
`/fd say info Today's firedrill takes place in NPS`\n
`/fd say pagerduty Calling out <@[member id]> `\n
`/fd start`\n
`/fd stop`\n
"""

            respond(response)

        case "say":

            response['channel_id'] = command['channel_id']
            response["icon_emoji"] = get_icon_emoji(params[1])
            response["text"] = params[2]
            response["username"] = get_username(params[1])

            say(response)

        case "start":
            
            response['channel_id'] = command['channel_id']
            response["username"] = get_username(role)
            response["text"] = "Firedrill *Start*"

            say(response)

        case "stop":

            response['channel_id'] = command['channel_id']
            response["username"] = get_username(role)
            response["text"] = "Firedrill *Stop*"

            say(response)

        case "wake":

            response["text"] = "I'm awake :zzz:"
            respond(response)

        case _:

            response["text"] = "Hmm? I don't understand the request. Try again?"
            respond(response)
    
    ack()

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["FIREDRILL_APP_TOKEN"]).start()