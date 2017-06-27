SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BOT_DIR=/opt/stack/vk_bot

cd $BOT_DIR

function log() {
    echo $1 | ts >> log.log
}

# Stop the bot process.
BOT_PID=$(ps aux | grep python | grep vkontakte-bot | head -1 | awk '{print $2}')

if [ ! -z $BOT_PID ]; then
  kill -9 $BOT_PID
  log "Bot PID=$BOT_PID is killed."
else
  log "Bot process doesn't exist. Just start a new one."
fi

# Save logs.
cat vk_bot.log >> vk_bot.bak

# Start a new bot process.
# vk - screen name
# stuff - screen command
# vkontakte-bot - run vk-bot
# echo -ne \015 emulates 'Enter'
screen_name=vk
log "Starting a new bot process..."

scr=$(screen -ls | grep vk)
if [ -z $scr ]
then
  log "Creating a new '$screen_name' screen..."
  screen -dmS $screen_name
  sleep 1
fi

screen -S $screen_name -X stuff 'vkontakte-bot'`echo -ne '\015'`

sleep 1
BOT_PID=$(ps aux | grep vkontakte-bot | head -1 | awk '{print $2}')

if [ ! -z $BOT_PID ]; then
  log "New bot process (PID=$BOT_PID) is started."
else
  log "New bot process is not started!"
fi

log ""
