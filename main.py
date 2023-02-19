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


def download_img(image_link, folder_images):
    file_name_image = urlparse(image_link).path.split('/')[-1]
    file_path_image = os.path.join(folder_images, file_name_image)
    response = requests.get(image_link)
    response.raise_for_status()
    with open(file_path_image, 'wb') as file:
        file.write(response.content)

      
def parse_book_page(response, book_page_url):
    html_code = BeautifulSoup(response.text, 'lxml')
    book_author_and_title = html_code.find(id="content").find('h1').text
    book_name, book_author = book_author_and_title.split("::")
    book_name = book_name.strip()
    book_author = book_author.strip()
    image_url = html_code.find(id="content").find('img')['src']
    image_link = urljoin(book_page_url, image_url)
    comments_url = html_code.find(id="content").find_all(class_='black')
    genres_url = html_code.find(id="content").find("span", class_='d_book').find_all("a")
    book_comments = ''.join([comment.text for comment in comments_url])
    book_genres = ''.join([genre.text for genre in genres_url])
    characteristics_book ={
        "book_name":book_name,
        "book_author":book_author,
        "image_link":image_link,
        "book_comments":book_comments,
        "book_genres":book_genres
    }
    return characteristics_book

  
def main():
    parser = argparse.ArgumentParser(description='C какой по какую книги  скачать')
    parser.add_argument('start_id', type=int, help='Первая книга')
    parser.add_argument('end_id', type=int, help='Последняя книга')
    args = parser.parse_args()
    
    book_folder = "books"
    Path(book_folder).mkdir(parents=True, exist_ok=True)
  
    images_folder = "images"
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    for id_book in range(args.start_id, args.end_id):
        params = {
            "id": id_book
        }
        book_page_url = f"https://tululu.org/b{id_book}/"
        text_url="https://tululu.org/txt.php"
        
        try:
            response_book = requests.get(text_url, params=params)
            response_book.raise_for_status()
            check_for_redirect(response_book)
            response_page_book = requests.get(book_page_url)
            response_page_book.raise_for_status
            characteristics_book = parse_book_page(response_page_book, book_page_url)
            book_name = characteristics_book["book_name"]
            image_link = characteristics_book["image_link"]
            book_comments = characteristics_book["book_comments"]
            book_genres = characteristics_book["book_genres"]
            file_path = os.path.join(book_folder, book_name)
            download_img(image_link, images_folder)
            download_txt(file_path, response_book)
        except requests.exceptions.HTTPError:
            print("Такой книги нет", id_book)
        except ValueError:
            print("Ошибка кода")
        except ConnectionError:
          print("Ошибка соединения")

          
if __name__ == "__main__":  
    main()
