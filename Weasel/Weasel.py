
import random
import string
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Save files in the same directory as this Python script
WEASEL_DIR = Path(__file__).resolve().parent
PLOT_FILE = WEASEL_DIR / "weasel_fitness.png"
LOG_FILE = WEASEL_DIR / "weasel_generations.txt"

# Evolution settings
OFFSPRING_COUNT = 100
MUTATION_RATE = 0.05

generation = 0
best_parent = ""
best_score = 0
target = ""
fitness_history = []
generation_history = []
log_handle = None
running = False


# Calculate fitness: one point for each matching character
def compare_strings(candidate, target):
    score = 0

    for i in range(len(target)):
        if i < len(candidate) and candidate[i] == target[i]:
            score += 1

    return score


# Create a random string of the required length
def random_string(length, allowed_characters):
    return "".join(
        random.choice(allowed_characters)
        for _ in range(length)
    )


# Mutate each character with a 5% chance
def mutate_string(text, allowed_characters):
    new_text = ""

    for char in text:
        if random.random() < MUTATION_RATE:
            new_text += random.choice(allowed_characters)
        else:
            new_text += char

    return new_text


# Save the fitness graph
def save_plot():
    if not fitness_history:
        return

    ax.clear()
    ax.plot(
        generation_history,
        fitness_history,
        marker=".",
        markersize=3
    )

    ax.set_title("Weasel Program: Fitness Over Time")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness Score")
    ax.set_ylim(0, len(target) + 1)
    ax.grid(True)

    figure.tight_layout()
    figure.savefig(PLOT_FILE, dpi=200)

    canvas.draw()


# Start the evolutionary process
def start_evolution():
    global generation, best_parent, best_score
    global target, fitness_history, generation_history
    global log_handle, running

    if running:
        return

    target = target_entry.get()

    if not target:
        messagebox.showwarning(
            "Missing phrase",
            "Please enter a target phrase."
        )
        return

    # Allow A-Z, spaces, and any characters used in the target.
    # This ensures that the entered target can be reached.
    allowed_characters = string.ascii_uppercase + " "
    allowed_characters += "".join(
        char for char in target
        if char not in allowed_characters
    )

    generation = 0
    best_parent = random_string(len(target), allowed_characters)
    best_score = compare_strings(best_parent, target)

    fitness_history = [best_score]
    generation_history = [0]

    # Close an earlier log file, if necessary
    if log_handle is not None:
        log_handle.close()

    log_handle = open(LOG_FILE, "w", encoding="utf-8")

    log_handle.write(f"Target phrase: {target}\n")
    log_handle.write(f"Target length: {len(target)}\n\n")
    log_handle.write(
        f"Generation 0 | Score: {best_score}/{len(target)}"
        f" | Best string: {best_parent}\n"
    )
    log_handle.flush()

    results_box.delete("1.0", tk.END)
    results_box.insert(
        tk.END,
        f"Generation 0\n"
        f"Score: {best_score}/{len(target)}\n"
        f"Best string: {best_parent}\n\n"
    )

    start_button.config(state=tk.DISABLED)
    running = True

    save_plot()
    update_generation(allowed_characters)


# Run one generation at a time so the GUI stays responsive
def update_generation(allowed_characters):
    global generation, best_parent, best_score, running

    if best_score == len(target):
        finish_evolution()
        return

    generation += 1

    # Create 100 offspring from the current best parent
    offspring = [
        mutate_string(best_parent, allowed_characters)
        for _ in range(OFFSPRING_COUNT)
    ]

    # Find the highest-scoring offspring
    best_offspring = max(
        offspring,
        key=lambda child: compare_strings(child, target)
    )

    offspring_score = compare_strings(best_offspring, target)

    # Keep the offspring only if it improves the score
    if offspring_score > best_score:
        best_parent = best_offspring
        best_score = offspring_score

    # Record the best fitness for this generation
    generation_history.append(generation)
    fitness_history.append(best_score)

    generation_text = (
        f"Generation {generation} | "
        f"Score: {best_score}/{len(target)} | "
        f"Best string: {best_parent}"
    )

    results_box.insert(tk.END, generation_text + "\n")
    results_box.see(tk.END)

    log_handle.write(generation_text + "\n")
    log_handle.flush()

    # Refresh and automatically save the graph
    save_plot()

    # Schedule the next generation
    if best_score == len(target):
        finish_evolution()
    else:
        root.after(
            1,
            lambda: update_generation(allowed_characters)
        )


# Finish and save the final results
def finish_evolution():
    global running, log_handle

    running = False

    final_message = (
        f"\nTarget reached!\n"
        f"Target: {target}\n"
        f"Best string: {best_parent}\n"
        f"Final score: {best_score}/{len(target)}\n"
        f"Generations: {generation}\n"
    )

    results_box.insert(tk.END, final_message)
    results_box.see(tk.END)

    if log_handle is not None:
        log_handle.write(final_message)
        log_handle.close()
        log_handle = None

    save_plot()

    start_button.config(state=tk.NORMAL)

    messagebox.showinfo(
        "Evolution complete",
        f"Target phrase reached in {generation} generations.\n\n"
        f"Fitness graph:\n{PLOT_FILE}\n\n"
        f"Generation log:\n{LOG_FILE}"
    )


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Weasel Program")
root.geometry("900x750")

title_label = tk.Label(
    root,
    text="Weasel Program: Evolutionary String Search",
    font=("Arial", 16, "bold")
)
title_label.pack(pady=10)

instruction_label = tk.Label(
    root,
    text="Enter a target phrase:"
)
instruction_label.pack()

target_entry = tk.Entry(root, width=50, font=("Arial", 12))
target_entry.pack(pady=5)

target_entry.insert(0, "METHINKS IT IS LIKE A WEASEL")

start_button = tk.Button(
    root,
    text="Start Evolution",
    command=start_evolution
)
start_button.pack(pady=8)

# Text area to display generation results
results_box = tk.Text(root, height=10, width=100)
results_box.pack(padx=10, pady=10)

# Create the fitness graph
figure, ax = plt.subplots(figsize=(7, 4))

canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

root.mainloop()
