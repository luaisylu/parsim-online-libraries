import argparse
import os.path
import time
from pathlib import Path 
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response, folder='books/'):
    if response.history:
        raise requests.exceptions.HTTPError

    
def download_txt(file_path, book_response):
    with open(file_path, 'wb') as file:
        file.write(book_response.content)


def download_img(image_link, folder_images):
    image_file_name = urlparse(image_link).path.split('/')[-1]
    image_path = os.path.join(folder_images, image_file_name)
    response = requests.get(image_link)
    response.raise_for_status()
    with open(image_path, 'wb') as file:
        file.write(response.content)

      
def parse_book_page(response, book_page_url):
    html_code = BeautifulSoup(response.text, 'lxml')
    book_author_and_title = html_code.find(id="content").find('h1').text
    book_name, book_author = book_author_and_title.split("::")
    book_name = book_name.strip()
    book_author = book_author.strip()
    image_url = html_code.find(id="content").find('img')['src']
    image_link = urljoin(book_page_url, image_url)
    book_comments = html_code.find(id="content").find_all(class_='black')
    book_genres = html_code.find(id="content").find("span", class_='d_book').find_all("a")
    book_comments = ''.join([comment.text for comment in book_comments])
    book_genres = ''.join([genre.text for genre in book_genres])
    book ={
        "book_name":book_name,
        "book_author":book_author,
        "image_link":image_link,
        "book_comments":book_comments,
        "book_genres":book_genres
    }
    return book

  
def main():
    parser = argparse.ArgumentParser(description='C какой по какую книги  скачать')
    parser.add_argument('start_id', type=int, help='Первая книга')
    parser.add_argument('end_id', type=int, help='Последняя книга')
    args = parser.parse_args()
    
    book_folder = "books"
    Path(book_folder).mkdir(parents=True, exist_ok=True)
  
    images_folder = "images"
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    for book_id in range(args.start_id, args.end_id):
        params = {
            "id": book_id
        }
        book_page_url = f"https://tululu.org/b{book_id}/"
        text_url="https://tululu.org/txt.php"
        
        try:
            book_response = requests.get(text_url, params=params)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            book_page_response = requests.get(book_page_url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
            book = parse_book_page(book_page_response, book_page_url)
            book_name = book["book_name"]
            image_link = book["image_link"]
            file_path = os.path.join(book_folder, book_name)
            download_img(image_link, images_folder)
            download_txt(file_path, book_response)
        except requests.exceptions.HTTPError:
            print("Такой книги нет", book_id)
        except ValueError:
            print("Ошибка кода")
        except ConnectionError:
          print("Ошибка соединения")
          time.sleep(20)
