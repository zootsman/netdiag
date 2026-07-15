#!/usr/bin/env python3

import asyncio
import argparse
import sys
from netdiag.menu import show_menu
from netdiag.core import run, AVAILABLE_CHECKS

def main():
    parser = argparse.ArgumentParser(
        description="NetDiag: Утилита для комплексной диагностики сети.",
        epilog="Если аргументы не указаны, будет запущено интерактивное меню."
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Запустить все доступные проверки.'
    )

    for check_name, check_info in AVAILABLE_CHECKS.items():
        parser.add_argument(
            f'--{check_name}',
            action='store_true',
            help=check_info['desc']
        )
    
    # Если аргументов больше одного (имя скрипта + аргументы)
    if len(sys.argv) > 1:
        args = parser.parse_args()
        checks_to_run = []
        
        if args.all:
            asyncio.run(run())
            return

        for check_name in AVAILABLE_CHECKS:
            if getattr(args, check_name.replace('-', '_')): # argparse заменяет - на _
                checks_to_run.append(check_name)

        if checks_to_run:
            asyncio.run(run(checks_to_run=checks_to_run))
        else:
            # Если был передан неизвестный флаг или флаг без действия
            print("Не выбрано ни одной проверки. Используйте --help для справки.")
            
    else:
        # Если запуск без аргументов, показать интерактивное меню
        asyncio.run(show_menu())

if __name__ == "__main__":
    main()
