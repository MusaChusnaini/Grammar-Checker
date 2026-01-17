import json
import os

class JavaneseGrammarChecker:
    def __init__(self, db_file):
        self.tokens = {}
        self.phrases = {} 
        
        self.valid_rules = (
            ('S', 'P'),             
            ('S', 'P', 'O'),        
            ('S', 'P', 'K'),        
            ('S', 'P', 'O', 'K'),
            ('S', 'P', 'K', 'O'), 
            ('O', 'P', 'S')       
        )
        
        self.load_database(db_file)

    def load_database(self, filename):
        if not os.path.exists(filename):
            print(f"Error: File database '{filename}' tidak ditemukan!")
            return

        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            
            # Load Subjek
            for word, phrase in data.get("subjek", {}).items():
                self.tokens[word.lower()] = "S"
                self.phrases[word.lower()] = phrase
            
            # Load Predikat
            for word, phrase in data.get("predikat", {}).items():
                self.tokens[word.lower()] = "P"
                self.phrases[word.lower()] = phrase
                
            # Load Objek
            for word, phrase in data.get("objek", {}).items():
                self.tokens[word.lower()] = "O"
                self.phrases[word.lower()] = phrase
            
            # Load Keterangan
            for word, phrase in data.get("keterangan", {}).items():
                self.tokens[word.lower()] = "K"
                self.phrases[word.lower()] = phrase
                
            print(f"Database dimuat! Total kata: {len(self.tokens)}")
            
        except json.JSONDecodeError:
            print("Error: Format JSON salah/rusak. Pastikan formatnya benar.")

    def get_token_info(self, word):
        """Mengembalikan Tipe Token dan Contoh Frasa"""
        w = word.lower()
        return self.tokens.get(w, "UNKNOWN"), self.phrases.get(w, "-")

    def parse(self, sentence):
        words = sentence.split()
        detected_pattern = []
        token_details = []

        print(f"\nMemproses kalimat: '{sentence}'")
        print("-" * 60) # Garis diperpanjang

        # 1. Tokenizing
        for word in words:
            token_type, phrase_example = self.get_token_info(word)
            
            if token_type == "UNKNOWN":
                print(f"[ERROR] Kata '{word}' tidak dikenali dalam kamus.")
                return False
            
            detected_pattern.append(token_type)
            
            # Output lebih informatif dengan Frasa
            print(f"> Ditemukan: {word.ljust(15)} | Tipe: {token_type} | Frasa: {phrase_example}")
            token_details.append(f"{word}({token_type})")

        detected_pattern_tuple = tuple(detected_pattern)
        print("-" * 60)
        print(f"Pola terdeteksi: {detected_pattern_tuple}")

        # 2. Syntax Matching
        if detected_pattern_tuple in self.valid_rules:
            print(f"[VALID] Kalimat Sesuai Aturan Grammar!")
            return True
        else:
            print(f"[INVALID] Pola {detected_pattern_tuple} tidak valid.")
            return False

# --- MAIN ---
if __name__ == "__main__":
    app = JavaneseGrammarChecker("kamus.json")

    while True:
        print("\n--- Checker Bahasa Jawa (Ketik 'exit' untuk keluar) ---")
        user_input = input("Masukkan kalimat: ")
        
        if user_input.lower() == 'exit':
            break
        
        if user_input.strip():
            app.parse(user_input)