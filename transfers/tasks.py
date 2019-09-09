from coldwallet.celery import app


is_running = False

@app.task
def worker_scan_transfers():
    print("Worker scans transfers")
    return True

@app.task
def worker_is_running():
    global is_running
    is_running_current = is_running
    is_running = True
    return is_running_current
