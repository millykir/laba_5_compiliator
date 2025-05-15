import re
import tkinter as tk
from tkinter import messagebox, filedialog, PhotoImage
from tkinter import ttk
import os

def update_line_numbers(text_area, line_numbers):
    """Обновление номеров строк."""
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete("1.0", tk.END)
    line_count = text_area.index(tk.END).split(".")[0]
    line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, int(line_count))))
    line_numbers.config(state=tk.DISABLED)

def on_text_change(event=None, text_area=None, line_numbers=None):
    """Обработчик изменения текста."""
    update_line_numbers(text_area, line_numbers)

def create_document():
    """Создание нового документа."""
    new_tab = ttk.Frame(notebook)
    notebook.add(new_tab, text="Новый документ")
    
    frame = tk.Frame(new_tab)
    frame.pack(fill=tk.BOTH, expand=True)
    
    line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0, border=0, background="lightgray", state=tk.DISABLED)
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)
    
    text_area = tk.Text(frame, undo=True, font=("Arial", selected_size.get()))
    text_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
    text_area.bind("<KeyRelease>", lambda event: on_text_change(event, text_area, line_numbers))

    new_tab.text_area = text_area
    new_tab.file_path = None
    
    update_line_numbers(text_area, line_numbers)

def open_document():
    """Открытие документа."""
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        new_tab = ttk.Frame(notebook)
        notebook.add(new_tab, text=file_path.split("/")[-1])
        
        frame = tk.Frame(new_tab)
        frame.pack(fill=tk.BOTH, expand=True)
        
        line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0, border=0, background="lightgray", state=tk.DISABLED)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        text_area = tk.Text(frame, undo=True, font=("Arial", selected_size.get()))
        text_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        text_area.bind("<KeyRelease>", lambda event: on_text_change(event, text_area, line_numbers))
        
        with open(file_path, "r", encoding="utf-8") as file:
            text_area.insert(tk.END, file.read())
        
        new_tab.text_area = text_area
        new_tab.file_path = file_path
        
        update_line_numbers(text_area, line_numbers)

def save_document():
    """Сохранить документ."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = current_tab.file_path
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
        else:
            save_document_as()

def save_document_as():
    """Сохранить документ с новым именем."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            notebook.tab(current_tab, text=file_path.split("/")[-1])
            current_tab.file_path = file_path

def update_font_size(*args):
    """Обновить размер шрифта в активной вкладке, не меняя размер окна."""
    size = selected_size.get()
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        current_tab.text_area.config(font=("Arial", size))

def get_active_text_area():
    """Получить текстовое поле активной вкладки."""
    current_tab = notebook.nametowidget(notebook.select())
    return current_tab.text_area if current_tab and hasattr(current_tab, "text_area") else None

def setup_hotkeys(root):
    root.bind("<Control-n>", lambda event: create_document())  
    root.bind("<Control-o>", lambda event: open_document())  
    root.bind("<Control-s>", lambda event: save_document())  
    root.bind("<Control-Shift-S>", lambda event: save_document_as())  
    root.bind("<Control-q>", lambda event: exit_program())  

    root.bind("<Control-z>", lambda event: undo(get_active_text_area()))  
    root.bind("<Control-y>", lambda event: redo(get_active_text_area()))  
    root.bind("<Control-x>", lambda event: cut_text(get_active_text_area()))  
    root.bind("<Control-c>", lambda event: copy_text(get_active_text_area()))  
    root.bind("<Control-v>", lambda event: paste_text(get_active_text_area()))  
    root.bind("<Control-a>", lambda event: select_all(get_active_text_area()))  


import re
import tkinter as tk
from tkinter import messagebox

# Глобальные переменные для тетрад
quadruples = []
temp_counter = 0

# Проверка на невалидные символы
def check_invalid_symbols(code):
    allowed_pattern = r"[a-zA-Z0-9_=\.\(\)\+\-\*/%\s;]"
    invalid_chars = re.findall(f"[^{allowed_pattern[1:-1]}]", code)
    return invalid_chars

# Лексический анализатор
def lexical_analyzer(code, file_path=None):
    invalid_chars = check_invalid_symbols(code)
    cleaned_code = re.sub(r"[^\w=\.\(\)\+\-\*/%\s;]", "", code)

    # Очистка таблицы перед добавлением новых данных
    for item in output_table.get_children():
        output_table.delete(item)

    if invalid_chars:
        output_table.insert("", "end", values=(
            "W001", "Удаление невалидных символов",
            ''.join(invalid_chars), "-", file_path or "–", "-"
        ))

    # Переходим к синтаксическому анализу
    errors = syntax_analyzer(cleaned_code)

    if errors:
        for err, position in errors:
            output_table.insert("", "end", values=(
                "E001", "Ошибка синтаксиса",
                err, position, file_path or "–", "1"
            ))
    else:
        output_table.insert("", "end", values=(
            "OK", "Успешно",
            "Ошибок не обнаружено", "-", file_path or "–", "1"
        ))

# Синтаксический анализатор методом рекурсивного спуска для присваивания
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def next_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, expected):
        if self.current_token == expected:
            self.next_token()
        else:
            self.errors.append((f"Ожидали '{expected}', встретили '{self.current_token}'", self.pos))

    def parse_assignment(self):
        if re.match(r"^[a-zA-Z_][a-zA-Z_0-9]*$", self.current_token):
            id_name = self.current_token
            self.match(id_name)
            if self.current_token == '=':
                self.match('=')
                temp = self.parse_E()
                if self.current_token == ';':
                    self.match(';')
                    quadruples.append(('=', temp, None, id_name))
                else:
                    self.errors.append(("Ожидали ';' в конце присваивания", self.pos))
            else:
                self.errors.append(("Ожидали '=' после идентификатора", self.pos))
        else:
            self.errors.append(("Ожидали идентификатор в начале присваивания", self.pos))

    def parse_E(self):
        temp = self.parse_T()
        return self.parse_A(temp)

    def parse_A(self, inherited):
        if self.current_token in ('+', '-'):
            op = self.current_token
            self.match(op)
            temp2 = self.parse_T()
            global temp_counter
            temp_counter += 1
            temp_name = f"t{temp_counter}"
            quadruples.append((op, inherited, temp2, temp_name))
            return self.parse_A(temp_name)
        else:
            return inherited  # ε

    def parse_T(self):
        temp = self.parse_O()
        return self.parse_B(temp)

    def parse_B(self, inherited):
        if self.current_token in ('*', '/'):
            op = self.current_token
            self.match(op)
            temp2 = self.parse_O()
            global temp_counter
            temp_counter += 1
            temp_name = f"t{temp_counter}"
            quadruples.append((op, inherited, temp2, temp_name))
            return self.parse_B(temp_name)
        else:
            return inherited  # ε

    def parse_O(self):
        if self.current_token == '(':
            self.match('(')
            temp = self.parse_E()
            self.match(')')
            return temp
        elif self.current_token == '-':
            self.match('-')
            if re.match(r"^[a-zA-Z_][a-zA-Z_0-9]*$|^\d+$", self.current_token):
                val = self.current_token
                self.match(val)
                global temp_counter
                temp_counter += 1
                temp_name = f"t{temp_counter}"
                quadruples.append(('-', val, None, temp_name))
                return temp_name
            else:
                self.errors.append((f"Ожидали идентификатор или число после '-', встретили '{self.current_token}'", self.pos))
                self.next_token()
                return "error"
        elif re.match(r"^[a-zA-Z_][a-zA-Z_0-9]*$|^\d+$", self.current_token):
            id_name = self.current_token
            self.match(id_name)
            return id_name
        else:
            self.errors.append((f"Ожидали идентификатор, число или '(' , встретили '{self.current_token}'", self.pos))
            self.next_token()
            return "error"

def show_quadruples(quadruples):
    if not quadruples:
        messagebox.showinfo("Тетрады", "Тетрады не найдены.")
        return

    output = "Тетрады:\n"
    for idx, (op, arg1, arg2, res) in enumerate(quadruples):
        output += f"{idx}: ({op}, {arg1}, {arg2}, {res})\n"

    messagebox.showinfo("Тетрады", output)

def syntax_analyzer(code):
    # Токенизация: разделяем по пробелам и спецсимволам
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z_0-9]*|\d+|[=;\+\-\*/\(\)]", code)

    # Очищаем глобальные данные
    global quadruples, temp_counter
    quadruples = []
    temp_counter = 0

    parser = Parser(tokens)
    parser.parse_assignment()

    if parser.current_token is not None:
        parser.errors.append((f"Лишний токен '{parser.current_token}' в конце", parser.pos))

    return parser.errors

# Вызов синтаксического анализа
def syntax_analysis():
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text = current_tab.text_area.get("1.0", tk.END).rstrip()
        file_path = getattr(current_tab, "file_path", "Без имени")
        lexical_analyzer(text, file_path)
        show_quadruples(quadruples)
    else:
        messagebox.showerror("Ошибка", "Нет активного документа!")



def undo(text_area):
    """Отменить действие."""
    if text_area:
        text_area.event_generate("<<Undo>>")

def redo(text_area):
    """Повторить действие."""
    if text_area:
        text_area.event_generate("<<Redo>>")

def cut_text(text_area):
    """Вырезать текст."""
    if text_area:
        text_area.event_generate("<<Cut>>")

def copy_text(text_area):
    """Копировать текст."""
    if text_area:
        text_area.event_generate("<<Copy>>")

def paste_text(text_area):
    """Вставить текст."""
    if text_area:
        text_area.event_generate("<<Paste>>")

def select_all(text_area):
    """Выделить весь текст."""
    if text_area:
        text_area.tag_add("sel", "1.0", tk.END)

def exit_program():
    """Выход из программы."""
    root.quit()

def delete_text(text_area):
    """Удалить текст."""
    text_area.delete("1.0", tk.END)

def show_help():
    """Показать справку."""
    messagebox.showinfo("Справка", "Это руководство пользователя.")

def about():
    """Информация о программе."""
    messagebox.showinfo("О программе", "Информация о программе.")



from docx import Document

import os
from tkinter import messagebox, Toplevel, Label
from PIL import Image, ImageTk
from docx import Document

def show_in_new_window(title, content):
    window = Toplevel()
    window.title(title)
    label = Label(window, text=content, justify='left', padx=10, pady=10)
    label.pack()

def show_image_window(title, image_path):
    window = Toplevel()
    window.title(title)
    img = Image.open(image_path)
    photo = ImageTk.PhotoImage(img)
    label = Label(window, image=photo)
    label.image = photo  # важно сохранить ссылку
    label.pack()

def show_text_window_from_file(title, filepath):
    print(f"[INFO] Попытка открыть файл: {filepath}")

    if not os.path.exists(filepath):
        print("[ОШИБКА] Файл не существует.")
        messagebox.showerror("Ошибка", f"Файл не найден:\n{filepath}")
        return

    _, file_extension = os.path.splitext(filepath)

    try:
        if file_extension == '.docx':
            document = Document(filepath)
            content = "\n".join([para.text for para in document.paragraphs])
            print("[INFO] .docx файл успешно прочитан.")
            show_in_new_window(title, content)

        elif file_extension == '.txt':
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                print("[INFO] Файл успешно прочитан.")
            show_in_new_window(title, content)

        elif file_extension.lower() == '.png':
            print("[INFO] PNG-файл успешно прочитан.")
            show_image_window(title, filepath)

        else:
            print(f"[ОШИБКА] Неподдерживаемый формат файла: {file_extension}")
            messagebox.showerror("Ошибка", f"Неподдерживаемый формат файла: {file_extension}")

    except UnicodeDecodeError as ude:
        print(f"[ОШИБКА] Проблема с кодировкой: {ude}")
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл из-за проблемы с кодировкой:\n{ude}")
    except Exception as e:
        print(f"[ОШИБКА] Непредвиденная ошибка: {e}")
        messagebox.showerror("Ошибка", f"Ошибка при открытии файла:\n{e}")

 

def show_in_new_window(title, content):
    window = tk.Toplevel()
    window.title(title)
    window.geometry("600x400")

    text_widget = tk.Text(window, wrap="word", font=("Consolas", 12))
    text_widget.insert("1.0", content)
    text_widget.configure(state="disabled")  # делаем текст только для чтения
    text_widget.pack(fill="both", expand=True)

    print("[INFO] Окно с текстом успешно создано.") 

import os

txt_path = os.path.join(os.path.dirname(__file__), "txt")

def show_task_description():
    show_text_window_from_file("Постановка задачи", os.path.join(txt_path, "task.txt"))

def show_grammar():
    show_text_window_from_file("Грамматика", os.path.join(txt_path, "grammar.txt"))

def show_grammar_classification():
    show_text_window_from_file("Классификация грамматики", os.path.join(txt_path, "classification.txt"))

def show_analysis_method():
    show_text_window_from_file("Метод анализа", os.path.join(txt_path, "analysis.png"))

def show_error_handling():
    show_text_window_from_file("Диагностика и нейтрализация ошибок", os.path.join(txt_path, "diagnostics.txt"))

def show_test_example():
    show_text_window_from_file("Тестовый пример", os.path.join(txt_path, "test.png"))

def show_references():
    show_text_window_from_file("Список литературы", os.path.join(txt_path, "literature.txt"))

def show_source_code():
    show_text_window_from_file("Исходный код программы", os.path.join(txt_path, "cod.txt"))


# Создание окна
root = tk.Tk()
root.title("Редактор")

# Устанавливаем начальные размеры окна
root.geometry("800x600")

# Главное меню
menu_bar = tk.Menu(root)

# Файл
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Создать", command=create_document)
file_menu.add_command(label="Открыть", command=open_document)
file_menu.add_command(label="Сохранить как", command=save_document_as)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=exit_program)
menu_bar.add_cascade(label="Файл", menu=file_menu)

# Правка
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Отменить", command=lambda: undo(get_active_text_area()))
edit_menu.add_command(label="Повторить", command=lambda: redo(get_active_text_area()))
edit_menu.add_separator()
edit_menu.add_command(label="Вырезать", command=lambda: cut_text(get_active_text_area()))
edit_menu.add_command(label="Копировать", command=lambda: copy_text(get_active_text_area()))
edit_menu.add_command(label="Вставить", command=lambda: paste_text(get_active_text_area()))
edit_menu.add_separator()
edit_menu.add_command(label="Удалить", command=lambda: delete_text(get_active_text_area()))
edit_menu.add_command(label="Выделить все", command=lambda: select_all(get_active_text_area()))
menu_bar.add_cascade(label="Правка", menu=edit_menu)

# Пуск
run_menu = tk.Menu(menu_bar, tearoff=0)
run_menu.add_command(label="Синтаксический анализ", command=syntax_analysis)
menu_bar.add_cascade(label="Пуск", menu=run_menu)

# Справка
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Вызов справки", command=show_help)
help_menu.add_separator()
help_menu.add_command(label="О программе", command=about)
menu_bar.add_cascade(label="Справка", menu=help_menu)

# Текст
text_menu = tk.Menu(menu_bar, tearoff=0)
text_menu.add_command(label="Постановка задачи", command=show_task_description)
text_menu.add_command(label="Грамматика", command=show_grammar)
text_menu.add_command(label="Классификация грамматики", command=show_grammar_classification)
text_menu.add_command(label="Метод анализа", command=show_analysis_method)
text_menu.add_command(label="Диагностика и нейтрализация ошибок", command=show_error_handling)
text_menu.add_command(label="Тестовый пример", command=show_test_example)
text_menu.add_command(label="Список литературы", command=show_references)
text_menu.add_command(label="Исходный код программы", command=show_source_code)
menu_bar.add_cascade(label="Текст", menu=text_menu)


root.config(menu=menu_bar)

# Панель инструментов
toolbar = tk.Frame(root)

import os
from tkinter import PhotoImage

base_path = os.path.join(os.path.dirname(__file__), "icons1")

icons = {
    "Создать": PhotoImage(file=os.path.join(base_path, "new.png")).subsample(20, 20),
    "Открыть": PhotoImage(file=os.path.join(base_path, "open.png")).subsample(2, 2),
    "Сохранить": PhotoImage(file=os.path.join(base_path, "save.png")).subsample(20, 20),
    "Сохранить как": PhotoImage(file=os.path.join(base_path, "save.png")).subsample(20, 20),
    "Отменить": PhotoImage(file=os.path.join(base_path, "undo.png")).subsample(20, 20),
    "Повторить": PhotoImage(file=os.path.join(base_path, "redo.png")).subsample(20, 20),
    "Копировать": PhotoImage(file=os.path.join(base_path, "copy.png")).subsample(20, 20),
    "Вырезать": PhotoImage(file=os.path.join(base_path, "cut.png")).subsample(20, 20),
    "Вставить": PhotoImage(file=os.path.join(base_path, "paste.png")).subsample(20, 20),
    "пуск": PhotoImage(file=os.path.join(base_path, "syntax.png")).subsample(20, 20),
}



buttons = [
    ("Создать", create_document),
    ("Открыть", open_document),
    ("Сохранить как", save_document),
    ("Отменить", lambda: undo(get_active_text_area())),
    ("Повторить", lambda: redo(get_active_text_area())),
    ("Копировать", lambda: copy_text(get_active_text_area())),
    ("Вырезать", lambda: cut_text(get_active_text_area())),
    ("Вставить", lambda: paste_text(get_active_text_area())),
    ("пуск", syntax_analysis),
]

for text, command in buttons:
    btn = tk.Button(toolbar, image=icons.get(text), command=command)
    btn.image = icons.get(text)
    btn.pack(side=tk.LEFT, padx=2, pady=2)

toolbar.pack(fill=tk.X)

# Размер шрифта
font_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36]
selected_size = tk.IntVar(value=12)
font_size_menu = tk.OptionMenu(toolbar, selected_size, *font_sizes, command=update_font_size)
font_size_menu.pack(side=tk.LEFT, padx=5, pady=2)

# Словарь языков
LANGUAGES = {
    "Русский": {
        "file": "Файл",
        "edit": "Правка",
        "run": "Пуск",
        "help": "Справка",
        "create": "Создать",
        "open": "Открыть",
        "save_as": "Сохранить как",
        "exit": "Выход",
        "undo": "Отменить",
        "redo": "Повторить",
        "cut": "Вырезать",
        "copy": "Копировать",
        "paste": "Вставить",
        "delete": "Удалить",
        "select_all": "Выделить все",
        "syntax_analysis": "Синтаксический анализ",
        "about": "О программе",
        "help_call": "Вызов справки",
    },
    "English": {
        "file": "File",
        "edit": "Edit",
        "run": "Run",
        "help": "Help",
        "create": "New",
        "open": "Open",
        "save_as": "Save As",
        "exit": "Exit",
        "undo": "Undo",
        "redo": "Redo",
        "cut": "Cut",
        "copy": "Copy",
        "paste": "Paste",
        "delete": "Delete",
        "select_all": "Select All",
        "syntax_analysis": "Syntax Analysis",
        "about": "About",
        "help_call": "Help",
    },
}

# Переменная для хранения текущего языка
selected_language = tk.StringVar(value="Русский")

def change_language(event=None):
    """Изменяет язык интерфейса"""
    lang = selected_language.get()
    translation = LANGUAGES[lang]

    # Обновление текста меню
    menu_bar.entryconfig(1, label=translation["file"])
    menu_bar.entryconfig(2, label=translation["edit"])
    menu_bar.entryconfig(3, label=translation["run"])
    menu_bar.entryconfig(4, label=translation["help"])

    file_menu.entryconfig(0, label=translation["create"])
    file_menu.entryconfig(1, label=translation["open"])
    file_menu.entryconfig(2, label=translation["save_as"])
    file_menu.entryconfig(4, label=translation["exit"])

    edit_menu.entryconfig(0, label=translation["undo"])
    edit_menu.entryconfig(1, label=translation["redo"])
    edit_menu.entryconfig(3, label=translation["cut"])
    edit_menu.entryconfig(4, label=translation["copy"])
    edit_menu.entryconfig(5, label=translation["paste"])
    edit_menu.entryconfig(7, label=translation["delete"])
    edit_menu.entryconfig(8, label=translation["select_all"])

    run_menu.entryconfig(0, label=translation["syntax_analysis"])

    help_menu.entryconfig(0, label=translation["help_call"])
    help_menu.entryconfig(2, label=translation["about"])

# Добавляем выпадающий список выбора языка
language_menu = ttk.Combobox(toolbar, textvariable=selected_language, values=list(LANGUAGES.keys()), state="readonly")
language_menu.pack(side=tk.RIGHT, padx=10)
language_menu.bind("<<ComboboxSelected>>", change_language)

# Строка состояния
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor="w")
status_label.pack(side=tk.BOTTOM, fill=tk.X) 

# Создание вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Окно для вывода результатов
output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, expand=False)

# Инициализация переменной для отображения статуса
status_label_var = tk.StringVar()

# Инициализация Label для отображения статуса
status_label = tk.Label(root, textvariable=status_label_var)
status_label.pack()

# Создание таблицы
columns = ("code", "type", "lexeme", "position", "file_path", "line")
output_table = ttk.Treeview(output_frame, columns=columns, show="headings")
# Определяем заголовки столбцов
output_table.heading("code", text="Код")
output_table.heading("type", text="Тип лексемы")
output_table.heading("lexeme", text="Лексема")
output_table.heading("position", text="Позиция")
output_table.heading("file_path", text="Файл")
output_table.heading("line", text="Строка")

# Определяем ширину колонок
output_table.column("code", width=50, anchor="center")
output_table.column("type", width=200)
output_table.column("lexeme", width=150)
output_table.column("position", width=100)
output_table.column("file_path", width=200)
output_table.column("line", width=50)

# Добавляем скроллбар
scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=output_table.yview)
output_table.configure(yscroll=scrollbar.set)

# Располагаем элементы
output_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def check_unsaved_changes():
    """Проверяет наличие несохраненных изменений перед выходом или выполнением других операций."""
    current_tab = notebook.nametowidget(notebook.select())
    if current_tab and hasattr(current_tab, "text_area"):
        text_area = current_tab.text_area
        file_path = current_tab.file_path

        current_text = text_area.get("1.0", tk.END).strip()
        original_text = ""

        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                original_text = file.read().strip()

        if current_text != original_text:  # Если текст изменился
            response = messagebox.askyesnocancel("Несохраненные изменения", "Файл был изменен. Сохранить перед закрытием?")
            if response:  # Если нажата кнопка "Да"
                save_document()
            return response  # True - продолжить, None - отмена действия

    return True  # Если изменений нет

def confirm_exit():
    """Подтверждение выхода из программы."""
    if check_unsaved_changes() is not None:
        root.quit()

def confirm_open_document():
    """Подтверждение открытия нового документа."""
    if check_unsaved_changes() is not None:
        open_document()

def confirm_create_document():
    """Подтверждение создания нового документа."""
    if check_unsaved_changes() is not None:
        create_document()

# Переназначение команд меню для проверки изменений
root.protocol("WM_DELETE_WINDOW", confirm_exit)  # Обработка закрытия окна
file_menu.entryconfig("Открыть", command=confirm_open_document)
file_menu.entryconfig("Создать", command=confirm_create_document)

6
# Запуск основного цикла приложения
root.mainloop()

 


