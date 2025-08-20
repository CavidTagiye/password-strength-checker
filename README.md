# 🔐 Password Strength Checker (Tkinter)

This project is a **desktop application** built with **Python (Tkinter)** that helps users evaluate the strength of their passwords and estimate the time it would take for a brute-force attack to crack them.

---

## ✨ Features

- 📝 **Real-time password evaluation**
  - Checks **length**
  - Checks **character variety** (uppercase, lowercase, digits, symbols)
  - Detects **patterns** (repeated characters, sequences, common words)
  - Calculates **entropy**  

- 📊 **Visual interface**
  - Color-coded progress bars for each category
  - Overall strength score (0–100)
  - Strength labels (Very Weak → Very Strong)

- ⏱ **Crack time estimation**
  - Estimates how long it would take to brute-force the password on:
    - Typical PC (~10^6 guesses/s)
    - High-end GPU (~10^9 guesses/s)
    - Small cluster (~10^12 guesses/s)
    - Large cluster (~10^15 guesses/s)

---

## 🖥 Screenshots
*(Add screenshots of the app UI here if you want)*

---

## 🚀 Installation & Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/CavidTagiye/password-strength-checker.git
   cd password-strength-checker
