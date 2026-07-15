import asyncio
from netdiag.utils import *

async def main():
    print("Время:", now())
    print()
    print("curl:", command_exists("curl"))
    print("dig:", command_exists("dig"))
    print()
    ok, text = await run_command(["uname", "-a"])
    print(ok)
    print(text)
    print()
    print(mask_ip("185.123.45.67"))
    print()
    ok, page = await http_get("https://api.ipify.org")
    print(ok)
    print(page)

if __name__ == "__main__":
    asyncio.run(main())