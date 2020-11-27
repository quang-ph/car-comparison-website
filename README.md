#Hệ thống so sánh xe giá xe hơi Careno
Hệ thống được phát triển và cài đặt thử nghiệm trên hệ điều hành Ubuntu 16.04

##Yêu cầu:
* Python 3.5
* Pipenv
* MongoDB

##Các bước cài đặt:
* Giải nén thư mục mã nguồn project
* Di chuyển đến thư mục gốc của project (mặc định là sosanhgiaxe)
    ```
    cd sosanhgiaxe
    ```
* Cài đặt các thư viện cần thiết cho project được qui định trong Pipfile
    ```
    pipenv install
    ```
* Khởi chạy môi trường cho project
    ```
    pipenv shell
    ```
* Khởi chạy MongoDB
    ```
    sudo service mongod start
    ```
* Thu thập dữ liệu phiên bản xe
    ```
    scrapy crawl basecar
    ```
* Thu thập dữ liệu bài đăng bán xe
    ```
    Lần lượt thay thế SELECTOR_PATH trong car_scraper/spiders/car_post_crawler.py bằng các file trong thư mục car_scraper/selector và chạy câu lệnh
    
    scrapy crawl carpost 
    ```
* Chạy file api/res_api.py
* Truy cập hệ thống tại địa chỉ http://localhost:5000