import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DEFAULT_FILE = "books.json"
GENRES = ["Фантастика", "Драма", "Детектив", "Научная", "Роман", "Другое"]

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("1050x700")
        self.root.minsize(950, 620)
        self.books = []
        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.genre_var = tk.StringVar(value=GENRES[0])
        self.pages_var = tk.StringVar()
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_pages_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="Готово к работе")
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        form = ttk.LabelFrame(main, text="Добавление книги", padding=10)
        form.grid(row=0, column=0, sticky="ew")
        for i in range(6):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Название книги").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.title_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Автор").grid(row=0, column=1, sticky="w")
        ttk.Entry(form, textvariable=self.author_var).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Жанр").grid(row=0, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.genre_var, values=GENRES, state="readonly").grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Количество страниц").grid(row=0, column=3, sticky="w")
        ttk.Entry(form, textvariable=self.pages_var).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Добавить книгу", command=self.add_book).grid(row=1, column=4, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Сохранить JSON", command=self.save_json).grid(row=1, column=5, sticky="ew")

        filter_frame = ttk.LabelFrame(main, text="Фильтрация", padding=10)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=12)
        for i in range(6):
            filter_frame.columnconfigure(i, weight=1)

        ttk.Label(filter_frame, text="Жанр").grid(row=0, column=0, sticky="w")
        ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, values=["Все"] + GENRES, state="readonly").grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(filter_frame, text="Страниц больше чем").grid(row=0, column=1, sticky="w")
        ttk.Entry(filter_frame, textvariable=self.filter_pages_var).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(filter_frame, text="Загрузить JSON", command=self.load_json).grid(row=1, column=4, sticky="ew")

        table_frame = ttk.LabelFrame(main, text="Прочитанные книги", padding=10)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        cols = ("id", "title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)
        headers = [("id", "ID", 60), ("title", "Название", 280), ("author", "Автор", 240), ("genre", "Жанр", 150), ("pages", "Страниц", 100)]
        for key, text, width in headers:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="center" if key in ("id", "pages") else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        bottom = ttk.Frame(main)
        bottom.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        ttk.Label(bottom, textvariable=self.status_var, relief="sunken", anchor="w", padding=6).grid(row=0, column=0, sticky="ew")
        ttk.Button(bottom, text="Удалить выбранное", command=self.delete_selected).grid(row=0, column=1, padx=(8, 0))

    def _validate_nonempty(self, value, field_name):
        value = value.strip()
        if not value:
            raise ValueError(f"Поле '{field_name}' не должно быть пустым.")
        return value

    def _validate_pages(self, value):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("Количество страниц должно быть числом.")
        pages = int(value)
        if pages <= 0:
            raise ValueError("Количество страниц должно быть положительным.")
        return pages

    def add_book(self):
        try:
            title = self._validate_nonempty(self.title_var.get(), "Название книги")
            author = self._validate_nonempty(self.author_var.get(), "Автор")
            genre = self._validate_nonempty(self.genre_var.get(), "Жанр")
            pages = self._validate_pages(self.pages_var.get())
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        item = {
            "id": len(self.books) + 1,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
        }
        self.books.append(item)
        self.refresh_table(self.books)
        self.title_var.set("")
        self.author_var.set("")
        self.pages_var.set("")
        self.status_var.set(f"Добавлена книга: {title}")

    def refresh_table(self, data=None):
        data = self.books if data is None else data
        self.tree.delete(*self.tree.get_children())
        for book in data:
            self.tree.insert("", "end", values=(book["id"], book["title"], book["author"], book["genre"], book["pages"]))

    def apply_filter(self):
        genre = self.filter_genre_var.get()
        pages_text = self.filter_pages_var.get().strip()
        try:
            pages_limit = 0
            if pages_text:
                if not pages_text.isdigit():
                    raise ValueError("Фильтр по страницам должен быть числом.")
                pages_limit = int(pages_text)
        except ValueError as e:
            messagebox.showerror("Ошибка фильтра", str(e))
            return

        filtered = []
        for book in self.books:
            if genre != "Все" and book["genre"] != genre:
                continue
            if pages_limit and book["pages"] <= pages_limit:
                continue
            filtered.append(book)
        self.refresh_table(filtered)
        self.status_var.set(f"Фильтр применён. Найдено: {len(filtered)}")

    def reset_filter(self):
        self.filter_genre_var.set("Все")
        self.filter_pages_var.set("0")
        self.refresh_table(self.books)
        self.status_var.set("Фильтр сброшен")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите книгу в таблице.")
            return
        book_id = int(self.tree.item(selected[0], "values")[0])
        self.books = [b for b in self.books if b["id"] != book_id]
        for idx, book in enumerate(self.books, start=1):
            book["id"] = idx
        self.refresh_table(self.books)
        self.status_var.set(f"Удалена книга ID {book_id}")

    def save_json(self):
        path = filedialog.asksaveasfilename(title="Сохранить JSON", defaultextension=".json", initialfile=DEFAULT_FILE, filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)
        self.status_var.set(f"Сохранено: {os.path.basename(path)}")
        messagebox.showinfo("Сохранение", "Данные успешно сохранены.")

    def load_json(self):
        path = filedialog.askopenfilename(title="Загрузить JSON", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = []
            for i, item in enumerate(data, start=1):
                title = self._validate_nonempty(str(item.get("title", "")), "Название книги")
                author = self._validate_nonempty(str(item.get("author", "")), "Автор")
                genre = str(item.get("genre", "Другое")).strip() or "Другое"
                if genre not in GENRES:
                    genre = "Другое"
                pages = self._validate_pages(str(item.get("pages", "")))
                loaded.append({"id": i, "title": title, "author": author, "genre": genre, "pages": pages})
            self.books = loaded
            self.refresh_table(self.books)
            self.status_var.set(f"Загружено книг: {len(self.books)}")
            messagebox.showinfo("Загрузка", "Данные успешно загружены.")
        except (json.JSONDecodeError, OSError, ValueError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить файл: {e}")


def main():
    root = tk.Tk()
    BookTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
