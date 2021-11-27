import re
import urllib.request
import json
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, CallbackContext, Filters
from bs4 import BeautifulSoup

default_path_bike_json_file = 'bike.json'
default_path_config_json_file = 'config.json'
default_log_file = 'log.txt'

bike_config = {}
config = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename=default_log_file,
    filemode='a'
)

logger = logging.getLogger(__name__)

NAME, SIZE, LINK = range(3)
NAME_DELETE = range(1)


def read_json_file(path):
    logger.info("Read json file %s", path)
    with open(path) as f:
        return json.load(f)


def write_json_file(data, path):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
    logger.info("Write json file %s with data: %s", path, data)


def check_bikes():
    bike_data = bike_config['bikes']
    html_config = config['html']

    for name_bike, data in bike_data.items():

        webUrl = urllib.request.urlopen(data['link'])

        data['availability'] = {}
        data['link_status'] = str(webUrl.getcode())
        data['your_size'] = False

        htmlText = webUrl.read()

        soup = BeautifulSoup(htmlText, 'html.parser')
        for link in soup.find_all(html_config['ship_tag']['tag'], class_=html_config['ship_tag']['class']):
            size = link.find(html_config['size_tag']['tag'], class_=html_config['size_tag']['class']).getText().replace(
                " ", "").replace("\n", "")

            if re.search(size, data['size'], re.IGNORECASE):
                data['your_size'] = True
                availability = link.find(html_config['availabilityMessage_tag']['tag'],
                                         class_=html_config['availabilityMessage_tag']['class'])
                if availability is None:
                    startShipDate = link.find(html_config['date_tag']['tag'],
                                              class_=html_config['date_tag']['class_start_date']).getText()
                    endShipDate = link.find(html_config['date_tag']['tag'],
                                            class_=html_config['date_tag']['class_end_date']).getText()
                    availabilityText = "Ship Date : " + startShipDate + " to " + endShipDate
                else:
                    availabilityText = availability.getText().replace(" ", "").replace("\n", "")
                data['availability'] = availabilityText


def bike_avaible_list_to_str():
    str = "Available Bike: \n"
    buy = False
    bike_data = bike_config['bikes']
    for name_bike, data in bike_data.items():
        if data["your_size"]:
            buy = True
            str = str + name_bike + "\n"
            str = str + data["link"] + "\n"
            str = str + data["size"] + " : " + data["availability"] + "\n"
    if buy:
        return str
    else:
        return None


def bike_list_to_str():
    if len(bike_config['bikes']) > 0:
        str = "Bike List: \n"
        bike_data = bike_config['bikes']
        for name_bike, data in bike_data.items():
            str = str + " Name: " + name_bike + "\n"
            str = str + " Link: " + data["link"] + "\n"
            str = str + " Size: " + data["size"] + "\n"
    else:
        str = "No bike in list"
    return str


def help_bot_command(update: Update, context: CallbackContext) -> None:
    str = "/list to see the list of bikes to check \n" \
          "/add to add new bike to check \n" \
          "/remove to remove a bike from the list \n"
    update.message.reply_text(str)


def check_bike_bot_callback(context: CallbackContext):
    logger.info("Check Bike..")
    if len(bike_config['bikes']) > 0:
        check_bikes()
        logger.info(bike_config['bikes'])
        strtosend = bike_avaible_list_to_str()
        if strtosend is not None:
            logger.info("Send bike Update...")
            context.bot.send_message(chat_id=config['params']['userid'], text=strtosend)
        else:
            logger.info("No bike avaible")
    else:
        logger.info("No bike in dictionary")


def add_bike_link_bot_command(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == config['params']['userid']:
        logger.info("%s add new bike command", update.effective_user.full_name)
        update.message.reply_text('Bike Name:')
        return NAME
    else:
        logger.error("%s send command /add but not have permission", update.effective_user.full_name)
        update.message.reply_text('Action Not permited')
        return ConversationHandler.END


def bike_name_bot(update: Update, context: CallbackContext) -> None:
    logger.info("%s add name bike:  %s", update.effective_user.full_name, update.message.text)
    bike_config['bikes'][update.message.text] = {}
    context.user_data['bike_name'] = update.message.text
    update.message.reply_text('Bike Size:')
    return SIZE


def bike_size_bot(update: Update, context: CallbackContext) -> None:
    logger.info("%s add size bike:  %s", update.effective_user.full_name, update.message.text)
    bike_config['bikes'][context.user_data['bike_name']]['size'] = update.message.text
    update.message.reply_text('Bike Link:')
    return LINK


def bike_link_bot(update: Update, context: CallbackContext) -> None:
    logger.info("%s add link bike:  %s", update.effective_user.full_name, update.message.text)
    bike_config['bikes'][context.user_data['bike_name']]['link'] = update.message.text
    update.message.reply_text('add')
    logger.info(bike_config)
    write_json_file(bike_config, default_path_bike_json_file)
    return ConversationHandler.END


def bike_list_bot(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == config['params']['userid']:
        logger.info("%s list command", update.effective_user.full_name)
        update.message.reply_text(bike_list_to_str())
    else:
        logger.error("%s send command /list but not have permission", update.effective_user.full_name)
        update.message.reply_text('Action Not permited')


def remove_bike_bot_start(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == config['params']['userid']:
        logger.info("%s send /remove command ", update.effective_user.full_name)
        update.message.reply_text('Bike Name:')
        return NAME_DELETE
    else:
        logger.error("%s send command /remove but not have permission", update.effective_user.full_name)
        update.message.reply_text('Action Not permited')
        return ConversationHandler.END


def remove_bike_bot_end(update: Update, context: CallbackContext) -> None:
    bike_name = update.message.text
    logger.info("%s send command /remove with %s", update.effective_user.full_name, bike_name)
    if bike_name in bike_config['bikes'].keys():
        bike_config['bikes'].pop(bike_name)
        write_json_file(bike_config, default_path_bike_json_file)
        update.message.reply_text('Deleted')
        logger.info("%s, %s bike deleted", update.effective_user.full_name, bike_name)
    else:
        logger.info("%s send /remove command with %s but not exist", update.effective_user.full_name, bike_name)
        update.message.reply_text('Not present')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("%s cancel", update.effective_user.full_name)
    update.message.reply_text('Cancel')
    return ConversationHandler.END


def main() -> None:
    logger.info("Start bot")
    print("Start bot")
    updater = Updater(config['params']['token'])
    j = updater.job_queue
    job_minute = j.run_repeating(check_bike_bot_callback, interval=config['params']['time'], first=1)
    dispatcher = updater.dispatcher
    add_bike_con_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_bike_link_bot_command)],
        states={
            NAME: [MessageHandler(Filters.text, bike_name_bot)],
            SIZE: [MessageHandler(Filters.text, bike_size_bot)],
            LINK: [MessageHandler(Filters.all, bike_link_bot)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    remove_bike_con_handler = ConversationHandler(
        entry_points=[CommandHandler('remove', remove_bike_bot_start)],
        states={
            NAME_DELETE: [MessageHandler(Filters.text, remove_bike_bot_end)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(add_bike_con_handler)
    dispatcher.add_handler(remove_bike_con_handler)
    dispatcher.add_handler(CommandHandler("help", help_bot_command))
    dispatcher.add_handler(CommandHandler("list", bike_list_bot))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    bike_config = read_json_file(default_path_bike_json_file)
    config = read_json_file(default_path_config_json_file)
    main()
