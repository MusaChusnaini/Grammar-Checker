import json
import os
from graphviz import Digraph

class JavaneseGrammarChecker:
    def __init__(self, db_file):
        self.tokens = {}
        self.phrases = {} 
        
        # Aturan Pola Kalimat Baku (Jejer-Wasesa-Lesan-Katrangan)
        self.valid_rules = (
            ('S', 'P'),             # J-W
            ('S', 'P', 'O'),        # J-W-L
            ('S', 'P', 'Pel'),      # J-W-G
            ('S', 'P', 'K'),        # J-W-K
            ('S', 'P', 'O', 'K'),   # J-W-L-K
            ('S', 'P', 'K', 'O'),   # Variasi
            ('S', 'P', 'K', 'S'),   # Variasi
        )
        
        self.load_database(db_file)

    def load_database(self, filename):
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' tidak ditemukan!")
            return

        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            
            # Load data dengan mapping ke S/P/O/K/Pel
            # S = Jejer, P = Wasesa, O = Lesan, Pel = Geganep, K = Katrangan
            categories = {
                "subjek": "S", "predikat": "P", "objek": "O", 
                "pelengkap": "Pel", "keterangan": "K"
            }

            for key, role_code in categories.items():
                for word, phrase_type in data.get(key, {}).items():
                    self.tokens[word.lower()] = role_code
                    self.phrases[word.lower()] = phrase_type
                
            print(f"Kamus Ngoko dimuat! Total kata: {len(self.tokens)}")
            
        except json.JSONDecodeError:
            print("Error: Format JSON rusak.")

    def get_token_info(self, word):
        w = word.lower()
        return self.tokens.get(w, "UNKNOWN"), self.phrases.get(w, "Tembung ?")

    def render_tree(self, parsed_data, filename="output_parse_tree"):
        output_folder = "output-diagram"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"[INFO] Folder '{output_folder}' berhasil dibuat.")
        full_path = os.path.join(output_folder, filename)

        dot = Digraph(comment='Javanese Parse Tree')
        dot.attr('node', shape='box', style='rounded', fontname='Arial', height='0.5')
        dot.node('root', 'Ukara (Kalimat)')

        role_labels = {
            'S': 'Jejer\n(Subject)',
            'P': 'Wasesa\n(Predikat)',
            'O': 'Lesan\n(Objek)',
            'Pel': 'Geganep\n(Pelengkap)',
            'K': 'Katrangan\n(Keterangan)'
        }

        last_k_node_id = None 

        for i, (word, role, category) in enumerate(parsed_data):
            role_label = role_labels.get(role, role)
            role_id = f"role_{i}"
            cat_id = f"cat_{i}"
            word_id = f"word_{i}"

            if role == 'K' and last_k_node_id is not None:
                dot.node(cat_id, category)
                dot.node(word_id, f'"{word}"')
                dot.edge(last_k_node_id, cat_id)
                dot.edge(cat_id, word_id)
            else:
                dot.node(role_id, role_label)
                dot.node(cat_id, category)
                dot.node(word_id, f'"{word}"')

                dot.edge('root', role_id)
                dot.edge(role_id, cat_id)
                dot.edge(cat_id, word_id)

                if role == 'K':
                    last_k_node_id = role_id
                else:
                    last_k_node_id = None

        try:
            output_path = dot.render(full_path, format='png', view=True)
            print(f"[INFO] Diagram tersimpan di: {output_path}")
        except Exception as e:
            print(f"[WARNING] Gagal render graphviz: {e}")

    def parse(self, sentence):
        words = sentence.split()
        detected_pattern = []
        parsed_tokens = []

        print(f"\nAnalisis Ukara: '{sentence}'")
        print("-" * 60)

        for word in words:
            token_type, phrase_category = self.get_token_info(word)
            
            if token_type == "UNKNOWN":
                print(f"[ERROR] Kalimat '{word}' tidak dikenal di kamus NGOKO.")
                return False
            
            detected_pattern.append(token_type)
            parsed_tokens.append((word, token_type, phrase_category))
            print(f"> {word.ljust(15)} | {token_type} | {phrase_category}")

        simplified_pattern = []
        last_token = None
        for token in detected_pattern:
            if token == 'K' and last_token == 'K':
                continue
            simplified_pattern.append(token)
            last_token = token
            
        pattern_tuple = tuple(simplified_pattern)
        
        print("-" * 60)
        if pattern_tuple in self.valid_rules:
            print(f"[VALID] Struktur Ukara Benar!")
            self.render_tree(parsed_tokens, filename=f"tree_{sentence.replace(' ', '_')}")
            return True
        else:
            print(f"[INVALID] Struktur {pattern_tuple} salah.")
            return False

if __name__ == "__main__":
    app = JavaneseGrammarChecker("kamus.json")
    while True:
        user_input = input("\nMasukkan Kalimat (ketik 'exit' untuk keluar): ")
        if user_input.lower() == 'exit': break
        if user_input.strip(): app.parse(user_input)