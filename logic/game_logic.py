import random


class MastermindLogic:
    
    def __init__(self):
        # Definiujemy 6 dostępnych kolorów w grze
        self.available_colors = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
        self.code_length = 4
        self.secret_code = []

    
    def generate_secret_code(self) -> list[str]:
        
        """Losuje tajną kombinację 4 kolorów z 6 dostępnych (zezwala na powtórzenia)"""
        
        self.secret_code = random.choices(self.available_colors, k=self.code_length)
        return self.secret_code


    def set_secret_code(self, custom_code: list[str]) -> None: 
        
        """
        Ustawia sekretny kod podany ręcznie przez użytkownika.
        Niezbędne dla trybów: Człowiek vs Człowiek oraz Komputer vs Człowiek.
        """
       
        self.secret_code = custom_code
    
    
    def check_guess(self, guess: list[str]) -> tuple[int, int]:
    
        """
        Porównuje ruch gracza (guess) z tajnym kodem (self.secret_code).
        Zwraca: (czarne_pionki, białe_pionki)
        czarne (correct_place) - właściwy kolor na właściwym miejscu
        białe (wrong_place)    - właściwy kolor, ale na złym miejscu
        """
    
        correct_place = 0  # czarne pionki
        secret_rest = []   # kolory z secret bez trafień pozycji 
        guess_rest = []    # kolory z guess bez trafień pozycji

        # (Czarne): Liczenie idealnych trafień (ten sam kolor i miejsce)
        for secret_color, guess_color in zip(self.secret_code, guess):
            if secret_color == guess_color:
                correct_place += 1
            else:
                secret_rest.append(secret_color)
                guess_rest.append(guess_color)

        wrong_place = 0  # białe pionki

       # (Białe): Liczenie trafień koloru na złych pozycjach
        for color in guess_rest:
            if color in secret_rest:
                wrong_place += 1
                secret_rest.remove(color)  # usunięcie, aby nie liczyć tego samego koloru drugi raz
        return correct_place, wrong_place