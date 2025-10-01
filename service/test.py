import requests
import aiohttp
import asyncio
import httpx

url = 'http://127.0.0.1:8000/shutdown'

response = requests.post(url=url, json={'shutdown': True, 'wait': 2.5})
print(response.json())
