import asyncio
from dotenv import load_dotenv
load_dotenv()
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon import events

from noisemon.settings import settings

async def main():
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    client = TelegramClient('account_initialization_session', api_id, api_hash)
    await client.start()

    all_subscriptions_map = dict()
    async for dialog in client.iter_dialogs():
        if not dialog.is_group and dialog.is_channel:
            entity = await client.get_entity(dialog.id)
            username = entity.username
            if username == "telegram":
                continue
            print(dialog.name, dialog.id, username)
            all_subscriptions_map[username] = entity
        
    target_subscriptions = set()
    for channel in settings.TelegramConfig.get_channels_list():
        target_subscriptions.add(channel)
        print(channel)
        
    # 2. Compare with target state list
    shall_be_subscribed = target_subscriptions.difference(all_subscriptions_map.keys())
    shall_be_unsubscribed = set(all_subscriptions_map.keys()).difference(target_subscriptions)
        
    # 3. Actualize account state
    print("This channels shall be added: ", shall_be_subscribed)
    for channel in shall_be_subscribed:
        await client(JoinChannelRequest(channel))

    print("This channels shall be quit: ", shall_be_unsubscribed)
    for username in shall_be_unsubscribed:
        await client(LeaveChannelRequest(all_subscriptions_map[username]))
    
    await client.disconnect()
    print("Done!")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
    loop.close()