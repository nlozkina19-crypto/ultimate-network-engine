import time
import asyncio
import aiohttp
import sys
import json
from datetime import datetime

# Цвета для терминала
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

SERVERS = {
    "USA (Amazon East)": "https://ec2.us-east-1.amazonaws.com/ping",
    "EU (Frankfurt)": "https://ec2.eu-central-1.amazonaws.com/ping",
    "Asia (Singapore)": "https://ec2.ap-southeast-1.amazonaws.com/ping",
    "Cloudflare Edge": "https://1.1.1.1"
}
DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes=25000000"

class UltimateBenchmark:
    def __init__(self):
        self.data = {"timestamp": str(datetime.now()), "pings": {}, "speed": {}}

    async def fetch_ping(self, session, name, url):
        try:
            start = time.perf_counter()
            async with session.get(url, timeout=3) as resp:
                await resp.read()
                ms = (time.perf_counter() - start) * 1000
                color = Colors.GREEN if ms < 100 else Colors.YELLOW if ms < 250 else Colors.RED
                return name, ms, color
        except:
            return name, None, Colors.RED

    async def fetch_speed(self, session):
        try:
            start = time.perf_counter()
            async with session.get(DOWNLOAD_URL, timeout=15) as resp:
                data = await resp.read()
                dur = time.perf_counter() - start
                mbps = (len(data) / (1024*1024) * 8) / dur
                return round(mbps, 2)
        except:
            return None

    async def spinner(self, msg, event):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not event.is_set():
            sys.stdout.write(f"\r{Colors.CYAN}{frames[i % 10]}{Colors.END} {msg}...")
            sys.stdout.flush()
            await asyncio.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * 50 + "\r")

    async def run(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 ULTIMATE NETWORK ENGINE v5.0 (PRO){Colors.END}")
        print(f"{Colors.CYAN}{'='*45}{Colors.END}\n")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(force_close=True)) as session:
            # Тест Пинга
            ev = asyncio.Event()
            task = asyncio.create_task(self.spinner("Замер глобальной задержки", ev))
            p_res = await asyncio.gather(*[self.fetch_ping(session, n, u) for n, u in SERVERS.items()])
            ev.set()
            await task

            print(f"{Colors.BOLD}📍 ГЛОБАЛЬНЫЙ ОТКЛИК:{Colors.END}")
            for name, ms, col in p_res:
                val = f"{ms:.2f} ms" if ms else "TIMEOUT"
                print(f" {col}●{Colors.END} {name:.<25} {col}{val}{Colors.END}")
                self.data["pings"][name] = ms

            # Тест Скорости
            ev = asyncio.Event()
            task = asyncio.create_task(self.spinner("Тест пропускной способности", ev))
            speed = await self.fetch_speed(session)
            ev.set()
            await task

            if speed:
                self.data["speed"] = speed
                col = Colors.GREEN if speed > 100 else Colors.YELLOW
                print(f"\n{Colors.BOLD}⚡ СКОРОСТЬ: {col}{speed} Mbps{Colors.END}")

            # Сохранение в JSON (для профи)
            with open("result.json", "w") as f:
                json.dump(self.data, f, indent=4)
            
            print(f"\n{Colors.CYAN}{'='*45}{Colors.END}")
            print(f"✅ Готово! Результаты в {Colors.BOLD}result.json{Colors.END}")

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    try:
        asyncio.run(UltimateBenchmark().run())
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Прервано.{Colors.END}")
