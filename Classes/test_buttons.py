import os
import sys
import msvcrt  # Для Windows. Для Linux используйте `keyboard` или `curses`.
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

def clear_console():
    """Очищает консоль."""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_buttons(selected):
    """Отрисовывает две кнопки в консоли с цветом для выбранной кнопки."""
    clear_console()
    
    # Выбранная кнопка будет зеленой, остальные — обычного цвета
    button1 = f"{Fore.GREEN}[X]{Style.RESET_ALL}" if selected == 1 else "[ ]"
    button2 = f"{Fore.GREEN}[X]{Style.RESET_ALL}" if selected == 2 else "[ ]"
    
    print("Выберите кнопку:")
    print(f"1. {button1} Кнопка 1")
    print(f"2. {button2} Кнопка 2")

def main():
    selected = 1  # Начальная выбранная кнопка
    while True:
        draw_buttons(selected)
        print("\nИспользуйте стрелки для выбора, Enter для подтверждения.")

        # Получаем нажатую клавишу
        key = msvcrt.getch()  # Для Windows
        if key == b'\r':  # Если нажата клавиша Enter
            print(f"\nВы выбрали кнопку {selected}!")
            break
        elif key in (b'H', b'P'):  # Стрелка вверх (H) или вниз (P)
            selected = 1 if selected == 2 else 2

if __name__ == "__main__":
    main()