import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from datetime import datetime
import file_manager as fm

DISPLAY_NAMES = {
    'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P',
    'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L',
    'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M',
    'grave': '`', 'minus': '-', 'equal': '=',
    'bracketleft': '[', 'bracketright': ']', 'backslash': '\\',
    'semicolon': ';', 'apostrophe': "'", 'comma': ',', 'period': '.', 'slash': '/',
    'Escape': 'Esc', 'Return': 'Enter', 'BackSpace': 'Back',
    'Caps_Lock': 'Caps', 'Tab': 'Tab', 'space': 'Space',
    'Shift_L': 'Shift',
    'Control_L': 'Ctrl', 'Control_R': 'Ctrl',
    'Alt_L': 'Alt', 'Alt_R': 'Alt',
    'Prior': 'PgUp', 'Next': 'PgDn', 'Insert': 'Ins', 'Delete': 'Del',
    'Up': '↑', 'Down': '↓', 'Left': '←', 'Right': '→', 
}

CYR_TO_LAT = {
    'Cyrillic_shorti': 'q', 'Cyrillic_tse': 'w', 'Cyrillic_u': 'e', 
    'Cyrillic_ka': 'r', 'Cyrillic_ie': 't', 'Cyrillic_en': 'y', 
    'Cyrillic_ghe': 'u', 'Cyrillic_sha': 'i', 'Cyrillic_shcha': 'o', 
    'Cyrillic_ze': 'p', 'Cyrillic_ha': '[', 'Cyrillic_hardsign': ']',
    'Cyrillic_ef': 'a', 'Cyrillic_yeru': 's', 'Cyrillic_ve': 'd',
    'Cyrillic_a': 'f', 'Cyrillic_pe': 'g', 'Cyrillic_er': 'h',
    'Cyrillic_o': 'j', 'Cyrillic_el': 'k', 'Cyrillic_de': 'l',
    'Cyrillic_zhe': ';', 'Cyrillic_e': "'",
    'Cyrillic_ya': 'z', 'Cyrillic_che': 'x', 'Cyrillic_es': 'c',
    'Cyrillic_em': 'v', 'Cyrillic_i': 'b', 'Cyrillic_te': 'n',
    'Cyrillic_softsign': 'm', 'Cyrillic_be': ',', 'Cyrillic_yu': '.',
    'Cyrillic_io': '`',
}

class KeyTesterApp:
    def __init__(self, root):
        self.root = root
        root.title("Тестер клавиатуры")
        try:
            self.root.iconbitmap("icon.ico")
        except tk.TclError:
            pass

        self.root.option_add("*tearOff", False)
        self.main_menu = tk.Menu(root)
        
        self.file_menu = tk.Menu(self.main_menu)
        self.file_menu.add_command(label="Новый тест", command=self.reset_test)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Сохранить отчет...", command=self.save_check)
        self.file_menu.add_command(label="Открыть отчет...", command=self.open_check)
        self.file_menu.add_command(label="Удалить отчет...", command=self.delete_check)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Закрыть", command=self.root.destroy)
        self.main_menu.add_cascade(label="Файл", menu=self.file_menu)
        
        self.form_menu = tk.Menu(self.main_menu)
        self.main_menu.add_cascade(label="Форм-фактор", menu=self.form_menu)

        def click_info():
            messagebox.showinfo("Информация", "KeyTester - 0.1")
        self.main_menu.add_cascade(label="Инфо", command=click_info)

        root.config(menu=self.main_menu)
        self.root.bind_all("<F10>", lambda e: "break")

        self.main_frame = tk.Frame(root, bg="#2c3e50", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.button_widgets = {}
        self.pressed = {}
        self.current_layout_name = None
        self.KEY_MAP = {}
        self.layouts = {}

        self.load_available_layouts()

        if self.layouts:
            first_key = list(self.layouts.keys())[0]
            self.set_layout(first_key)

        root.bind("<KeyPress>", self.key_press)
        root.bind("<KeyRelease>", self.key_release)

    def load_available_layouts(self):
        names = fm.get_available_layouts()
        for name in names:
            try:
                self.layouts[name] = fm.load_layout(name)
                self.form_menu.add_command(
                    label=name, 
                    command=lambda n=name: self.set_layout(n)
                )
            except Exception as e:
                print(f"Ошибка загрузки {name}: {e}")

    def set_layout(self, name):
        if name not in self.layouts:
            return
        self.current_layout_name = name
        self.KEY_MAP = self.layouts[name]
        self.redraw_keyboard()

    def redraw_keyboard(self):
        for lbl in self.button_widgets.values():
            lbl.destroy()
        self.button_widgets.clear()
        self.pressed.clear()
        self.create_keyboard()

    def create_keyboard(self):
        if not self.KEY_MAP:
            return

        for keysym, coords in self.KEY_MAP.items():
            row = int(coords[0])
            col = int(coords[1])
            width = int(coords[2])
            height = int(coords[3]) if len(coords) > 3 else 1
            
            display_text = DISPLAY_NAMES.get(keysym, keysym)
            
            label = tk.Label(
                self.main_frame,
                text=display_text,
                font=("Arial", 9, "bold"),
                bg="#ecf0f1", fg="#2c3e50",
                relief="raised", bd=2,
                height=2,
                width=4,
            )
            label.grid(row=row, column=col, columnspan=width, rowspan=height,
                       sticky="nsew", padx=4, pady=4)
            self.button_widgets[keysym] = label

        for x in range(36):
            self.main_frame.grid_columnconfigure(x, weight=1, minsize=25)

    def key_press(self, event):
        keysym = event.keysym
        
        # Игнорируем правый Shift
        if keysym == "Shift_R":
            return
            
        if len(keysym) == 1 and keysym.isalpha():
            keysym = keysym.lower()
            
        # Обработка кириллицы (в том числе с зажатым Shift)
        if keysym.lower() in CYR_TO_LAT:
            keysym = CYR_TO_LAT[keysym.lower()]
            
        if keysym in self.button_widgets:
            self.pressed[keysym] = True
            self.button_widgets[keysym].configure(
                bg="#A63928", fg="white", relief="sunken")

    def key_release(self, event):
        keysym = event.keysym
        
        # Костыль для бага Windows с отпусканием правого Alt и Ctrl
        if keysym == "Alt_L" and "Alt_R" in self.pressed:
            keysym = "Alt_R"
        elif keysym == "Control_L" and "Control_R" in self.pressed:
            keysym = "Control_R"
            
        if keysym == "Shift_R":
            return
            
        if len(keysym) == 1 and keysym.isalpha():
            keysym = keysym.lower()
            
        # Обработка кириллицы (в том числе с зажатым Shift)
        if keysym.lower() in CYR_TO_LAT:
            keysym = CYR_TO_LAT[keysym.lower()]
            
        if keysym in self.button_widgets:
            self.pressed.pop(keysym, None)
            self.button_widgets[keysym].configure(
                bg="#FDAA9D", fg="#2c3e50", relief="raised"
            )

    def reset_test(self):
        for keysym, label in self.button_widgets.items():
            label.configure(bg="#ecf0f1", fg="#2c3e50", relief="raised")
        self.pressed.clear()
        messagebox.showinfo("Сброс", "Все клавиши сброшены в исходное состояние.")

    def save_check(self):
        if not self.current_layout_name:
            messagebox.showwarning("Внимание", "Раскладка не загружена. Нечего сохранять.")
            return

        model = simpledialog.askstring("Сохранение", "Введите модель клавиатуры (например, Logitech K120):")
        if not model:
            return
        
        comment = simpledialog.askstring("Комментарий", "Комментарий к тесту (необязательно):")

        check_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "layout": self.current_layout_name,
            "pressed_keys": list(self.pressed.keys()),
            "comment": comment or ""
        }

        try:
            filename = fm.save_check(check_data)
            messagebox.showinfo("Успех", f"Отчет сохранен:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def open_check(self):
        fm.ensure_dirs()
        filepath = filedialog.askopenfilename(
            initialdir=fm.CHECKS_DIR,
            title="Выберите отчет",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if not filepath:
            return

        try:
            data = fm.load_check(filepath)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Отчет: {data.get('model', 'Без модели')}")
        win.geometry("500x550")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Дата теста:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        tk.Label(win, text=data.get('date', ''), bg="#f0f0f0").pack(anchor="w", padx=10)

        tk.Label(win, text="Модель клавиатуры:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        entry_model = tk.Entry(win, width=40)
        entry_model.insert(0, data.get('model', ''))
        entry_model.pack(anchor="w", padx=10)

        tk.Label(win, text="Форм-фактор:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        tk.Label(win, text=data.get('layout', 'Неизвестно'), bg="#f0f0f0").pack(anchor="w", padx=10)

        tk.Label(win, text="Залипшие клавиши:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        stuck_text = ', '.join(data.get('pressed_keys', [])) or "Нет"
        tk.Label(win, text=stuck_text, bg="#f0f0f0", fg="#A63928").pack(anchor="w", padx=10)

        tk.Label(win, text="Комментарий:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        text_comment = tk.Text(win, height=6, width=50)
        text_comment.insert("1.0", data.get('comment', ''))
        text_comment.pack(anchor="w", padx=10, pady=(0, 10))

        def save_changes():
            data['model'] = entry_model.get().strip()
            data['comment'] = text_comment.get("1.0", "end-1c").strip()

            try:
                fm.update_check(filepath, data)
                messagebox.showinfo("Успех", "Изменения сохранены!", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}", parent=win)

        btn_save = tk.Button(win, text="Сохранить изменения", command=save_changes, 
                             bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
        btn_save.pack(pady=10)

    def delete_check(self):
        fm.ensure_dirs()
        filepath = filedialog.askopenfilename(
            initialdir=fm.CHECKS_DIR,
            title="Выберите отчет для удаления",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if not filepath:
            return
            
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить отчет?\n{os.path.basename(filepath)}"):
            try:
                fm.delete_check(filepath)
                messagebox.showinfo("Успех", "Отчет удален.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyTesterApp(root)
    root.mainloop()