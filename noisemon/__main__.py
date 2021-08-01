import uvicorn
from multiprocessing import Process
from settings import settings
from data_processing.processor import Processor
from data_retrieval.telegram import TelegramDataSource
import zmq

# context = zmq.Context()

myprocessor = Processor()
mytelegramsource = TelegramDataSource()

if __name__ == '__main__':
    try:
        myprocessor_process = Process(target=myprocessor.run, name="ProcessorSubprocess")
        myprocessor_process.start()

        mytelegramsource_process = Process(target=mytelegramsource.run, name="TelegramSubprocess")
        mytelegramsource_process.start()


        uvicorn.run(
            "app:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.ENVIRONMENT != "production"
        )
    finally:
        myprocessor_process.close()
        mytelegramsource_process.close()