
from settings import settings
from processor import Processor
from _queue import Queue

myprocessor = Processor()
queue = Queue()

def main():
    
    queue.register_consumer_callback(myprocessor.process_data)

    queue.channel.start_consuming()
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        queue.channel.stop_consuming()
    finally:
        queue.gracefully_shutdown()
