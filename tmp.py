with open("Zeszyt1.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

with open("Zeszyt_modified.txt", "w", encoding="utf-8") as modified_file:
    for line in lines:
        line = line.rstrip("\n")  # Usuwamy znak końca linii
        line = line.replace("'", "\\'")  # Dodajemy znak ucieczki przed każdym apostrofem
        modified_line = line.replace("\t", ":'") + "',\n"  # Dokonujemy zamiany i dodajemy przecinek przed końcem linii
        modified_file.write(modified_line)