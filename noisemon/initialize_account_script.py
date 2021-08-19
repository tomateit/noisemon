from data_retrieval.telegram_data_source import TelegramDataSource
import asyncio

# context = zmq.Context()
async def initialize_account():
    

    mytelegramsource = TelegramDataSource()
    try:
        await mytelegramsource.connect_to_telegram()
        await mytelegramsource.initialize_account()


        print("Initialization complete")
    finally:

        await mytelegramsource.client.disconnect()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(initialize_account())
    loop.close()