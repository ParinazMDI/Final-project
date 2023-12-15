



#getting the cover image and display
import requests
from IPython.display import Image, display
import pandas as pd

data_book=pd.read_csv("data_book.csv")
New_df=pd.read_csv("New_df.csv")
official_genres = {"art", "biography", "business", "chick-lit", "children's", "christian", "classics",
          "comics", "contemporary", "cookbooks", "crime", "books", "fantasy", "fiction",
          "gay-and-lesbian", "graphic-novels", "historical-fiction", "history", "horror",
          "humor-and-comedy", "manga", "memoir", "music", "mystery", "nonfiction", "paranormal",
          "philosophy", "poetry", "psychology", "religion", "romance", "science", "science-fiction", 
          "self-help", "suspense", "spirituality", "sports", "thriller", "travel", "young-adult"}

import ast
New_df['genres'] = New_df['genres'].apply(lambda x: [element for element in ast.literal_eval(x) if element in official_genres])


def get_book_cover_url(title):
    title_query = title.replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q={title_query}&maxResults=1"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        if items:
            book_info = items[0]
            image_links = book_info['volumeInfo'].get('imageLinks', {})
            return image_links.get('thumbnail')  # Returns the URL of the thumbnail image
    return "No cover image found"

def display_book_cover(title):
    cover_url = get_book_cover_url(title)
    if cover_url != "No cover image found":
        display(Image(url=cover_url))
    else:
        print("Cover image not found.")
        
        
        
        #connection with GPT
import openai

openai.api_key = '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'

def gpt_response(recommended_title, message_history, **params):
    # Construct the prompt
    prompt = f"Can you provide a summary and your thoughts on the book '{recommended_title}'?"
    message_history.append({"role": "user", "content": prompt})

    # Set the parameters for the GPT model
    completion_params = {
        "model": "gpt-3.5-turbo",
        "messages": message_history,
        **params
    }

    # Get the completion from the GPT model
    completion = openai.ChatCompletion.create(**completion_params)
    message_history.append({"role": "assistant", "content": f"{completion.choices[0].message.content}"})

    return message_history

def complete_last_sentence(text):
    sentences = text.split('. ')
    if len(sentences) > 1 and not text.endswith('.'):
        return '. '.join(sentences[:-1]) + '.'
    return text



def get_user_choice():
    print("How would you like to search for a book?")
    print("1. By Title\n2. By Author\n3. By Genre")
    return input("Enter your choice (1, 2, or 3): ")



def find_book_by_title(title):
    found = data_book[data_book['original_title'].str.lower() == title.lower()]
    if not found.empty:
        print(f"{title} is one of the best books of 2023.")
        recommendation = data_book[data_book['original_title'].str.lower() != title.lower()].sample()
        recommended_title = recommendation.iloc[0]['original_title']
        print(f"Interested in another standout read? Check out other best picks from 2023!: {recommendation.iloc[0]['original_title']} by {recommendation.iloc[0]['authors']}")
        display_book_cover(recommended_title)
        
        message_history = [{"role": "system", "content": "Start of conversation."}]
        while True:
            user_input = input(f"Do you want to know more about '{recommended_title}'? (yes/no/exit): ").strip().lower()
            if user_input == "yes":
                message_history = gpt_response(recommended_title, message_history, max_tokens=150, temperature=0.7)
                response = message_history[-1]["content"]
                complete_response = complete_last_sentence(response)
                print(complete_response)
                break
            elif user_input == "no":
                break
            elif user_input == "exit":
                print("Hope you found some great recommendations! ")
                return
            
            else:
                print("Invalid input. Please answer with 'yes', 'no', or 'exit'.")

        while True:
            user_input = input("Do you want to search another book? (yes/no): ").strip().lower()
            if user_input == "yes":
                new_title = input("Enter the book title: ").strip()
                find_book_by_title(new_title)
                break
            elif user_input == "no":
                print("Enjoy our picks! See you soon!")
                break
            else:
                print("Invalid input. Please answer with 'yes' or 'no'.")
        
        
    else:
        found = New_df[New_df['original_title'].str.lower() == title.lower()]
        if not found.empty:
            book = found.iloc[0]
            print(f"Great pick! '{title}' is ready for you in our collection – it's like it knew you were coming.")
#             print(f"Average Rating: {book['average_rating']}, Description: {book['description']}")
            
            recommendation = New_df[(New_df['cluster'] == book['cluster']) & (New_df['original_title'].str.lower() != title.lower())].sample()
            if not recommendation.empty:
                book_title = recommendation.iloc[0]['original_title']
                print(f"You might be interested in : {book_title} by {recommendation.iloc[0]['authors']}")
                display_book_cover(book_title)
                
                while True:
                    user_input = input(f"Do you want to know more about '{book_title}'? (yes/no/exit): ").strip().lower()
                    if user_input == "yes":
                        print(f"Average Rating: {recommendation.iloc[0]['average_rating']}, Description: {recommendation.iloc[0]['description']}")
                        break
                    elif user_input == "no":
                        break
                    elif user_input == "exit":
                        print("Search ended. Happy exploring!")
                        return
                    else:
                        print("Invalid input. Please answer with 'yes', 'no', or 'exit'.")

                while True:
                    user_input = input("Do you want to search another book? (yes/no/exit): ").strip().lower()
                    if user_input == "yes":
                        new_title = input("Enter the book title: ").strip()
                        find_book_by_title(new_title)
                        break
                    elif user_input == "no":
                        print("Enjoy your day with my recommendation!")
                        break
                    elif user_input == "exit":
                        print("Search ended. Happy exploring! ")
                        return
                    else:
                        print("Invalid input. Please answer with 'yes', 'no', or 'exit'.")
            else:
                print("No other books found in the same group.")
                handle_genre_search()
        else:
            handle_genre_search()

def handle_genre_search():
    while True:
        user_input = input("Book not found. Would you like to try searching by genre? (yes/no): ").strip().lower()
        if user_input == "yes":
            genre = input("Enter the genre: ").strip()
            find_book_by_genre(genre)
            break
        elif user_input == "no":
            print("Happy to help! Have a great time! ")
            break
        else:
            print("Invalid input. Please answer with 'yes' or 'no'.")








            
            
def find_book_by_author(author):
    found = data_book[data_book['authors'].str.lower() == author.lower()]
    previously_recommended = set()

    if not found.empty:
        print(f"{author}'s books are in the Best of 2023.")
        recommendation = found.sample()
        recommended_title = recommendation.iloc[0]['original_title']
        previously_recommended.add(recommendation.iloc[0]['original_title'])
        print(f"Recommendation: {recommendation.iloc[0]['original_title']} by {author}")
        display_book_cover(recommended_title)
        message_history = [{"role": "system", "content": "Start of conversation."}]
        while True:
            user_input = input(f"Do you want to know more about '{recommended_title}'? (yes/no): ").strip().lower()
            if user_input == "yes":
                message_history = gpt_response(recommended_title, message_history, max_tokens=150, temperature=0.7)
                response = message_history[-1]["content"]
                complete_response = complete_last_sentence(response)
                print(complete_response)
                break
            elif user_input == "no":
                break
            else:
                print("Invalid input. Please answer with 'yes' or 'no'.")

        while True:
            user_input = input("Do you want to search for another book by the same author? (yes/no): ").strip().lower()
            if user_input == "yes":
                remaining_books = found[~found['original_title'].isin(previously_recommended)]
                if not remaining_books.empty:
                    recommendation = remaining_books.sample()
                    recommended_title = recommendation.iloc[0]['original_title']
                    previously_recommended.add(recommended_title)
                    print(f"Another best choice of the 2023: {recommended_title} by {author}")
                    display_book_cover(recommended_title)
                    
                    while True:
                        detail_input = input(f"Do you want to know more about '{recommended_title}'? (yes/no): ").strip().lower()
                        if detail_input == "yes":
                    
                            message_history = gpt_response(recommended_title, message_history, max_tokens=150, temperature=0.7)
                            response = message_history[-1]["content"]
                            complete_response = complete_last_sentence(response)
                            print(complete_response)
                            break
                        elif detail_input == "no":
                            break
                        else:
                            print("Invalid input. Please answer with 'yes' or 'no'.")

                        
                    
                    
                else:
                    print("I shared all my info!")
                    
                    user_input = input("Do you want to search for another author? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        new_author = input("Enter the author's name: ").strip()
                        find_book_by_author(new_author)
                    elif user_input == "no":
                        print("Enjoy your day with your chosen book!")
                    else:
                        print("Invalid input. Please answer with 'yes' or 'no'.")
                    break
            elif user_input == "no":
                print("Enjoy your day with my recommendation!")
                break
            else:
                print("Invalid input. Please answer with 'yes' or 'no'.")
                
        
        
    else:
        found = New_df[New_df['authors'].str.lower() == author.lower()]
        if not found.empty:
            while True:
                available_books = found[~found['original_title'].isin(previously_recommended)]
                if available_books.empty:
                    print(f"Oops!I've shared all of {author}'s books in my dataset.")
                    while True:
                        user_input = input("Would you like me to look up more works by another author? (yes/no): ").strip().lower()
                        if user_input == "yes":
                            new_author = input("Enter the new author's name: ").strip()
                            find_book_by_author(new_author)
                            break
                        elif user_input == "no":
                            print("I'm always here to share some fantastic recommendations whenever you need them!")
                            break
                        else:
                            print("Invalid input. Please answer with 'yes' or 'no'.")
                    break    

                book = available_books.sample().iloc[0]
                book_title = book['original_title']
                previously_recommended.add(book['original_title'])
                print(f"A must-read that we think you'll love!,it's {book['original_title']} by {author}")
                display_book_cover(book_title)
            
                
                while True:
                    user_input = input("Do you need more info about this book? (yes/no): ").strip().lower()
                    if user_input in ["yes", "no"]:
                        break
                    print("Invalid input. Please answer with 'yes' or 'no'.")

                if user_input == "yes":
                    print(f"Average Rating: {book['average_rating']}, Description: {book['description']}")

                while True:
                    user_input = input("Would you like me to look up more works by the same author? (yes/no): ").strip().lower()
                    if user_input in ["yes", "no"]:
                        break
                    print("Invalid input. Please answer with 'yes' or 'no'.")

                if user_input != "yes":
                    print("Enjoy your day with my recommendation!")
                    break
        else:
            while True:
                user_input = input("No books found by this author. Would you like to try searching by title? (yes/no/exit): ").strip().lower()
                if user_input in ["yes", "no","exit"]:
                    break
                print("Invalid input. Please answer with 'yes' , 'no' or 'exit'.")

            if user_input == "yes":
                title = input("Enter the book title: ").strip()
                find_book_by_title(title)
            elif user_input == "no":
                print("I did my best to make you happy!")
            elif user_input == "exit":
                print("See you then!")
                
                



def find_book_by_genre(genre):
    genre = genre.lower()
    matched_books = New_df[New_df['genres'].apply(lambda genres: any(g.lower() == genre for g in genres))]

    if matched_books.empty:
        print(f"No books found in the genre '{genre}'.")
        while True:
            user_input = input("Do you want to try again with a different genre? (yes/no): ").strip().lower()
            if user_input == "yes":
                new_genre = input("Enter the new genre: ").strip()
                find_book_by_genre(new_genre)
                break
            elif user_input == "no":
                while True:
                    user_input = input("Would you like to try searching by the name of the book? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        title = input("Enter the book title: ").strip()
                        find_book_by_title(title)
                        break
                    elif user_input == "no":
                        print("I am always here to recommend you!")
                        break
                    else:
                        print("Invalid input. Please answer with 'yes' or 'no'.")
                break
            else:
                print("Invalid input. Please answer with 'yes' or 'no'.")
        return
    
    while True:
        recommendation = matched_books.sample()
        book_title = recommendation.iloc[0]['original_title']
        print(f"Recommendation in '{genre}' genre: {book_title} by {recommendation.iloc[0]['authors']}")
        display_book_cover(book_title)
        
        while True:
            user_input = input(f"Do you want to know more about '{book_title}'? (yes/no/exit): ").strip().lower()
            if user_input == "yes":
                print(f"Rate of this book: {recommendation.iloc[0]['average_rating']}")
                print(f"Summary of your choice: {recommendation.iloc[0]['description']}")
                break
            elif user_input == "no":
                break
            elif user_input == "exit":
                print("Grateful you chose me for your recommendations!")
                return
            
            else:
                print("Invalid input. Please answer with 'yes' , 'no' or 'exit'.")

        while True:
            user_interest = input("Are you up for another great find in this genre? (yes/no/exit): ").strip().lower()
            if user_interest == "yes":
                break
            elif user_interest == "no" or user_interest == "exit":
                print("Enjoy your day with my recommendation!" if user_interest == "no" else "Thank you for choosing me!")
                return
            else:
                print("Invalid input. Please answer with 'yes' , 'no' or 'exit'.")

        
        
        


        


def main():
    user_choice = get_user_choice().strip()
    if user_choice == "1":
        title = input("Enter the book title: ").strip()
        find_book_by_title(title)
    elif user_choice == "2":
        author = input("Enter the author's name: ").strip()
        find_book_by_author(author)
    elif user_choice == "3":
        genre = input("Enter the genre: ").strip()
        find_book_by_genre(genre)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()



    
