import argparse
import os.path
from pathlib import Path 
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response, folder='books/'):
    if response.history:
        raise requests.exceptions.HTTPError

    
def download_txt(file_path, response_book):
    with open(file_path, 'wb') as file:
        file.write(response_book.content)


def download_img(link_image, folder_images):
    file_name_image = urlparse(link_image).path.split('/')[-1]
    file_path_imge = os.path.join(folder_images, file_name_image)
    response = requests.get(link_image)
    response.raise_for_status()
    with open(file_path_imge, 'wb') as file:
        file.write(response.content)

      
def parse_book_page(response):
    html_code = BeautifulSoup(response.text, 'lxml')
    author_and_title_book = html_code.find(id="content").find('h1').text
    book_name, author_book = author_and_title_book.split("::")
    book_name = book_name.strip()
    author_book = author_book.strip()
    image_path = html_code.find(id="content").find('img')['src']
    link_image = urljoin("https://tululu.org", image_path)
    comments_path = html_code.find(id="content").find_all(class_='black')
    genres_path = html_code.find(id="content").find("span", class_='d_book').find_all("a")
    list_of_comments = ''.join([comment.text for comment in comments_path])
    list_of_genres = ''.join([genre.text for genre in genres_path])
    website_statistic ={
        "book_name":book_name,
        "author_book":author_book,
        "link_image":link_image,
        "list_of_comments":list_of_comments,
        "list_of_genres":list_of_genres
    }
    return website_statistic

  
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', type=int)
    parser.add_argument('end_id', type=int)
    args = parser.parse_args()
    
    book_folder = "books"
    Path(book_folder).mkdir(parents=True, exist_ok=True)
  
    folder_images = "images"
    Path(folder_images).mkdir(parents=True, exist_ok=True)
    for id_book in range(args.start_id, args.end_id):
        params = {
            "id": id_book
        }
        book_page_url = f"https://tululu.org/b{id_book}/"
        text_url="https://tululu.org/txt.php"
        response_book = requests.get(text_url, params=params)
      
        try:
            response_book.raise_for_status()
            check_for_redirect(response_book)
            response_page_book = requests.get(book_page_url)
            book_name = parse_book_page(response_page_book)["book_name"]
            link_image = parse_book_page(response_page_book)["link_image"]
            list_of_comments = parse_book_page(response_page_book)["list_of_comments"]
            list_of_genres = parse_book_page(response_page_book)["list_of_genres"]
            file_path = os.path.join(book_folder, book_name)
            print(list_of_comments)
        except requests.exceptions.HTTPError:
            print("Такой книги нет", id_book)
        except ValueError:
            print("Ошибка кода")
       
if __name__ == "__main__":  
    main()
