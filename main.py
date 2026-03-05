import random
from operator import itemgetter

class Domanda:
    domanda:str
    opzione_giusta: str
    opzioni: [str]

    def __init__(self, testo, livello, corretta, errate):
        self.testo = testo
        self.livello = int(livello)
        self.corretta = corretta
        # Creiamo una lista unica con tutte le risposte (corretta + le 3 errate)
        self.tutte_le_risposte = [corretta] + errate

    def mescola_risposte(self):
        """Restituisce le risposte in ordine casuale."""
        opzioni = list(self.tutte_le_risposte)
        random.shuffle(opzioni)
        return opzioni

# 2. CLASSE CLASSIFICA: Gestisce la lettura e scrittura del file "punti.txt"
class Classifica:
    def __init__(self, nome_file):
        self.nome_file = nome_file
        self.dati = [] # Qui caricheremo i nomi e i punti

    def carica(self):
        """Legge il file punti.txt e salva i dati in una lista di dizionari."""
        try:
            with open(self.nome_file, 'r', encoding='utf-8') as f:
                for riga in f:
                    parti = riga.strip().split()
                    if len(parti) >= 2:
                        # parti[:-1] prende tutto tranne l'ultimo (il nome)
                        # parti[-1] prende l'ultimo elemento (il punteggio)
                        nome = " ".join(parti[:-1])
                        punti = int(parti[-1])
                        self.dati.append({"Nickname": nome, "Punti": punti})
        except FileNotFoundError:
            pass # Se il file non esiste ancora, non facciamo nulla

    def aggiungi_e_salva(self, nickname, punteggio):
        """Aggiunge il nuovo punteggio, ordina e scrive tutto sul file."""
        # Aggiungiamo il giocatore attuale alla lista
        self.dati.append({"Nickname": nickname, "Punti": punteggio})

        # Ordiniamo per Punti (decrescente) e poi per Nickname (alfabetico)
        self.dati.sort(key=itemgetter("Punti", "Nickname"), reverse=True)

        # Scriviamo la lista aggiornata sul file
        with open(self.nome_file, 'w', encoding='utf-8') as f:
            for d in self.dati:
                f.write(f"{d['Nickname']} {d['Punti']}\n")

# 3. CLASSE TRIVIAGAME: Il "motore" che fa funzionare il gioco
class TriviaGame:
    def __init__(self, file_quiz, file_punti):
        self.domande = self.carica_domande(file_quiz)
        self.classifica = Classifica(file_punti)
        self.punteggio_giocatore = 0

    def carica_domande(self, nome_file):
        """Legge domande.txt e crea una lista di oggetti Domanda."""
        lista_domande = []
        try:
            with open(nome_file, 'r', encoding='utf-8') as f:
                # Leggiamo tutto e togliamo le righe vuote
                righe = [linea.strip() for linea in f if linea.strip()]
                # Ogni domanda occupa 6 righe (testo, liv, corretta, 3 errate)
                for i in range(0, len(righe), 6):
                    testo = righe[i]
                    liv = righe[i+1]
                    giusta = righe[i+2]
                    sbagliate = [righe[i+3], righe[i+4], righe[i+5]]

                    # Creiamo l'oggetto Domanda e lo aggiungiamo alla lista
                    lista_domande.append(Domanda(testo, liv, giusta, sbagliate))
        except FileNotFoundError:
            print("Errore: File domande.txt non trovato!")
        return lista_domande

    def gioca(self):
        """Gestisce i turni di gioco."""
        if not self.domande: return

        livello_attuale = 0
        # Trova il livello massimo presente tra le domande
        max_liv = max(d.livello for d in self.domande)

        while livello_attuale <= max_liv:
            # Filtra le domande: prendi solo quelle del livello corrente
            pool = [d for d in self.domande if d.livello == livello_attuale]
            domanda_scelta = random.choice(pool)

            print(f"\nLivello {livello_attuale}) {domanda_scelta.testo}")
            opzioni = domanda_scelta.mescola_risposte()

            # Mostra le opzioni numerate
            for i, testo_r in enumerate(opzioni, 1):
                print(f"  {i}. {testo_r}")

            # Chiede la risposta e controlla se è giusta
            try:
                scelta = int(input("Inserisci la risposta: "))
                risposta_utente = opzioni[scelta - 1]

                if risposta_utente == domanda_scelta.corretta:
                    print("Risposta corretta!")
                    self.punteggio_giocatore += 1
                    livello_attuale += 1 # Passa al livello successivo
                else:
                    print(f"Risposta sbagliata! Era: {domanda_scelta.corretta}")
                    break # Fine gioco se sbagli
            except (ValueError, IndexError):
                print("Scelta non valida! Fine partita.")
                break

        # Fine partita: salva i risultati
        print(f"\nHai totalizzato {self.punteggio_giocatore} punti!")
        nick = input("Inserisci il tuo nickname: ")

        self.classifica.carica() # Legge la vecchia classifica
        self.classifica.aggiungi_e_salva(nick, self.punteggio_giocatore)
        print("Punteggio salvato con successo!")

# --- AVVIO DEL PROGRAMMA ---
if __name__ == "__main__":
    gioco = TriviaGame("domande.txt", "punti.txt")
    gioco.gioca()