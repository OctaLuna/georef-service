import multiprocessing

bind = "127.0.0.1:8001"
workers = min((2 * multiprocessing.cpu_count()) + 1, 9)
worker_class = "uvicorn.workers.UvicornWorker"
preload_app = True  # loads GeoDataFrame in parent process; workers share it via copy-on-write
timeout = 30
keepalive = 5
