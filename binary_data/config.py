# configurations
import logging

LOG_LEVEL = logging.DEBUG
LOG_FILE = 'logs/app.log'
LOG_FILE_BACKUP_COUNT = 10
LOG_FILE_MAX_SIZE = 1 * 1024 * 1024

# LLM_URL = "http://129.80.164.69:8888/" # vm5
LLM_URL = "http://135.237.153.168:8888/" # A100
# LLM_URL = "http://129.80.129.149:8888/" #vm6
# LLM_URL = "http://129.80.151.216:8888/"  # vm4

LLM_ENDPOINT = '/api/train/llm/rag/invoke'
PROMPT = 'prompts/binary_clusters.txt'
