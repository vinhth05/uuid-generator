import uuid
import threading
import queue
from typing import Callable, Optional
from utils.logger import logger
from config import NAMESPACE_MAP, CHUNK_SIZE

class UUIDGenerator:
    def __init__(self):
        self._cancel_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._pause_flag.set() # Set means NOT paused
        
    def generate_worker(
        self,
        version: str,
        quantity: int,
        namespace_type: str,
        custom_name: str,
        output_queue: queue.Queue,
        progress_callback: Callable[[int, int], None],
        completion_callback: Callable[[bool], None]
    ):
        """Worker function to generate UUIDs in a separate thread."""
        logger.info(f"Starting generation of {quantity} UUID v{version}s")
        self._cancel_flag.clear()
        self._pause_flag.set()
        
        generated_count = 0
        namespace_uuid = NAMESPACE_MAP.get(namespace_type, uuid.NAMESPACE_DNS)
        
        try:
            while generated_count < quantity:
                if self._cancel_flag.is_set():
                    logger.info("Generation cancelled.")
                    break
                    
                self._pause_flag.wait() # Block if paused
                
                # Calculate chunk size
                current_chunk = min(CHUNK_SIZE, quantity - generated_count)
                chunk_results = []
                
                # Generate chunk
                for _ in range(current_chunk):
                    if version == "1":
                        u = str(uuid.uuid1())
                    elif version == "3":
                        u = str(uuid.uuid3(namespace_uuid, custom_name))
                    elif version == "4":
                        u = str(uuid.uuid4())
                    elif version == "5":
                        u = str(uuid.uuid5(namespace_uuid, custom_name))
                    else:
                        u = str(uuid.uuid4())
                        
                    chunk_results.append(u)
                
                generated_count += current_chunk
                
                # Put chunk in queue for the consumer (UI/Exporter)
                output_queue.put(chunk_results)
                progress_callback(generated_count, quantity)
                
            completion_callback(self._cancel_flag.is_set())
            
        except Exception as e:
            logger.error(f"Error during generation: {e}", exc_info=True)
            completion_callback(False)
            
    def start_generation(self, version, quantity, namespace_type, custom_name, output_queue, progress_cb, completion_cb):
        thread = threading.Thread(
            target=self.generate_worker,
            args=(version, quantity, namespace_type, custom_name, output_queue, progress_cb, completion_cb),
            daemon=True
        )
        thread.start()
        return thread
        
    def cancel(self):
        self._cancel_flag.set()
        self._pause_flag.set() # Unpause to allow thread to exit
        
    def pause(self):
        self._pause_flag.clear()
        
    def resume(self):
        self._pause_flag.set()
