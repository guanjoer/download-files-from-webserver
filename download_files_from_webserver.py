import os
import requests
from bs4 import BeautifulSoup

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_name = os.path.join(dest_folder, os.path.basename(url)) # basename만
    
    try:
        # 청크 단위로 파일 읽기 위해 stream 지정 # 메모리 사용 최적화 목적
        response = requests.get(url, stream=True) 
        response.raise_for_status()  # HTTP 에러 체크
        total_length = response.headers.get('content-length')

        with open(file_name, 'wb') as file:
            if total_length is None:  # 콘텐츠 길이를 모를 때
                file.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for chunk in response.iter_content(chunk_size=1024): # 1KB 씩 파일 내용 읽기
                    if chunk:
                        dl += len(chunk)
                        file.write(chunk)
                        done = int(50 * dl / total_length)
                        print(f"\r[{('=' * done)}{' ' * (50-done)}] {dl/total_length*100:.2f}%", end='') # 파일 다운로드 진행 상황 표시

        print(f'\nDownloaded: {file_name}')
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
    
    return file_name

def download_directory(base_url, dest_folder):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {base_url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    
    for link in links:
        file_name = link.get('href')
        # 파일이 존재하고 상대 경로일 경우에만
        if file_name and not file_name.startswith('/'):
            file_url = base_url + file_name
            # 링크가 디렉토리인지 확인
            if file_name.endswith('/'):
                new_dest_folder = os.path.join(dest_folder, file_name[:-1]) # 끝에 / 제거
                new_base_url = file_url
                download_directory(new_base_url, new_dest_folder)
            else:
                download_file(file_url, dest_folder)

# 웹서버의 URL
# ex) http://192.168.0.1:8080/
# URL 끝에 /를 입력해야 한다. 그렇지 않을 시, 에러 발생
base_url = 'your_webserver_url' # your_webserver_url
# 파일이 저장될 로컬 폴더 이름
dest_folder = 'downloaded_files'  

download_directory(base_url, dest_folder)
