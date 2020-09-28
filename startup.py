import uvicorn
import api

host = 'dev.skaphe.com'
port = 8000
log_level = 'info'

app = api.app

if __name__ == "__main__":
	uvicorn.run(app, host=host, port=port, log_level=log_level)