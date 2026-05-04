import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        self.books = []          # список словарей с книгами
        self.filtered_books = [] # отфильтрованный список

        # Создание виджетов
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()

        # Загрузка данных при старте
        self.load_data()

        # Обновление таблицы
        self.update_list()

    def create_input_frame(self):
        """Фрейм для ввода данных книги"""
        input_frame = ttk.LabelFrame(self.root, text="Добавить книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        # Автор
        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.author_entry = ttk.Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=2)

        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=2)

        # Количество страниц
        ttk.Label(input_frame, text="Страниц:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.pages_entry = ttk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=2, sticky="w")

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_genre_var = tk.StringVar()
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, width=20, state="readonly")
        self.filter_genre_combo['values'] = ["Все"]  # будет обновлено при загрузке
        self.filter_genre_combo.current(0)
        self.filter_genre_combo.grid(row=0, column=1, padx=5)

        # Фильтр по страницам > 200
        self.filter_pages_var = tk.BooleanVar()
        pages_check = ttk.Checkbutton(filter_frame, text="Страниц > 200", variable=self.filter_pages_var, command=self.apply_filters)
        pages_check.grid(row=0, column=2, padx=20)

        # Кнопка применить фильтры
        apply_btn = ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters)
        apply_btn.grid(row=0, column=3, padx=10)

        # Кнопка сброса фильтров
        reset_btn = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters)
        reset_btn.grid(row=0, column=4, padx=10)

    def create_tree_view(self):
        """Таблица для отображения книг"""
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=("title", "author", "genre", "pages"), show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80)
        self.tree.pack(fill="both", expand=True)

        scrollbar.config(command=self.tree.yview)

    def create_button_frame(self):
        """Кнопки сохранения и загрузки"""
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        save_btn = ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_data)
        save_btn.pack(side="left", padx=5)

        load_btn = ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_data)
        load_btn.pack(side="left", padx=5)

        # Дополнительно: кнопка удаления выбранной книги (для удобства)
        del_btn = ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_selected)
        del_btn.pack(side="right", padx=5)

    def add_book(self):
        """Добавление новой книги после валидации"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Проверки
        if not title:
            messagebox.showerror("Ошибка", "Название книги не может быть пустым")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым")
            return
        if not genre:
            messagebox.showerror("Ошибка", "Жанр не может быть пустым")
            return
        if not pages_str:
            messagebox.showerror("Ошибка", "Укажите количество страниц")
            return
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым положительным числом")
            return

        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(new_book)
        self.update_genre_combobox()   # обновить список жанров для фильтра
        self.update_list()             # перерисовать таблицу
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def update_genre_combobox(self):
        """Обновить выпадающий список жанров для фильтра"""
        genres = set(book["genre"] for book in self.books)
        genre_list = sorted(["Все"] + list(genres))
        self.filter_genre_combo['values'] = genre_list
        if self.filter_genre_var.get() not in genre_list:
            self.filter_genre_var.set("Все")

    def apply_filters(self):
        """Применить текущие фильтры к списку книг"""
        selected_genre = self.filter_genre_var.get()
        filter_pages = self.filter_pages_var.get()

        self.filtered_books = []
        for book in self.books:
            # Фильтр по жанру
            if selected_genre != "Все" and book["genre"] != selected_genre:
                continue
            # Фильтр по страницам
            if filter_pages and not (book["pages"] > 200):
                continue
            self.filtered_books.append(book)

        self.update_list(use_filtered=True)

    def reset_filters(self):
        """Сбросить все фильтры"""
        self.filter_genre_var.set("Все")
        self.filter_pages_var.set(False)
        self.filtered_books = self.books.copy()
        self.update_list(use_filtered=True)

    def update_list(self, use_filtered=False):
        """Обновить содержимое таблицы"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Определяем, какой список отображать
        display_list = self.filtered_books if use_filtered and self.filtered_books else self.books
        if not use_filtered:
            # Обычное отображение всех книг
            display_list = self.books

        for book in display_list:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def save_data(self):
        """Сохранить текущий список книг в JSON файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузить данные из JSON файла"""
        if not os.path.exists(DATA_FILE):
            # Если файла нет – создаём пустой список
            self.books = []
        else:
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Базовая валидация загруженных данных
                    if isinstance(loaded, list):
                        self.books = loaded
                    else:
                        self.books = []
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                self.books = []
        self.update_genre_combobox()
        self.reset_filters()   # сбросить фильтры и показать все книги

    def delete_selected(self):
        """Удалить выделенную книгу из списка"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите книгу для удаления")
            return

        # Получаем название книги из выбранной строки
        item = selected[0]
        values = self.tree.item(item, "values")
        title_to_del = values[0]
        author_to_del = values[1]

        # Ищем и удаляем из self.books
        for i, book in enumerate(self.books):
            if book["title"] == title_to_del and book["author"] == author_to_del:
                del self.books[i]
                break
        self.update_genre_combobox()
        self.reset_filters()   # обновить отображение
        messagebox.showinfo("Удаление", f"Книга '{title_to_del}' удалена")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()