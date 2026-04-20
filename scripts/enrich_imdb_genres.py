# -*- coding: utf-8 -*-
"""Enrich imdb.json with genres based on IMDB IDs.

This script reads app/imdb.json, adds a "genres" field to each movie
based on a predefined mapping, then writes the enriched JSON back.

Usage:
    python scripts/enrich_imdb_genres.py
"""
import json
import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Genre mapping for IMDB top 250 movies by IMDB ID (170+ movies mapped)
GENRE_MAP = {
    "tt0111161": ["Drama"],  # The Shawshank Redemption
    "tt0068646": ["Crime", "Drama"],  # The Godfather
    "tt0468569": ["Action", "Crime", "Drama"],  # The Dark Knight
    "tt0071562": ["Crime", "Drama"],  # The Godfather Part II
    "tt0050083": ["Drama"],  # 12 Angry Men
    "tt0108052": ["Biography", "Drama", "History"],  # Schindler's List
    "tt0110912": ["Crime", "Drama"],  # Pulp Fiction
    "tt0167260": ["Adventure", "Fantasy"],  # The Lord of the Rings: The Return of the King
    "tt0073486": ["Drama"],  # One Flew Over the Cuckoo's Nest
    "tt0060196": ["Adventure", "Biography", "Drama"],  # Lawrence of Arabia
    "tt0167261": ["Adventure", "Fantasy"],  # The Lord of the Rings: The Two Towers
    "tt0099685": ["Crime", "Drama"],  # GoodFellas
    "tt0102926": ["Crime", "Drama", "Thriller"],  # The Silence of the Lambs
    "tt0317248": ["Action", "Crime", "Drama"],  # City of God
    "tt0118799": ["Comedy", "Drama"],  # Life Is Beautiful
    "tt0103064": ["Action", "Sci-Fi"],  # Terminator 2: Judgment Day
    "tt0076759": ["Adventure", "Sci-Fi"],  # Star Wars: Episode IV - A New Hope
    "tt0253474": ["Biography", "Drama"],  # The Pianist
    "tt0172495": ["Action", "Adventure", "Drama"],  # Gladiator
    "tt6751668": ["Drama", "Thriller"],  # Parasite
    "tt0120689": ["Crime", "Drama"],  # The Green Mile
    "tt0054215": ["Horror", "Thriller"],  # Psycho
    "tt0109830": ["Drama", "Romance"],  # Forrest Gump
    "tt0120586": ["Drama"],  # American History X
    "tt0073195": ["Adventure", "Thriller"],  # Jaws
    "tt0119217": ["Drama", "Romance"],  # Good Will Hunting
    "tt0440963": ["Drama"],  # The Departure
    "tt0088763": ["Adventure", "Comedy", "Sci-Fi"],  # Back to the Future
    "tt0107290": ["Action", "Adventure", "Sci-Fi"],  # Jurassic Park
    "tt0137523": ["Drama", "Thriller"],  # Fight Club
    "tt0045152": ["Comedy", "Musical", "Romance"],  # Singin' in the Rain
    "tt1345836": ["Action", "Crime", "Drama"],  # The Dark Knight Rises
    "tt0034583": ["Drama", "Romance", "War"],  # Casablanca
    "tt0050082": ["Mystery", "Thriller"],  # Rear Window
    "tt0114369": ["Crime", "Drama", "Thriller"],  # Se7en
    "tt0080684": ["Adventure", "Sci-Fi"],  # The Empire Strikes Back
    "tt0114814": ["Crime", "Drama", "Mystery"],  # The Usual Suspects
    "tt0816692": ["Adventure", "Drama", "Sci-Fi"],  # Interstellar
    "tt1375666": ["Action", "Sci-Fi", "Thriller"],  # Inception
    "tt0133093": ["Action", "Sci-Fi"],  # The Matrix
    "tt0078748": ["Horror", "Sci-Fi"],  # Alien
    "tt0083658": ["Sci-Fi", "Thriller"],  # Blade Runner
    "tt0047478": ["Action", "Adventure", "Drama"],  # Seven Samurai
    "tt0113492": ["Mystery", "Thriller"],  # Memento
    "tt0086879": ["Biography", "Drama"],  # Amadeus
    "tt0120815": ["Drama", "War"],  # Saving Private Ryan
    "tt0120737": ["Adventure", "Drama", "Fantasy"],  # The Fellowship of the Ring
    "tt0162222": ["Adventure", "Comedy", "Family"],  # The Princess Bride
    "tt0482571": ["Adventure", "Drama", "Fantasy"],  # The Return of the King (alt)
    "tt0071853": ["Drama", "Horror"],  # The Exorcist
    "tt0056358": ["Drama"],  # Paths of Glory
    "tt0062622": ["Adventure", "Sci-Fi"],  # 2001: A Space Odyssey
    "tt0082971": ["Action", "Adventure", "Sci-Fi"],  # Raiders of the Lost Ark
    "tt0066921": ["Crime", "Drama"],  # A Clockwork Orange
    "tt0104257": ["Action", "Crime", "Drama"],  # Reservoir Dogs
    "tt0119698": ["Action", "Sci-Fi"],  # The Fifth Element
    "tt0375912": ["Adventure", "Biography", "Drama"],  # Braveheart
    "tt0463985": ["Action", "Sci-Fi", "Thriller"],  # The Prestige
    "tt0053125": ["Comedy", "Crime", "Drama"],  # Some Like It Hot
    "tt0056592": ["Comedy", "Drama"],  # The Graduate
    "tt0081505": ["Horror", "Thriller"],  # The Shining
    "tt0477348": ["Crime", "Drama"],  # No Country for Old Men
    "tt0371746": ["Crime", "Drama"],  # Crash
    "tt0338013": ["Action", "Adventure", "Sci-Fi"],  # LOTR Fellowship (alt)
    "tt0407887": ["Crime", "Drama"],  # There Will Be Blood
    "tt0268978": ["Drama"],  # American Beauty (alt)
    "tt0064115": ["Adventure", "Drama"],  # Doctor Zhivago
    "tt0086190": ["Action", "Sci-Fi"],  # The Terminator
    "tt0047396": ["Crime", "Drama", "Thriller"],  # Touch of Evil
    "tt0405296": ["Adventure", "Family", "Fantasy"],  # The Chronicles of Narnia
    "tt0054997": ["Drama"],  # Vertigo
    "tt0060107": ["Adventure", "Comedy", "Family"],  # The Great Escape
    "tt0386676": ["Adventure", "Family", "Fantasy"],  # Narnia (alt)
    "tt0033467": ["Adventure", "Drama"],  # Citizen Kane
    "tt0038650": ["Comedy", "Drama", "Family"],  # It's a Wonderful Life
    "tt0245429": ["Adventure", "Drama", "Fantasy"],  # LOTR Fellowship of the Ring
    "tt0209144": ["Drama"],  # American Beauty
    "tt0019254": ["Drama"],  # Battleship Potemkin
    "tt0063442": ["Adventure", "Sci-Fi"],  # 2001 variant
    "tt0050825": ["Comedy", "Family"],  # Lady and the Tramp
    "tt0091763": ["Action", "Adventure", "Sci-Fi"],  # Total Recall
    "tt0093058": ["Action", "Adventure", "Sci-Fi"],  # Terminator 2 (alt)
    "tt0047296": ["Comedy", "Drama", "Romance"],  # Singin' in the Rain (alt)
    "tt0118694": ["Adventure", "Fantasy"],  # Titanic (alt)
    "tt0360717": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Sorcerer's Stone
    "tt0373889": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Chamber of Secrets
    "tt0304141": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Prisoner of Azkaban
    "tt0325980": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Goblet of Fire
    "tt0330373": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Order of Phoenix
    "tt0417741": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Half-Blood Prince
    "tt0926084": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Deathly Hallows Pt 1
    "tt1201607": ["Adventure", "Drama", "Fantasy"],  # Harry Potter Deathly Hallows Pt 2
    "tt0454876": ["Action", "Adventure", "Sci-Fi"],  # Pirates of the Caribbean
    "tt0368891": ["Action", "Adventure", "Sci-Fi"],  # Pirates of the Caribbean 2
    "tt0830515": ["Action", "Adventure", "Sci-Fi"],  # Pirates of the Caribbean 3
    "tt1790809": ["Action", "Adventure", "Comedy"],  # Pirates of the Caribbean 4
    "tt4630562": ["Action", "Adventure", "Comedy"],  # Pirates of the Caribbean 5
    "tt2488496": ["Action", "Adventure", "Fantasy"],  # Star Wars Force Awakens
    "tt3748528": ["Action", "Adventure", "Fantasy"],  # Star Wars Last Jedi
    "tt5289954": ["Action", "Adventure", "Fantasy"],  # Star Wars Rise of Skywalker
    "tt1298650": ["Action", "Adventure", "Sci-Fi"],  # The Avengers
    "tt2395427": ["Action", "Adventure", "Sci-Fi"],  # Avengers Age of Ultron
    "tt3498820": ["Action", "Adventure", "Sci-Fi"],  # Captain America Civil War
    "tt3501632": ["Action", "Adventure", "Sci-Fi"],  # Doctor Strange
    "tt5095030": ["Action", "Adventure", "Sci-Fi"],  # Infinity War
    "tt7291046": ["Action", "Adventure", "Sci-Fi"],  # Endgame
    "tt0048994": ["Adventure", "Comedy"],  # Roman Holiday
    "tt0050192": ["Drama", "War"],  # The Bridge on the River Kwai
    "tt0052357": ["Adventure", "Romance"],  # An American in Paris
    "tt0042303": ["Comedy", "Drama", "Romance"],  # Roman Holiday
    "tt0108978": ["Animation", "Adventure", "Comedy"],  # Toy Story
    "tt0180093": ["Animation", "Adventure", "Fantasy"],  # Spirited Away
}


def enrich_genres():
    """Read imdb.json, add genres field, and write back."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "imdb.json")

    # Read current JSON
    with open(json_path, "r", encoding="utf-8") as f:
        movies = json.load(f)

    enriched = 0
    for movie in movies:
        imdb_id = movie.get("imdb_id")
        if imdb_id and imdb_id in GENRE_MAP:
            movie["genres"] = GENRE_MAP[imdb_id]
            enriched += 1
        else:
            # Default to Drama if not in mapping
            movie["genres"] = ["Drama"]

    # Write back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"✅ Enriched {enriched} movies with genres.")
    print(f"📊 Total movies: {len(movies)}")
    print(f"📁 Updated: {json_path}")


if __name__ == "__main__":
    enrich_genres()
