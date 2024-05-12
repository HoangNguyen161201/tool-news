from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import os
from untils import generate_content, generate_to_voice, generate_image, generate_video_by_image, concact_content_videos, count_folders

try:
    browser = webdriver.Chrome()
    browser.get('https://www.24h.com.vn/tin-tuc-trong-ngay-c46.html')

    # try:
    # await browser load end
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'md5'))
    )

    # get link to redirect to new
    newLinks = browser.find_elements(By.CLASS_NAME, 'md5')
    href = newLinks[2].get_attribute('href')
    browser.get(href)

    # await browser load end
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'cate-24h-foot-arti-deta-content-main'))
    )

    # Scroll smoothly to the bottom of the page
    viewScreen = 100
    body_height = browser.execute_script("return document.body.scrollHeight;")
    while viewScreen <= (body_height - 100):
        browser.execute_script(f"window.scrollTo(0, {viewScreen});")
        time.sleep(0.03)
        viewScreen += 50
        body_height = browser.execute_script("return document.body.scrollHeight;")


    # get title
    titleElement = browser.find_elements(By.CLASS_NAME, 'clrTit')[0]
    title = titleElement.text

    #contents -------------------------------------
    content = ''
    content += browser.find_element(By.TAG_NAME, 'strong').text
    article = browser.find_element(By.CLASS_NAME, 'cate-24h-foot-arti-deta-info')

    # Loại bỏ các thẻ <p> trong phần tử <div class="bv-lq"> trong article
    try:
        browser.execute_script("arguments[0].remove()", article.find_element(By.CLASS_NAME, 'bv-lq'))
    except:
        print('An exception occurred')
    try:
        browser.execute_script("arguments[0].remove()", browser.find_element(By.CLASS_NAME, 'footer-24h'))
    except:
        print('An exception occurred')
    try:
        browser.execute_script("arguments[0].remove()", browser.find_element(By.CLASS_NAME, 'cate-24h-foot-arti-deta-related-news'))
    except:
        print('An exception occurred')
    try:
        browser.execute_script("arguments[0].remove()", browser.find_element(By.ID, 'lazyLoad_content_template_cate'))
    except:
        print('An exception occurred')


    # all content by p tag
    paragraphs = article.find_elements(By.XPATH, "//p[not(contains(@class, 'img_chu_thich_0407')) and not(contains(@class, 'text-uppercase')) and not(contains(@class, 'cate-24h-foot-home-tour-news-readmore')) and not(contains(@class, 'linkOrigin'))]")
    for paragraph in paragraphs:
        content += paragraph.text

    # get images --------------------------------
    images =  article.find_elements(By.CLASS_NAME, 'news-image')
    href_images = [element.get_attribute('src') for element in images]
    href_images = [href for href in href_images if "gif" not in href]

    # create folder to save files to edit video
    count_folder = count_folders('./videos')
    path_folder = f'./videos/video-{count_folder}'
    try:
        os.makedirs(path_folder)
    except:
        print('folder existed')

    #import images
    path_videos = []
    for key, item in enumerate(href_images):
        print(item)
        img_path = f"{path_folder}/image-{key}.jpg"
        img_blur_path = f"{path_folder}/image-blur-{key}.jpg"
        generate_image(item, img_path, img_blur_path)
        random_number = random.randint(5, 10)
        generate_video_by_image(
            1 if key % 2 == 0 else None,
            img_path,
            img_blur_path,
            f'{path_folder}/video-{key}.mp4',
            random_number
        )
        path_videos.append(f"{path_folder}/video-{key}.mp4")

    # # generate title by ai
    # title = generate_content(f'hãy đặt lại title youtube cho tôi: {title}')
    # # generate content by ai
    # content = generate_content(f'hay viết lại đoạn văn sau và có độ dài ký tự là {content.__len__()}: {content}')
    # time.sleep(60)
    # # generate tags
    # tags = generate_content(f'hãy gợi ý tags để tui gắn vào youtube, title của video là {title}, content là {content}')

    # generate voice ---------------------------------------
    generate_to_voice(title, f"{path_folder}/title-voice.mp3")
    generate_to_voice(content, f"{path_folder}/content-voice.mp3")

    # concact content video ---------------------------------------
    concact_content_videos(f"{path_folder}/content-voice.mp3",path_videos, f'{path_folder}/video-content.mp4' )
    
    # save content to file txt
    with open(f"{path_folder}/result.txt", "w",  encoding="utf-8") as file:
        # Viết vào file
        file.write(f"link: {href}.\n")
        file.write(f"title: {title}\n")
        file.write(f"content: {content}\n")
        # file.write(f"tags: {tags}\n")
        
    print('title')
    print(title)
    print('content')
    print(content)
except NameError:
    print(NameError)
    browser.quit()


