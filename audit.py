import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

class App:
    def __init__(self, root):
        self.root = root
        root.title("Монитор Событий")

        # Цвета
        background_color = "#D0E8F5"  # бледно-голубой

        # Визуальные компоненты
        main_frame = tk.Frame(root, bg=background_color)
        main_frame.pack(expand=True, fill="both")

        self.label = ttk.Label(main_frame, text="Монитор событий", font=("Arial", 16, "bold"))
        self.label.grid(row=0, column=0, columnspan=3, pady=10)

        self.process_button = ttk.Button(main_frame, text="Мониторить процессы", command=self.monitor_processes, style="White.TButton")
        self.process_button.grid(row=1, column=0, pady=5)

        self.file_button = ttk.Button(main_frame, text="Мониторить изменения файлов", command=self.select_file, style="White.TButton")
        self.file_button.grid(row=2, column=0, pady=5)

        self.result_label = ttk.Label(main_frame, text="Результаты:", font=("Arial", 12), background=background_color)
        self.result_label.grid(row=4, column=0, pady=5)

        self.result_frame = tk.Frame(main_frame, height=100, width=400, bg=background_color)
        self.result_frame.grid(row=5, column=0, pady=5)
        self.result_frame.grid_propagate(False)

        self.result_list = tk.Listbox(self.result_frame, height=10, width=60, bg="white")
        self.result_list.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_list.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.result_list.config(yscrollcommand=self.scrollbar.set)

        control_frame = tk.Frame(main_frame, bg=background_color)
        control_frame.grid(row=6, column=0, pady=10)

        self.clear_button = ttk.Button(control_frame, text="Очистить", command=self.clear_results, style="White.TButton")
        self.clear_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(control_frame, text="Сохранить", command=self.save_results, style="White.TButton")
        self.save_button.grid(row=0, column=1, padx=5)

        self.print_button = ttk.Button(control_frame, text="Распечатать", command=self.print_results, style="White.TButton")
        self.print_button.grid(row=0, column=2, padx=5)

        self.selected_file = ""
        self.observer = None
        self.after_id = None

        # Размещаем окно по центру экрана
        self.center_window()

    def center_window(self):
        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Получаем размеры окна
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        # Вычисляем координаты для размещения окна по центру экрана
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Устанавливаем новые координаты окна
        self.root.geometry("+{}+{}".format(x, y))
        self.root.update_idletasks()  # Обновляем окно

    def monitor_processes(self):
        messagebox.showinfo("Мониторинг процессов", "Мониторинг процессов...")
        self.result_list.delete(0, tk.END)
        self.processes = [proc for proc in psutil.process_iter()]
        self.process_index = 0
        self.start_monitoring_process()

    def start_monitoring_process(self):
        if self.process_index < len(self.processes):
            proc = self.processes[self.process_index]
            try:
                proc_name = 'Процесс {} запущен'.format(proc.name())
                print(proc_name)
                self.result_list.insert(tk.END, proc_name)
                self.process_index += 1
                self.after_id = self.root.after(50, self.start_monitoring_process)  # Запланировать следующее выполнение через 50 мс
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                self.process_index += 1
                self.start_monitoring_process()

    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            self.monitor_files()

    def monitor_files(self):
        messagebox.showinfo("Мониторинг изменений файлов", "Мониторинг изменений файла {}...".format(self.selected_file))
        self.result_list.delete(0, tk.END)

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, result_list):
                super().__init__()
                self.result_list = result_list

            def on_any_event(self, event):
                if not event.is_directory and event.src_path == self.selected_file:
                    if event.event_type == 'modified' or event.event_type == 'created':
                        file_event = 'Файл {} {}'.format(event.src_path, event.event_type)
                        print(file_event)
                        self.result_list.insert(tk.END, file_event)

        self.observer = Observer()
        self.observer.schedule(FileChangeHandler(self.result_list), os.path.dirname(self.selected_file), recursive=True)
        self.observer.start()

        # Ложное событие мониторинга файла
        self.create_fake_file_event()

    def create_fake_file_event(self):
        # Создаем временный файл
        temp_file = "temp_file.txt"
        with open(temp_file, "w") as file:
            file.write("Initial content")

        # Ждем некоторое время
        time.sleep(2)

        # Меняем содержимое файла
        with open(temp_file, "w") as file:
            file.write("Modified content")

        # После того, как ваше приложение обнаружит изменение файла и отреагирует на него,
        # можно удалить временный файл
        os.remove(temp_file)

    def clear_results(self):
        self.result_list.delete(0, tk.END)

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                for i in range(self.result_list.size()):
                    file.write(self.result_list.get(i) + "\n")

    def print_results(self):
        # Здесь вы можете добавить код для печати результатов
        messagebox.showinfo("Печать", "Печать результатов...")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


