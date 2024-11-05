import httpx
import asyncio
import os
from pathlib import Path

async def check_services():
    services = {
        'Ollama': 'http://localhost:11434/api/tags',
        'Tika': 'http://localhost:9998/tika',
        'SpaCy': 'http://localhost:8080/status',
    }
    
    async with httpx.AsyncClient() as client:
        for service, url in services.items():
            try:
                response = await client.get(url)
                print(f"✅ {service}: OK")
            except Exception as e:
                print(f"❌ {service}: Failed - {str(e)}")

    # Verificar diretórios
    dirs = ['uploads', 'results', 'logs']
    for dir_name in dirs:
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print(f"✅ Directory {dir_name}: OK")
        else:
            print(f"❌ Directory {dir_name}: Not found")

if __name__ == "__main__":
    asyncio.run(check_services())