import uvicorn
from multiprocessing import Process
from settings import settings
from data_processing.processor import Processor
from data_retrieval.telegram_data_source import TelegramDataSource
import zmq
import asyncio

# context = zmq.Context()
def main():
    myprocessor = Processor()
    mytelegramsource = TelegramDataSource()
    

    try:
        
        myprocessor_process = Process(target=myprocessor.run, name="ProcessorSubprocess")
        myprocessor_process.start()

        mytelegramsource_process = Process(target=mytelegramsource.run, name="TelegramSubprocess")
        mytelegramsource_process.start()

        # loop.subprocess_exec
        # loop.run_until_complete(initialize_account())


        uvicorn.run(
            "app:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.ENVIRONMENT != "production"
        )
    finally:
        myprocessor_process.close()
        mytelegramsource_process.close()
        myprocessor.db.close()


if __name__ == '__main__':
    main()
