from bs4 import BeautifulSoup
import requests
import os


def download_all(words):
    urls = []
    for word in words:
        bring = download(word)
        if type(bring) == list:
            for i in bring:
                urls.append(i)
        else:
            urls.append(bring)
    return urls


def download(word, name=None, link="https://www.signingsavvy.com/search/"):
    html_doc = requests.get(f"{link}{word}")
    soup = BeautifulSoup(html_doc.text)
    check = soup.find_all("video")
    if len(check) == 0:
        return check_results(soup, word)
    else:
        video_tags = soup.video()
        src = video_tags[0].get("src")
        if name == None:
            return src
        else:
            return src


def check_results(soup, name):
    search_result_div = soup.find("div", class_="search_results")
    if search_result_div:
        links = search_result_div.find_all("a", href=True)
        hrefs = [link["href"] for link in links]
        return download(hrefs[0], name, "https://www.signingsavvy.com/")
    else:
        return spell(name)


def spell(name):
    alpha = []
    for i in name:
        alpha.append(download(i))
    return alpha


def main():
    arr = ["I", "love", "men", "women", "children", "dogs", "cats", "wikipedia"]
    print(download_all(arr))


if __name__ == "__main__":
    main()
