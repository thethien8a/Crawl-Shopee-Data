# Thêm hàm input_with_timeout vào đầu file, ngay sau các import
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import easyocr # Thư viện nhận diện chữ từ ảnh
import time
import random
import undetected_chromedriver as uc  # Thêm undetected_chromedriver để tránh chống bot
import traceback
import threading  # Thêm thư viện threading để hỗ trợ input với timeout
import pyshorteners # Thêm thư viện pyshorteners để rút gọn URL
# Xử lý cái lỗi không liên quan đến quá trình cào dữ liệu

from selenium.webdriver.common.action_chains import ActionChains

# Thêm hàm này vào file
def random_mouse_movement(driver):
    """Thực hiện các chuyển động chuột ngẫu nhiên trên trang để giả lập người dùng thực"""
    try:
        actions = ActionChains(driver)
        viewport_width = driver.execute_script("return window.innerWidth")
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Thực hiện 3-7 chuyển động chuột ngẫu nhiên
        num_movements = random.randint(3, 7)
        for _ in range(num_movements):
            x = random.randint(100, viewport_width - 200)
            y = random.randint(100, viewport_height - 200)
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.1, 0.5))
            
        # Đôi khi click vào một phần tử không quan trọng (như space trống)
        if random.random() < 0.3:
            actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
            actions.pause(random.uniform(0.5, 1.0))
            
        actions.perform()
    except Exception as e:
        print(f"Lỗi khi thực hiện chuyển động chuột: {e}")
        
def input_with_timeout(prompt, timeout=10):
    """
    Hàm đọc input với timeout, trả về None nếu hết thời gian chờ
    """
    print(prompt, end='', flush=True)
    
    # Biến để lưu kết quả input
    result = [None]
    input_event = threading.Event()
    
    # Định nghĩa hàm đọc input
    def get_input():
        result[0] = input()
        input_event.set()
    
    # Tạo và bắt đầu thread đọc input
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    # Đợi đến khi có input hoặc hết thời gian timeout
    input_received = input_event.wait(timeout)
    
    if not input_received:
        # Hết thời gian mà không có input
        print(f"\nĐã hết thời gian chờ ({timeout} giây). Tự động tiếp tục...")
        return None
    
    return result[0]

def shorten_url(url):
    # Hàm  để rút gọn URL
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)


def convert_image_url(url):
    # Hàm xử lý riêng cho các trường hợp cụ thể trong "chỉ báo khuyến mãi"
    dict = {"https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/a0842aa9294375794fd2.png":"Mall", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/4bce1bc553abb9ce061d.png":"Xử lý bởi Shopee", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/f7b68952a53e41162ad3.png":"Xử lý bởi Shopee", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/ef5ae19bc5ed8a733a70.png":"Yêu thích", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/f7b342784ff25c9e4403.png":"Yêu thích+", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/06ac2f74334798aeb1e0.png":"Choice", 
        "https://deo.shopeemobile.com/shopee/modules-federation/live/0/shopee__item-card-standard-v2/0.1.48/pc/29ae698914953718838e.png":"Premium"}
    if(url in dict):
        return dict[url]
    
    # Trong TH lầ text không có trong dict ở trên
    # Khởi tạo EasyOCR với tiếng Việt
    reader = easyocr.Reader(['vi'])
    results = reader.readtext(url)
    text=""
    for result in results:
        text = result[1]
    return text

def extract_shop_info(driver):
    """
    Hàm mới chỉ để trích xuất thông tin shop từ trang chi tiết sản phẩm
    """
    # Khởi tạo dictionary lưu thông tin shop
    shop_info = {
        "Tên shop": "Không tìm thấy tên shop",
        "Đánh giá shop": "Không có thông tin",
        "Sản phẩm đang bán": "Không có thông tin",
        "Tỉ lệ phản hồi": "Không có thông tin",
        "Thời gian phản hồi": "Không có thông tin",
        "Thời gian tham gia": "Không có thông tin",
        "Người theo dõi": "Không có thông tin"
    }
    
    try:
        # Cuộn trang để hiển thị thông tin shop
        # Lấy chiều cao trang
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        # Cuộn từ trên xuống dưới từ từ
        current_position = 0
        scroll_step = random.randint(600, 900)  # Kích thước mỗi bước cuộn
        
        while current_position < total_height:
            # Tăng vị trí cuộn
            current_position += scroll_step
            # Giới hạn vị trí không vượt quá chiều cao trang
            current_position = min(current_position, total_height)
            
            # Thực hiện cuộn
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            
            # Thêm độ trễ ngẫu nhiên giữa các lần cuộn để giống người thật
            time.sleep(random.uniform(0.5, 1.0))
            
            # Cập nhật lại tổng chiều cao sau mỗi lần cuộn vì có thể có nội dung dynamic
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height
        
        # Trước tiên, tìm tên shop
        try:
            shop_name_element = driver.find_element(By.CSS_SELECTOR, "div.fV3TIn")
            shop_info["Tên shop"] = shop_name_element.text.strip()
        except:
            print("Không tìm thấy tên shop theo CSS selector 'div.fV3TIn'")
        
        # Tìm container chính chứa thông tin shop
        shop_containers = driver.find_elements(By.CSS_SELECTOR, "div.NGzCXN")
        
        for container in shop_containers:
            # Tìm tất cả các phần tử thông tin trong container
            info_elements = container.find_elements(By.CSS_SELECTOR, "div.YnZi6x, a.YnZi6x")
            
            for element in info_elements:
                try:
                    # Tìm label (tên thông tin)
                    label_element = element.find_element(By.CSS_SELECTOR, "label.ffHYws")
                    label_text = label_element.text.strip()
                    
                    # Tìm giá trị tương ứng
                    value_element = element.find_element(By.CSS_SELECTOR, "span.Cs6w3G")
                    value_text = value_element.text.strip()
                    
                    # Cập nhật thông tin shop dựa trên label
                    if "Đánh Giá" in label_text:
                        shop_info["Đánh giá shop"] = value_text
                    if "Sản Phẩm" in label_text:
                        shop_info["Sản phẩm đang bán"] = value_text
                    if "Tỉ Lệ Phản Hồi" in label_text:
                        shop_info["Tỉ lệ phản hồi"] = value_text
                    if "Thời Gian Phản Hồi" in label_text:
                        shop_info["Thời gian phản hồi"] = value_text
                    if "Tham Gia" in label_text:
                        shop_info["Thời gian tham gia"] = value_text
                    if "Người Theo Dõi" in label_text:
                        shop_info["Người theo dõi"] = value_text
                except Exception as e:
                    print(f"Lỗi khi xử lý một phần tử thông tin shop: {e}")
                    continue
                    
    except Exception as e:
        print(f"Lỗi tổng thể khi cào thông tin shop: {e}")
        traceback.print_exc()
    
    return shop_info

def get_shop_details(driver, product_url, product_element=None, last_search_url=None):
    """
    Hàm truy cập trang chi tiết sản phẩm và lấy thông tin về shop
    dựa trên cấu trúc HTML cụ thể từ Shopee
    
    Args:
        driver: WebDriver đang chạy
        product_url: URL của sản phẩm
        product_element: Phần tử sản phẩm (WebElement)
        last_search_url: URL trang kết quả tìm kiếm gần nhất để quay lại
    """
    # Lưu lại URL hiện tại trước khi chuyển đến trang chi tiết
    if last_search_url is None:
        current_url = driver.current_url
    else:
        current_url = last_search_url
    
    print(f"Đã lưu URL trang kết quả tìm kiếm: {current_url}")
    
    # Thêm độ trễ trước khi click, giống người dùng đang xem xét sản phẩm
    time.sleep(random.uniform(1.5, 3))
    
    try:
        # Tạo một biến để theo dõi trạng thái click
        click_success = False

        # Nếu có product_element, thử nhiều cách để click vào nó
        if product_element:
            print(f"Đang cố gắng click vào sản phẩm để xem chi tiết...")
            
            # Phương pháp 1: Tìm và click vào thẻ a đầu tiên
            try:
                link_elements = product_element.find_elements(By.CSS_SELECTOR, "a")
                if link_elements:
                    print(f"Đang thử click vào thẻ a đầu tiên...")
                    # Cuộn đến phần tử trước khi click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_elements[0])
                    time.sleep(1)  # Chờ cuộn xong
                    link_elements[0].click()
                    time.sleep(2)  # Chờ để xác nhận click thành công
                    click_success = True
            except Exception as e:
                print(f"Không thể click vào thẻ a đầu tiên: {e}")
            
            # Phương pháp 2: Tìm nội dung href và điều hướng trực tiếp nếu các phương pháp click đều thất bại
            if not click_success:
                try:
                    print("Đang thử tìm URL từ thuộc tính href...")
                    # Tìm tất cả các phần tử có thuộc tính href trong product_element
                    elements_with_href = product_element.find_elements(By.CSS_SELECTOR, "[href]")
                    
                    for element in elements_with_href:
                        href = element.get_attribute("href")
                        if href and ("/item/" in href or "/product/" in href or "-i." in href):
                            print(f"Đã tìm thấy URL sản phẩm từ thuộc tính href: {href}")
                            driver.get(href)
                            time.sleep(3)  # Chờ trang tải
                            click_success = True
                            break
                except Exception as e:
                    print(f"Không thể tìm URL từ thuộc tính href: {e}")
        
        # Nếu tất cả các phương pháp click đều thất bại hoặc không có product_element
        # Điều hướng trực tiếp đến URL nếu được cung cấp
        if not click_success:
            if product_url:
                print(f"Đang truy cập trực tiếp đến URL sản phẩm: {product_url}")
                driver.get(product_url)
                click_success = True
            else:
                print("Không thể mở trang sản phẩm: không tìm thấy phần tử click được và không có URL")
                return {
                    "Tên shop": "Không thể mở trang sản phẩm",
                    "Đánh giá shop": "Không có thông tin",
                    "Sản phẩm đang bán": "Không có thông tin",
                    "Tỉ lệ phản hồi": "Không có thông tin",
                    "Thời gian phản hồi": "Không có thông tin",
                    "Thời gian tham gia": "Không có thông tin",
                    "Người theo dõi": "Không có thông tin"
                }
        
        # Đợi trang tải xong với thời gian ngẫu nhiên
        loading_time = random.uniform(5, 8)
        print(f"Đang đợi trang tải trong {loading_time:.1f} giây...")
        time.sleep(loading_time)
        
        # Cuộn trang từ trên xuống dưới một cách có hệ thống để load hết nội dung
        print("Đang cuộn trang từ trên xuống dưới để load hết nội dung...")
        
        # Lấy chiều cao trang
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        # Cuộn từ trên xuống dưới từ từ
        current_position = 0
        scroll_step = random.randint(600, 900)  # Kích thước mỗi bước cuộn
        
        while current_position < total_height:
            # Tăng vị trí cuộn
            current_position += scroll_step
            # Giới hạn vị trí không vượt quá chiều cao trang
            current_position = min(current_position, total_height)
            
            # Thực hiện cuộn
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            
            # Thêm độ trễ ngẫu nhiên giữa các lần cuộn để giống người thật
            time.sleep(random.uniform(0.8, 1.5))
            
            # Cập nhật lại tổng chiều cao sau mỗi lần cuộn vì có thể có nội dung dynamic
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height
                
        # Đợi một chút ở cuối trang như người dùng đang đọc
        time.sleep(random.uniform(2, 4))
        
        # Cuộn trở lại lên đầu trang
        print("Đang cuộn lại lên đầu trang...")
        
        # Cuộn về đầu từng đoạn
        while current_position > 0:
            current_position -= scroll_step * 2  # Cuộn lên nhanh hơn lúc cuộn xuống
            current_position = max(0, current_position)  # Đảm bảo không về âm
            
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.3, 0.7))  # Thời gian nghỉ ngắn hơn khi cuộn lên
        
        # Đợi 1-2 giây sau khi cuộn về đầu trang
        time.sleep(random.uniform(1, 2))
        
        # Khởi tạo dictionary lưu thông tin shop
        shop_info = {
            "Tên shop": "Không tìm thấy tên shop",
            "Đánh giá shop": "Không có thông tin",
            "Sản phẩm đang bán": "Không có thông tin",
            "Tỉ lệ phản hồi": "Không có thông tin",
            "Thời gian phản hồi": "Không có thông tin",
            "Thời gian tham gia": "Không có thông tin",
            "Người theo dõi": "Không có thông tin"
        }
        
        try:
            # Trước tiên, tìm tên shop
            try:
                shop_name_element = driver.find_element(By.CSS_SELECTOR, "div.fV3TIn")
                shop_info["Tên shop"] = shop_name_element.text.strip()
            except:
                print("Không tìm thấy tên shop theo CSS selector 'div.fV3TIn'")
            
            # Tìm container chính chứa thông tin shop
            shop_containers = driver.find_elements(By.CSS_SELECTOR, "div.NGzCXN")
            
            for container in shop_containers:
                # Tìm tất cả các phần tử thông tin trong container
                info_elements = container.find_elements(By.CSS_SELECTOR, "div.YnZi6x, a.YnZi6x")
                
                for element in info_elements:
                    try:
                        # Tìm label (tên thông tin)
                        label_element = element.find_element(By.CSS_SELECTOR, "label.ffHYws")
                        label_text = label_element.text.strip()
                        
                        # Tìm giá trị tương ứng
                        value_element = element.find_element(By.CSS_SELECTOR, "span.Cs6w3G")
                        value_text = value_element.text.strip()
                        
                        
                        # Cập nhật thông tin shop dựa trên label
                        if "Đánh Giá" in label_text:
                            shop_info["Đánh giá shop"] = value_text
                        if "Sản Phẩm" in label_text:
                            shop_info["Sản phẩm đang bán"] = value_text
                        if "Tỉ Lệ Phản Hồi" in label_text:
                            shop_info["Tỉ lệ phản hồi"] = value_text
                        if "Thời Gian Phản Hồi" in label_text:
                            shop_info["Thời gian phản hồi"] = value_text
                        if "Tham Gia" in label_text:
                            shop_info["Thời gian tham gia"] = value_text
                        if "Người Theo Dõi" in label_text:
                            shop_info["Người theo dõi"] = value_text
                    except Exception as e:
                        print(f"Lỗi khi xử lý một phần tử thông tin shop: {e}")
                        continue
                        
        except Exception as e:
            print(f"Lỗi tổng thể khi cào thông tin shop: {e}")
            traceback.print_exc()
        
        # Thêm thời gian trước khi quay lại, giống như người dùng đã đọc xong
        review_time = random.uniform(3, 6)
        print(f"Đã xem xong thông tin shop, đợi {review_time:.1f} giây trước khi quay lại...")
        time.sleep(review_time)
        
        # THAY ĐỔI QUAN TRỌNG: Thay vì sử dụng nút Back, quay lại bằng cách tải lại URL trang kết quả tìm kiếm
        print(f"Đang quay lại trang kết quả tìm kiếm bằng cách tải lại URL: {current_url}")
        driver.get(current_url)
        
        # Đợi trang kết quả tìm kiếm tải lại
        back_loading_time = random.uniform(5, 8)  # Tăng thời gian chờ
        print(f"Đang đợi trang kết quả tải trong {back_loading_time:.1f} giây...")
        time.sleep(back_loading_time)
        
        # MỚI: Thêm cuộn trang từ trên xuống dưới sau khi quay lại để đảm bảo các phần tử đều hiển thị
        print("Đang cuộn lại trang kết quả tìm kiếm từ trên xuống dưới để tải lại tất cả phần tử...")
        
        # Đưa trang về đầu
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Lấy chiều cao trang
        total_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        scroll_step = random.randint(300, 500)  # Bước cuộn lớn hơn để nhanh hơn
        
        # Cuộn từ trên xuống dưới để tải lại các phần tử
        while current_position < total_height:
            # Tăng vị trí cuộn
            current_position += scroll_step
            # Giới hạn vị trí không vượt quá chiều cao trang
            current_position = min(current_position, total_height)
            
            # Thực hiện cuộn
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            
            # Độ trễ dài hơn để đảm bảo các phần tử được tải hoàn toàn
            time.sleep(random.uniform(0.5, 1.0))
            
            # Cập nhật lại tổng chiều cao sau mỗi lần cuộn
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                print(f"Trang đã mở rộng từ {total_height}px lên {new_height}px")
                total_height = new_height
        
        # Cuộn lại lên đầu trang một lần nữa để sẵn sàng cho việc cào tiếp theo
        print("Đang cuộn lại lên đầu trang để chuẩn bị cho việc cào tiếp theo...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
    except Exception as e:
        print(f"Lỗi khi truy cập trang sản phẩm: {e}")
        traceback.print_exc()
        shop_info = {
            "Tên shop": "Lỗi khi truy cập trang sản phẩm",
            "Đánh giá shop": "Không có thông tin",
            "Sản phẩm đang bán": "Không có thông tin",
            "Tỉ lệ phản hồi": "Không có thông tin",
            "Thời gian phản hồi": "Không có thông tin",
            "Thời gian tham gia": "Không có thông tin",
            "Người theo dõi": "Không có thông tin"
        }
    
    return shop_info

def crawl_shopee(search_term, start_page, num_pages, get_shop_info=False):
    """
    Hàm chính để cào dữ liệu từ Shopee - đã được sửa đổi để tách biệt quá trình
    cào sản phẩm và cào thông tin shop
    
    Args:
        search_term: Từ khóa tìm kiếm
        start_page: Trang bắt đầu cào (0 là trang đầu tiên)
        num_pages: Số trang cần cào
        get_shop_info: Có lấy thông tin chi tiết về shop hay không
    
    Returns:
        Danh sách các sản phẩm đã cào được
    """
    # Khởi tạo biến driver
    driver = None
    all_products = []
    
    try:
        # Khởi tạo trình duyệt Chrome với undetected_chromedriver để tránh bị phát hiện bot
        print("Đang khởi tạo trình duyệt với undetected_chromedriver...")
        
        # Tạo Chrome Options để tối ưu hóa việc tránh phát hiện
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Ẩn dấu hiệu automation
        chrome_options.add_argument("--start-maximized")  # Mở toàn màn hình để dễ quan sát
        chrome_options.add_argument("--disable-extensions")  # Tắt extensions
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn popup
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # User-agent phổ biến
        
        # Khởi tạo trình duyệt với undetected_chromedriver
        driver = uc.Chrome(options=chrome_options)
        
        # Mở trang Shopee để xử lý đăng nhập/captcha nếu cần
        driver.get("https://shopee.vn")
        input("Vui lòng xử lý CAPTCHA hoặc đăng nhập nếu cần, sau đó nhấn Enter để tiếp tục: ")
        
        # === GIAI ĐOẠN 1: Cào thông tin cơ bản của sản phẩm trước ===
        print("\n=== GIAI ĐOẠN 1: Cào thông tin cơ bản của sản phẩm ===")
        for page_idx in range(num_pages):
            # Tính số trang thực tế từ index của vòng lặp và trang bắt đầu
            current_page = start_page + page_idx
            
            # Tạo URL trang tìm kiếm với từ khóa và số trang
            encoded_term = search_term.replace(" ", "%20")
            url = f"https://shopee.vn/search?keyword={encoded_term}&page={current_page}"
            
            print(f"\n=== Đang xử lý trang {page_idx+1}/{num_pages} (Trang thực tế trên Shopee: {current_page}): {url} ===")
            driver.get(url)
            
            # Chờ đợi cho trang tải ban đầu
            print("Đang đợi trang tải ban đầu...")
            time.sleep(5)
            
            # Bước 1: Cuộn trang để tải tất cả sản phẩm
            print("\n--- Bước 1: Cuộn trang để tải tất cả sản phẩm ---")
            scroll_page(driver)
            
            # Bước 2: Cào dữ liệu sau khi đã cuộn trang - KHÔNG lấy thông tin shop ở đây
            print("\n--- Bước 2: Cào dữ liệu sản phẩm cơ bản ---")
            page_products = crawl_products(driver, get_shop_info=False)  # Không lấy thông tin shop ngay
            all_products.extend(page_products)
            
            # Hiển thị thống kê cho trang hiện tại
            print(f"\n=== Tổng kết trang {page_idx+1}/{num_pages} (Trang Shopee: {current_page}) ===")
            print(f"- Đã cào được {len(page_products)} sản phẩm từ trang này")
            print(f"- Tổng số sản phẩm đã cào: {len(all_products)}")
            
            # Delay ngẫu nhiên giữa các trang để tránh bị chặn
            if page_idx < num_pages - 1:
                delay = random.uniform(3, 5)
                print(f"\nHoàn thành trang {page_idx+1}/{num_pages} (Trang Shopee: {current_page}). Đợi {delay:.1f} giây trước khi chuyển trang tiếp...")
                time.sleep(delay)
                
                # Hỏi người dùng có muốn tiếp tục không, với timeout 10 giây
                response = input_with_timeout("Nhấn Enter để tiếp tục sang trang tiếp, hoặc nhập 'q' để dừng (tự động tiếp tục sau 10 giây): ", 10)
                if response and response.lower() == 'q':
                    print("Dừng theo yêu cầu người dùng")
                    break
        
        # === GIAI ĐOẠN 2: Lấy thông tin chi tiết về shop nếu được yêu cầu ===
        if get_shop_info and all_products:
            print("\n\n=== GIAI ĐOẠN 2: Lấy thông tin chi tiết về shop ===")
            print(f"Tổng số sản phẩm cần lấy thông tin shop: {len(all_products)}")
            
            # Giới hạn số lượng sản phẩm trong một phiên
            max_products_per_session = 5  # Giảm xuống còn 5 sản phẩm mỗi phiên
            session_count = 0
            
            for idx, product in enumerate(all_products):
                # Lấy URL gốc của sản phẩm
                product_url = product.get("original_link", None)
                
                if product_url:
                    print(f"\n--- Đang lấy thông tin shop cho sản phẩm {idx+1}/{len(all_products)}: {product['Tên sản phẩm']} ---")
                    
                    # Truy cập trang sản phẩm
                    print(f"Đang truy cập URL sản phẩm: {product_url}")
                    driver.get(product_url)
                    
                    # Đợi trang tải - thời gian dài hơn và ngẫu nhiên hơn
                    loading_time = random.uniform(5, 10)  # Tăng thời gian chờ
                    print(f"Đang đợi trang tải trong {loading_time:.1f} giây...")
                    time.sleep(loading_time)
                    
                    # Thêm chuyển động chuột ngẫu nhiên để giống người dùng thực
                    random_mouse_movement(driver)
                    
                    # Cuộn trang với tốc độ không đều
                    print("Đang cuộn trang với tốc độ không đều để giống người dùng thực...")
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    current_position = 0
                    
                    while current_position < total_height:
                        # Cuộn với bước nhảy ngẫu nhiên
                        scroll_step = random.randint(200, 700)
                        current_position += scroll_step
                        current_position = min(current_position, total_height)
                        
                        # Đôi khi cuộn lên trên một chút rồi lại cuộn xuống (như người thực)
                        if random.random() < 0.2:
                            back_step = random.randint(50, 200)
                            temp_position = max(0, current_position - back_step)
                            driver.execute_script(f"window.scrollTo(0, {temp_position});")
                            time.sleep(random.uniform(0.5, 2.0))
                        
                        driver.execute_script(f"window.scrollTo(0, {current_position});")
                        
                        # Thời gian nghỉ ngẫu nhiên và dài hơn
                        time.sleep(random.uniform(1.0, 4.0))
                        
                        # Đôi khi dừng lâu hơn như đang đọc nội dung
                        if random.random() < 0.3:
                            print("Đang dừng lại để 'đọc' nội dung...")
                            time.sleep(random.uniform(3.0, 8.0))
                            random_mouse_movement(driver)
                    
                    # Lấy thông tin shop
                    shop_info = extract_shop_info(driver)
                    
                    # Cập nhật thông tin shop vào sản phẩm
                    product.update(shop_info)
                    
                    # Kiểm tra nếu cần nghỉ giữa các phiên
                    session_count += 1
                    if session_count >= max_products_per_session:
                        session_break = random.uniform(30, 90)  # Nghỉ 30-90 giây
                        print(f"\n!!! ĐÃ CÀO {session_count} SẢN PHẨM LIÊN TỤC !!!")
                        print(f"Đang tạm dừng {session_break:.1f} giây để tránh bị chặn...")
                        
                        # Lưu dữ liệu hiện tại để tránh mất dữ liệu
                        temp_save = f"temp_products_{time.strftime('%Y%m%d_%H%M%S')}.csv"
                        print(f"Đang lưu dữ liệu tạm thời vào {temp_save}...")
                        save_to_csv(all_products[:idx+1], temp_save)
                        
                        # Hỏi người dùng có muốn tiếp tục không
                        response = input_with_timeout(f"Đã tạm dừng sau {session_count} sản phẩm. Nhấn Enter để tiếp tục sau {session_break:.1f} giây, hoặc nhập 'q' để dừng: ", 20)
                        if response and response.lower() == 'q':
                            print("Dừng theo yêu cầu người dùng")
                            break
                        
                        # Nghỉ giữa các phiên
                        time.sleep(session_break)
                        session_count = 0  # Reset bộ đếm phiên
                        
                        # Làm mới trang Shopee trước khi tiếp tục
                        print("Đang làm mới trang Shopee...")
                        driver.get("https://shopee.vn")
                        time.sleep(random.uniform(5, 10))
                        
                        # Kiểm tra đăng nhập trước khi tiếp tục
                        if "Đăng nhập" in driver.page_source:
                            print("!!! CẢNH BÁO: Có thể bạn đã bị đăng xuất. Vui lòng đăng nhập lại !!!")
                            input("Hãy đăng nhập lại vào Shopee, sau đó nhấn Enter để tiếp tục: ")
                    
                    # Thêm độ trễ ngẫu nhiên và dài hơn giữa các sản phẩm
                    if idx < len(all_products) - 1:
                        delay = random.uniform(5, 15)  # Tăng thời gian chờ lên 5-15 giây
                        print(f"Đã lấy xong thông tin shop. Đợi {delay:.1f} giây trước khi xử lý sản phẩm tiếp...")
                        time.sleep(delay)
        
        # Lưu kết quả vào CSV
        if all_products:
            save_to_csv(all_products)
            
    except Exception as e:
        print(f"Lỗi: {e}")
        # Hiển thị thêm thông tin về lỗi
        traceback.print_exc()
    finally:
        # Cải thiện cách đóng trình duyệt để tránh lỗi
        print("Đang đóng trình duyệt...")
        
        try:
            if driver:
                # Đóng tất cả cửa sổ browser trước khi quit
                original_window = driver.current_window_handle
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        driver.close()
                
                driver.switch_to.window(original_window)
                
                # Đóng session và browser
                driver.close()
                driver.quit()
                
                # Thêm thời gian chờ ngắn để đảm bảo trình duyệt được đóng hoàn toàn
                time.sleep(0.5)
                
                # Thiết lập biến driver về None để tránh bị gọi quit thêm lần nữa
                temp = driver
                driver = None
                del temp
                
                print("Đã đóng trình duyệt thành công.")
        except Exception as e:
            print(f"Lỗi khi đóng trình duyệt: {e}")
            print("Lỗi này không ảnh hưởng đến dữ liệu đã thu thập.")
        
    return all_products

def scroll_page(driver):
    """
    Cuộn trang từ trên xuống dưới để tải tất cả sản phẩm
    """
    print("Đang cuộn trang để tải tất cả sản phẩm...")
    
    # Khởi tạo các biến theo dõi
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    scroll_step = 800  # Mỗi lần cuộn 800px
    
    # Đợi cho trang tải ban đầu
    time.sleep(3)
    
    # Cuộn từng bước đến cuối trang
    while current_position < total_height:
        # Cuộn xuống một đoạn
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        print(f"Đã cuộn xuống vị trí {current_position}px / {total_height}px")
        
        # Đợi để trang tải các sản phẩm mới
        time.sleep(random.uniform(1, 2))
        
        # Cập nhật lại chiều cao trang (có thể đã thay đổi do lazy loading)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > total_height:
            print(f"Trang đã mở rộng từ {total_height}px lên {new_height}px")
            total_height = new_height
    
    print("Đã cuộn đến cuối trang")
    
    # Cuộn lại lên trên cùng để bắt đầu cào dữ liệu
    driver.execute_script("window.scrollTo(0, 0);")
    print("Đã cuộn lại lên đầu trang và sẵn sàng cào dữ liệu")
    time.sleep(10)  # Đợi một chút sau khi cuộn lên

def crawl_products(driver, get_shop_info=False):
    """
    Cào dữ liệu sản phẩm sau khi đã cuộn trang - ĐÃ SỬA ĐỂ LƯU URL GỐC
    
    Args:
        driver: WebDriver đang chạy
        get_shop_info: Có lấy thông tin chi tiết về shop hay không (không còn sử dụng trong cách tiếp cận mới)
        
    Returns:
        Danh sách các sản phẩm đã cào được
    """
    print("Bắt đầu cào dữ liệu sản phẩm...")
    products = []
    processed_names = set()  # Tránh trùng lặp sản phẩm
    
    # Lưu lại URL trang tìm kiếm hiện tại để có thể quay lại sau
    current_search_url = driver.current_url
    print(f"URL trang tìm kiếm hiện tại: {current_search_url}")
    
    try:
        # Tìm container chính của sản phẩm 
        product_container = driver.find_element(By.CSS_SELECTOR, "ul.row.shopee-search-item-result__items")
        # Tìm tất cả các sản phẩm trong container
        product_items = product_container.find_elements(By.CSS_SELECTOR, "li.col-xs-2-4.shopee-search-item-result__item")
        print(f"Tìm thấy tổng cộng {len(product_items)} sản phẩm")
    except Exception as e:
        print(f"Không tìm thấy container sản phẩm: {e}")
        return []
    
    # Xử lý từng sản phẩm
    for index, item in enumerate(product_items, 1):
        try:
            # Tìm tên sản phẩm - cập nhật theo bộ chọn CSS chính xác và đầy đủ từ người dùng
            try:
                # Bộ chọn chính xác và đầy đủ cho tên sản phẩm
                name_element = item.find_element(By.CSS_SELECTOR, "div.line-clamp-2.break-words.min-w-0.min-h-\\[2\\.5rem\\].text-sm")
                name = name_element.text.strip()
            except:
                # Thử các bộ chọn khác nếu bộ chọn chính không hoạt động
                try:
                    name_element = item.find_element(By.CSS_SELECTOR, "div.line-clamp-2.break-words")
                    name = name_element.text.strip()
                except:
                    try:
                        name_element = item.find_element(By.CSS_SELECTOR, "div.ie3A\\+n, div[class*='ie3A+n']")
                        name = name_element.text.strip()
                    except:
                        print(f"Không thể tìm thấy tên sản phẩm {index}, đang chuyển đến sản phẩm tiếp theo")
                        continue
            
            # Bỏ qua nếu đã xử lý sản phẩm này rồi hoặc tên rỗng
            if name in processed_names or not name:
                continue
            
            # Lấy thông tin giá - cập nhật theo cấu trúc HTML thực tế
            try:
                # Sử dụng bộ chọn chính xác cho giá 
                price_container = item.find_element(By.CSS_SELECTOR, "div.truncate.flex.items-baseline")
                
                # Tìm thẻ span chứa giá thực tế (thẻ span thứ hai trong container)
                price_elements = price_container.find_elements(By.CSS_SELECTOR, "span")
                
                if len(price_elements) >= 2:
                    # Span đầu tiên thường chứa ký hiệu tiền tệ (đ), span thứ hai chứa giá trị
                    currency = price_elements[0].text.strip()
                    price_value = price_elements[1].text.strip()
                    price = currency + price_value
                else:
                    # Nếu không tìm thấy đủ span, lấy toàn bộ nội dung của container
                    price = price_container.text.strip()
            except:
                # Thử các bộ chọn khác nếu bộ chọn chính không hoạt động
                try:
                    # Thử nhiều bộ chọn khác nhau cho giá
                    selectors = [
                        "div.vioxXd, div[class*='vioxXd']", 
                        "span.ZEgDH9", 
                        "div[class*='price']",
                        "div.kPYiVF", # Bộ chọn giá phổ biến trên Shopee
                        "span[class*='font-medium'][class*='text-base']" # Bộ chọn dựa trên mẫu HTML
                    ]
                    
                    price = None
                    for selector in selectors:
                        try:
                            price_element = item.find_element(By.CSS_SELECTOR, selector)
                            price = price_element.text.strip()
                            if price:  # Nếu tìm thấy giá không rỗng, thoát khỏi vòng lặp
                                break
                        except:
                            continue
                    
                    if not price:
                        price = "Không có thông tin giá"
                except:
                    price = "Không có thông tin giá"
            
            # Lấy thông tin đã bán
            try:
                sold_selectors = [
                    "div.truncate.text-shopee-black87.text-xs.min-h-4",
                    "div.r6HknA, div[class*='r6HknA']"
                ]
                
                sold = None
                for selector in sold_selectors:
                    try:
                        sold_element = item.find_element(By.CSS_SELECTOR, selector)
                        sold = sold_element.text.strip()
                        if sold:  # Nếu tìm thấy thông tin bán không rỗng, thoát khỏi vòng lặp
                            break
                    except:
                        continue
                
                if not sold:
                    sold = "Chưa có thông tin"
            except:
                sold = "Chưa có thông tin"
            
            # Lấy đường dẫn sản phẩm
            original_link = None  # Khởi tạo biến cho URL gốc
            try:
                link_element = item.find_element(By.CSS_SELECTOR, "a")
                link = link_element.get_attribute("href")
                original_link = link  # Lưu lại link gốc để sử dụng cho việc truy cập trang sản phẩm
                link = shorten_url(link)  # Rút gọn URL để hiển thị
            except:
                link = "Không có đường dẫn"
                original_link = None
            

            # Lấy thông tin giảm giá - thêm mới theo cấu trúc HTML
            try:
                # Tìm thẻ div chứa thông tin giảm giá từ bộ chọn CSS chính xác mà người dùng cung cấp
                discount_element = item.find_element(By.CSS_SELECTOR, "div.text-shopee-primary.font-medium.bg-shopee-pink.py-0\\.5.px-1.text-sp10\\/3.h-4.rounded-\\[2px\\].shrink-0.mr-1")
                discount = discount_element.text.strip()
            except:
                # Thử các bộ chọn khác nếu bộ chọn chính không hoạt động
                try:
                    # Thử tìm các thẻ có chứa thuộc tính aria-label với giá trị có dấu %
                    discount_elements = item.find_elements(By.CSS_SELECTOR, "span[aria-label*='%']")
                    if discount_elements:
                        discount = discount_elements[0].get_attribute("aria-label")
                    else:
                        # Tìm các thẻ div có class chứa từ khóa liên quan đến giảm giá
                        discount_elements = item.find_elements(By.CSS_SELECTOR, "div[class*='shopee-pink'], div[class*='discount'], div[class*='sale']")
                        if discount_elements:
                            discount = discount_elements[0].text.strip()
                        else:
                            discount = "Không giảm giá"
                except:
                    discount = "Không giảm giá"
            
            # Lấy thông tin nhãn sản phẩm (yêu thích, yêu thích+, mall, v.v.)
            try:
                # Tìm các thẻ img với alt="flag-label" hoặc class chứa h-sp14
                label_image_selectors = [
                    "img[alt='flag-label']",
                    "img.h-sp14",
                    "img.inline-block"
                ]
                
                label_image_url = None
                for selector in label_image_selectors:
                    try:
                        # Tìm trong thẻ div chứa tên sản phẩm
                        label_image_elements = name_element.find_elements(By.CSS_SELECTOR, selector)
                        if label_image_elements:
                            label_image_url = label_image_elements[0].get_attribute("src")
                            if label_image_url:  # Nếu tìm thấy URL, thoát khỏi vòng lặp
                                break
                    except:
                        continue
                
                # Chuyển đổi URL thành tên nhãn sử dụng hàm convert_image_url có sẵn
                if label_image_url:
                    label = convert_image_url(label_image_url)
                else:
                    label = "Không có nhãn"
            except Exception as e:
                print(f"Lỗi khi xử lý nhãn sản phẩm: {str(e)}")
                label = "Không có nhãn"

            # Lấy thông tin ưu đãi (voucher, khuyến mãi)
            try:
                uu_dai_selectors = [
                    "div.truncate.bg-shopee-voucher-yellow.text-white.leading-4.text-sp10.px-px",
                    "div[class*='voucher-yellow']",
                    "div[class*='bg-shopee-voucher']",
                    "div[bis_skin_checked='1']"
                ]
                
                uu_dai = None
                for selector in uu_dai_selectors:
                    try:
                        uu_dai_elements = item.find_elements(By.CSS_SELECTOR, selector)
                        if uu_dai_elements:
                            uu_dai = uu_dai_elements[0].text.strip()
                            if uu_dai:  # Nếu tìm thấy thông tin ưu đãi không rỗng, thoát khỏi vòng lặp
                                break
                    except:
                        continue
                
                if not uu_dai:
                    uu_dai = "Không có ưu đãi"
            except Exception as e:
                print(f"Lỗi khi xử lý ưu đãi: {str(e)}")
                uu_dai = "Không có ưu đãi"

            # Lấy thông tin chỉ báo khuyến mãi (Rẻ Vô Địch, Mua Kèm Deal Sốc, v.v.)
            try:
                # Selectors that target the specific container structure shown in your image
                promo_indicator_selectors = [
                    # Target spans with truncate class specifically within the promotional container
                    "div.box-border.flex.items-center span.truncate",
                    "div[aria-hidden='true'] span.truncate[style*='color: rgb(238, 77, 45)']",
                    "div.overflow-hidden.h-4 span.truncate",
                    # Another approach: find the parent containers first
                    "div.relative.relative.flex.items-center span.truncate",
                    # And a more specific selector targeting the exact structure
                    "div.box-border.flex.space-x-1.h-5 div.pointer-events-none span.truncate"
                ]
                
                promo_indicators = []
                for selector in promo_indicator_selectors:
                    try:
                        # Tìm tất cả các span thỏa mãn điều kiện
                        promo_elements = item.find_elements(By.CSS_SELECTOR, selector)
                        for element in promo_elements:
                            # Lấy nội dung text từ các span này
                            text = element.text.strip()
                            if text and text not in promo_indicators:  # Tránh trùng lặp
                                # Kiểm tra thêm để đảm bảo không phải phần tử giá
                                parent_element = driver.execute_script("return arguments[0].parentElement", element)
                                parent_text = parent_element.text.strip() if parent_element else ""
                                # Nếu parent chứa "₫" hoặc các ký tự tiền tệ khác, đây có thể là phần tử giá
                                if "₫" not in text and "₫" not in parent_text:
                                    promo_indicators.append(text)
                    except Exception as e:
                        print(f"Lỗi khi xử lý một chỉ báo khuyến mãi: {str(e)}")
                        continue
                
                # Nối các chỉ báo lại với nhau ngăn cách bởi dấu "-"
                if promo_indicators:
                    promo_text = " - ".join(promo_indicators)
                else:
                    promo_text = "Không có"
            except Exception as e:
                print(f"Lỗi khi xử lý chỉ báo khuyến mãi: {str(e)}")
                promo_text = "Không có"
                        
            # Lấy thông tin đánh giá sản phẩm
            try:
                rating_selectors = [
                    "div.text-shopee-black87.text-xs\\/sp14.flex-none",
                    "div.text-shopee-black87",
                    "div[class*='rating']",
                    "div[bis_skin_checked='1']:not([class*='truncate'])"  # Tìm các div có bis_skin_checked nhưng không phải voucher
                ]
                
                rating = None
                for selector in rating_selectors:
                    try:
                        rating_elements = item.find_elements(By.CSS_SELECTOR, selector)
                        for element in rating_elements:
                            text = element.text.strip()
                            # Kiểm tra xem text có phải là một số (thường là từ 1-5 với một chữ số thập phân)
                            # Ví dụ: "4.9"
                            if text and any(char.isdigit() for char in text):
                                # Nếu có nhiều hơn một số, lấy cái đầu tiên thỏa mãn điều kiện rating
                                try:
                                    # Thử chuyển đổi thành số để kiểm tra xem đây có phải rating không
                                    float_val = float(text)
                                    if 0 <= float_val <= 5:  # Ratings thường từ 0-5
                                        rating = text
                                        break
                                except ValueError:
                                    continue
                        if rating:  # Nếu đã tìm thấy rating, thoát khỏi vòng lặp
                            break
                    except Exception as e:
                        continue
                
                if not rating:
                    rating = "Chưa có đánh giá"
            except Exception as e:
                print(f"Lỗi khi xử lý đánh giá sản phẩm: {str(e)}")
                rating = "Chưa có đánh giá"

            # Lấy thông tin địa chỉ/vị trí của sản phẩm
            try:
                location_selectors = [
                    "div.flex-shrink.min-w-0.truncate.text-shopee-black54.text-sp10 span.ml-\\[3px\\]",
                    "span[aria-label^='location-']",
                    "span.align-middle:not(:first-child)",
                    "div[class*='text-shopee-black54'] span.align-middle"
                ]
                
                location = None
                for selector in location_selectors:
                    try:
                        location_elements = item.find_elements(By.CSS_SELECTOR, selector)
                        if location_elements:
                            for element in location_elements:
                                text = element.text.strip()
                                if text:
                                    location = text
                                    break
                        
                        # Thử cách khác nếu không tìm thấy
                        if not location:
                            # Tìm theo aria-label có chứa location
                            aria_elements = item.find_elements(By.CSS_SELECTOR, "span[aria-label^='location-']")
                            if aria_elements:
                                aria_label = aria_elements[0].get_attribute("aria-label")
                                if aria_label and aria_label.startswith("location-"):
                                    location = aria_label.replace("location-", "")
                        
                        if location:  # Nếu tìm thấy địa chỉ, thoát khỏi vòng lặp
                            break
                    except Exception as e:
                        continue
                
                if not location:
                    location = "Không có thông tin"
            except Exception as e:
                print(f"Lỗi khi xử lý thông tin địa chỉ: {str(e)}")
                location = "Không có thông tin"
            
            # Hiển thị tiến độ
            if index % 5 == 0 or index == 1:  # Hiển thị cho sản phẩm đầu tiên và sau mỗi 5 sản phẩm
                print(f"Đang xử lý sản phẩm {index}/{len(product_items)}")

            # Thêm vào danh sách kết quả
            product = {
                # Ngày cào dữ liệu
                "Tên sản phẩm": name,
                "Giá bán hiển thị trên feed": price,
                "Giảm giá hiển thị trên feed": discount,
                "Đã bán": sold,
                "Nhãn": label,
                "Ưu đãi": uu_dai,
                "Chỉ báo khuyến mãi": promo_text,
                "Đánh giá": rating,
                "Địa chỉ": location,  # Thêm thông tin địa chỉ
                "Link": link,
                "original_link": original_link  # Lưu URL gốc để sử dụng trong giai đoạn 2
            }
            
            # QUAN TRỌNG: Không lấy thông tin shop ngay tại đây nữa
            
            products.append(product)
            processed_names.add(name)
            
            # Thêm độ trễ nhỏ để tránh quá tải
            if index % 10 == 0:
                time.sleep(random.uniform(0.5, 1))
                
            # Hiển thị tiến độ cào dữ liệu
            if index % 5 == 0 or index == len(product_items):
                print(f"Đã cào {index}/{len(product_items)} sản phẩm ({(index/len(product_items)*100):.1f}%)")
                
        except Exception as e:
            print(f"Lỗi khi xử lý sản phẩm {index}: {str(e)}")
            continue
    
    print(f"Hoàn thành cào dữ liệu. Đã thu thập {len(products)} sản phẩm.")
    return products


def save_to_csv(products, filename=None):
    """
    Lưu dữ liệu sản phẩm vào file CSV
    """
    # Tạo một bản sao của danh sách sản phẩm để chỉnh sửa
    products_to_save = []
    
    # Loại bỏ trường original_link trước khi lưu
    for product in products:
        product_copy = product.copy()
        if 'original_link' in product_copy:
            del product_copy['original_link']
        products_to_save.append(product_copy)
    
    # Nếu không có tên file, tạo tên mặc định
    if filename is None:
        filename = f"shopee_products_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        df = pd.DataFrame(products_to_save)
        df.to_csv(filename, index=False, encoding="utf-8-sig")  # utf-8-sig để hỗ trợ tiếng Việt trên Excel
        print(f"\n=== Đã lưu {len(products)} sản phẩm vào file {filename} ===")
        
    except Exception as e:
        print(f"Lỗi khi lưu file CSV: {e}")
        # Thử lưu với encoding khác nếu gặp lỗi
        df.to_csv(filename, index=False, encoding="utf-8", errors="ignore")
        print(f"Đã lưu file {filename} (có thể mất một số ký tự đặc biệt)")

if __name__ == "__main__":
    print("\n=== CÔNG CỤ CÀO DỮ LIỆU SHOPEE VỚI UNDETECTED_CHROMEDRIVER ===")
    print("Lưu ý: Trình duyệt sẽ hiển thị để bạn theo dõi quá trình cào dữ liệu")
    print("Công cụ này sử dụng undetected_chromedriver để tránh phát hiện bot\n")
    
    # Thông số tìm kiếm
    search_keyword = input("Nhập từ khóa tìm kiếm (ví dụ: mỹ phẩm): ") or "mỹ phẩm"
    
    # Thêm tùy chọn trang bắt đầu
    try:
        start_page = int(input("Nhập trang bắt đầu cào (0 là trang đầu tiên): ") or "0")
        start_page = max(0, start_page)  # Đảm bảo trang bắt đầu không âm
    except ValueError:
        print("Giá trị không hợp lệ. Sử dụng trang bắt đầu mặc định là 0.")
        start_page = 0
    
    try:
        num_pages = int(input("Nhập số trang cần cào (1-100): ") or "1")
        # Giới hạn số trang hợp lý
        num_pages = min(max(1, num_pages), 100)
    except ValueError:
        print("Giá trị không hợp lệ. Sử dụng số trang mặc định là 1.")
        num_pages = 1
        
    # Luôn luôn lấy thông tin chi tiết về shop
    get_shop_info = True
    print("Chế độ lấy thông tin chi tiết về shop được bật. Quá trình cào sẽ mất nhiều thời gian hơn.")
    
    print("\nLưu ý về anti-bot:")
    print("- Cần đăng nhập thủ công để tránh bị phát hiện")
    print("- Không nên cào quá nhiều trang liên tục")
    print("- Sử dụng thời gian nghỉ hợp lý giữa các trang")
    
    # Bắt đầu quá trình cào
    print(f"\nBắt đầu cào dữ liệu cho từ khóa '{search_keyword}' trên {num_pages} trang, bắt đầu từ trang {start_page}...")
    crawl_shopee(search_keyword, start_page, num_pages, get_shop_info)