-- 샘플 데이터 삽입

-- 카테고리 데이터
INSERT INTO categories (name, description) VALUES
('Electronics', '전자제품 및 가전제품'),
('Books', '도서 및 전자책'),
('Clothing', '의류 및 패션 액세서리'),
('Home & Garden', '가정용품 및 정원 용품'),
('Sports', '스포츠 및 아웃도어 용품'),
('Toys', '장난감 및 게임'),
('Food', '식품 및 음료'),
('Beauty', '화장품 및 뷰티 제품');

-- 상품 데이터 (50개)
INSERT INTO products (name, category_id, price, stock_quantity, description) VALUES
-- Electronics
('Laptop Pro 15', 1, 1299.99, 50, '고성능 노트북 15인치'),
('Wireless Mouse', 1, 29.99, 200, '무선 마우스 - 블루투스'),
('USB-C Hub', 1, 49.99, 150, '7-in-1 USB-C 허브'),
('Mechanical Keyboard', 1, 89.99, 80, '기계식 키보드 RGB'),
('4K Monitor 27"', 1, 399.99, 30, '27인치 4K 모니터'),
('Bluetooth Earbuds', 1, 79.99, 120, '무선 이어폰 노이즈 캔슬링'),

-- Books
('Python Programming', 2, 39.99, 100, 'Python 프로그래밍 완벽 가이드'),
('Data Science Handbook', 2, 49.99, 75, '데이터 사이언스 핸드북'),
('AI & Machine Learning', 2, 59.99, 60, 'AI와 머신러닝 입문서'),
('Web Development 101', 2, 34.99, 90, '웹 개발 기초'),

-- Clothing
('Cotton T-Shirt', 3, 19.99, 300, '면 100% 티셔츠'),
('Denim Jeans', 3, 49.99, 150, '데님 청바지'),
('Running Shoes', 3, 89.99, 100, '러닝화 - 경량'),
('Winter Jacket', 3, 129.99, 80, '겨울 재킷 방수'),
('Baseball Cap', 3, 14.99, 200, '야구 모자'),

-- Home & Garden
('Coffee Maker', 4, 79.99, 60, '자동 커피 메이커'),
('Vacuum Cleaner', 4, 149.99, 40, '무선 진공 청소기'),
('LED Desk Lamp', 4, 34.99, 100, 'LED 스탠드 조명'),
('Air Purifier', 4, 199.99, 35, '공기 청정기'),
('Garden Tools Set', 4, 44.99, 50, '정원 도구 세트'),

-- Sports
('Yoga Mat', 5, 24.99, 150, '요가 매트 - 6mm'),
('Dumbbells Set', 5, 59.99, 70, '덤벨 세트 10kg'),
('Resistance Bands', 5, 19.99, 120, '저항 밴드 세트'),
('Tennis Racket', 5, 79.99, 50, '테니스 라켓 프로'),
('Bicycle Helmet', 5, 39.99, 80, '자전거 헬멧'),

-- Toys
('LEGO Classic Set', 6, 49.99, 100, '레고 클래식 세트'),
('Remote Control Car', 6, 34.99, 80, 'RC 카 고속'),
('Board Game - Strategy', 6, 29.99, 90, '전략 보드 게임'),
('Puzzle 1000 Pieces', 6, 19.99, 60, '1000 피스 퍼즐'),
('Action Figure', 6, 24.99, 120, '액션 피규어'),

-- Food
('Organic Honey', 7, 12.99, 200, '유기농 꿀 500g'),
('Green Tea Pack', 7, 9.99, 250, '녹차 티백 50개'),
('Dark Chocolate', 7, 7.99, 180, '다크 초콜릿 70%'),
('Protein Bar Box', 7, 24.99, 150, '프로틴 바 12개입'),
('Coffee Beans', 7, 19.99, 100, '원두 커피 500g'),

-- Beauty
('Facial Cleanser', 8, 14.99, 200, '페이셜 클렌저'),
('Moisturizer Cream', 8, 24.99, 150, '보습 크림'),
('Lip Balm Set', 8, 9.99, 250, '립밤 세트 3개'),
('Shampoo & Conditioner', 8, 19.99, 180, '샴푸 컨디셔너 세트'),
('Face Mask Pack', 8, 12.99, 220, '페이스 마스크 팩 10매'),

-- 추가 상품
('Smart Watch', 1, 249.99, 60, '스마트 워치 피트니스'),
('Tablet 10"', 1, 349.99, 45, '10인치 태블릿'),
('Cookbook - Italian', 2, 29.99, 80, '이탈리아 요리책'),
('Backpack', 3, 39.99, 120, '백팩 여행용'),
('Water Bottle', 5, 14.99, 200, '보온병 500ml'),
('Playing Cards', 6, 4.99, 300, '포커 카드'),
('Olive Oil', 7, 16.99, 100, '엑스트라 버진 올리브 오일'),
('Perfume', 8, 59.99, 70, '향수 50ml'),
('Sunglasses', 3, 49.99, 90, '선글라스 UV 차단'),
('Plant Pot Set', 4, 19.99, 110, '화분 세트 3개');

-- 고객 데이터 (30명)
INSERT INTO customers (email, name, phone, city, country, is_premium) VALUES
('john.doe@email.com', 'John Doe', '555-0101', 'New York', 'USA', true),
('jane.smith@email.com', 'Jane Smith', '555-0102', 'Los Angeles', 'USA', false),
('bob.johnson@email.com', 'Bob Johnson', '555-0103', 'Chicago', 'USA', true),
('alice.brown@email.com', 'Alice Brown', '555-0104', 'Houston', 'USA', false),
('charlie.wilson@email.com', 'Charlie Wilson', '555-0105', 'Phoenix', 'USA', false),
('david.lee@email.com', 'David Lee', '555-0106', 'Seoul', 'South Korea', true),
('emma.kim@email.com', 'Emma Kim', '555-0107', 'Busan', 'South Korea', false),
('frank.park@email.com', 'Frank Park', '555-0108', 'Seoul', 'South Korea', true),
('grace.choi@email.com', 'Grace Choi', '555-0109', 'Incheon', 'South Korea', false),
('henry.jung@email.com', 'Henry Jung', '555-0110', 'Daegu', 'South Korea', false),
('isabel.garcia@email.com', 'Isabel Garcia', '555-0111', 'Madrid', 'Spain', true),
('jack.martinez@email.com', 'Jack Martinez', '555-0112', 'Barcelona', 'Spain', false),
('kate.lopez@email.com', 'Kate Lopez', '555-0113', 'London', 'UK', true),
('liam.white@email.com', 'Liam White', '555-0114', 'Manchester', 'UK', false),
('mia.taylor@email.com', 'Mia Taylor', '555-0115', 'Toronto', 'Canada', false),
('noah.anderson@email.com', 'Noah Anderson', '555-0116', 'Vancouver', 'Canada', true),
('olivia.thomas@email.com', 'Olivia Thomas', '555-0117', 'Sydney', 'Australia', false),
('peter.jackson@email.com', 'Peter Jackson', '555-0118', 'Melbourne', 'Australia', true),
('quinn.harris@email.com', 'Quinn Harris', '555-0119', 'Tokyo', 'Japan', false),
('rachel.clark@email.com', 'Rachel Clark', '555-0120', 'Osaka', 'Japan', true),
('sam.lewis@email.com', 'Sam Lewis', '555-0121', 'Berlin', 'Germany', false),
('tina.walker@email.com', 'Tina Walker', '555-0122', 'Munich', 'Germany', true),
('uma.hall@email.com', 'Uma Hall', '555-0123', 'Paris', 'France', false),
('victor.allen@email.com', 'Victor Allen', '555-0124', 'Lyon', 'France', true),
('wendy.young@email.com', 'Wendy Young', '555-0125', 'Rome', 'Italy', false),
('xavier.king@email.com', 'Xavier King', '555-0126', 'Milan', 'Italy', true),
('yara.wright@email.com', 'Yara Wright', '555-0127', 'Amsterdam', 'Netherlands', false),
('zack.scott@email.com', 'Zack Scott', '555-0128', 'Rotterdam', 'Netherlands', false),
('anna.green@email.com', 'Anna Green', '555-0129', 'Singapore', 'Singapore', true),
('ben.adams@email.com', 'Ben Adams', '555-0130', 'Hong Kong', 'Hong Kong', false);

-- 주문 데이터 (100개 주문, 최근 6개월)
INSERT INTO orders (customer_id, order_date, status, total_amount, payment_method, shipped_date, delivered_date) VALUES
-- 최근 주문들 (2025년 10월)
(1, '2025-10-08 10:30:00', 'delivered', 1379.98, 'credit_card', '2025-10-08 15:00:00', '2025-10-09 14:00:00'),
(2, '2025-10-07 14:20:00', 'shipped', 89.98, 'paypal', '2025-10-08 09:00:00', NULL),
(3, '2025-10-06 09:15:00', 'delivered', 249.97, 'credit_card', '2025-10-06 16:00:00', '2025-10-08 10:00:00'),
(4, '2025-10-05 16:45:00', 'processing', 129.99, 'credit_card', NULL, NULL),
(5, '2025-10-05 11:30:00', 'delivered', 64.97, 'debit_card', '2025-10-06 08:00:00', '2025-10-07 15:00:00'),
(6, '2025-10-04 13:20:00', 'shipped', 449.98, 'credit_card', '2025-10-05 10:00:00', NULL),
(7, '2025-10-03 10:00:00', 'delivered', 179.97, 'paypal', '2025-10-03 17:00:00', '2025-10-05 11:00:00'),
(8, '2025-10-02 15:30:00', 'cancelled', 299.99, 'credit_card', NULL, NULL),
(9, '2025-10-01 09:45:00', 'delivered', 89.97, 'debit_card', '2025-10-02 08:00:00', '2025-10-03 16:00:00'),
(10, '2025-09-30 14:15:00', 'delivered', 349.96, 'credit_card', '2025-10-01 09:00:00', '2025-10-02 13:00:00'),

-- 9월 주문들
(11, '2025-09-28 10:30:00', 'delivered', 199.98, 'paypal', '2025-09-29 08:00:00', '2025-09-30 15:00:00'),
(12, '2025-09-27 16:20:00', 'delivered', 79.98, 'credit_card', '2025-09-28 10:00:00', '2025-09-29 14:00:00'),
(13, '2025-09-26 11:15:00', 'delivered', 549.97, 'credit_card', '2025-09-27 09:00:00', '2025-09-29 11:00:00'),
(14, '2025-09-25 14:45:00', 'delivered', 169.98, 'debit_card', '2025-09-26 08:00:00', '2025-09-28 10:00:00'),
(15, '2025-09-24 09:30:00', 'delivered', 219.97, 'paypal', '2025-09-25 09:00:00', '2025-09-27 15:00:00'),
(16, '2025-09-23 15:20:00', 'delivered', 129.98, 'credit_card', '2025-09-24 10:00:00', '2025-09-26 11:00:00'),
(17, '2025-09-22 10:00:00', 'delivered', 399.99, 'credit_card', '2025-09-23 08:00:00', '2025-09-25 14:00:00'),
(18, '2025-09-21 13:30:00', 'delivered', 89.97, 'debit_card', '2025-09-22 09:00:00', '2025-09-24 10:00:00'),
(19, '2025-09-20 16:45:00', 'delivered', 279.96, 'paypal', '2025-09-21 10:00:00', '2025-09-23 15:00:00'),
(20, '2025-09-19 11:15:00', 'delivered', 159.98, 'credit_card', '2025-09-20 08:00:00', '2025-09-22 11:00:00'),

-- 8월 주문들
(21, '2025-08-28 10:30:00', 'delivered', 299.97, 'credit_card', '2025-08-29 09:00:00', '2025-08-31 14:00:00'),
(22, '2025-08-27 14:20:00', 'delivered', 189.98, 'paypal', '2025-08-28 10:00:00', '2025-08-30 15:00:00'),
(23, '2025-08-26 09:15:00', 'delivered', 449.96, 'credit_card', '2025-08-27 08:00:00', '2025-08-29 11:00:00'),
(24, '2025-08-25 16:45:00', 'delivered', 129.99, 'debit_card', '2025-08-26 09:00:00', '2025-08-28 10:00:00'),
(25, '2025-08-24 11:30:00', 'delivered', 219.97, 'credit_card', '2025-08-25 08:00:00', '2025-08-27 15:00:00'),
(1, '2025-08-20 10:00:00', 'delivered', 549.98, 'credit_card', '2025-08-21 09:00:00', '2025-08-23 14:00:00'),
(2, '2025-08-18 15:30:00', 'delivered', 169.97, 'paypal', '2025-08-19 10:00:00', '2025-08-21 11:00:00'),
(3, '2025-08-16 09:45:00', 'delivered', 289.96, 'credit_card', '2025-08-17 08:00:00', '2025-08-19 15:00:00'),
(4, '2025-08-14 14:15:00', 'delivered', 399.99, 'debit_card', '2025-08-15 09:00:00', '2025-08-17 14:00:00'),
(5, '2025-08-12 11:20:00', 'delivered', 79.98, 'credit_card', '2025-08-13 08:00:00', '2025-08-15 10:00:00');

-- 주문 상세 항목 (각 주문마다 1-4개의 상품)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
-- Order 1
(1, 1, 1, 1299.99, 1299.99),
(1, 3, 1, 49.99, 49.99),
(1, 2, 1, 29.99, 29.99),

-- Order 2
(2, 13, 1, 89.99, 89.99),

-- Order 3
(3, 11, 2, 19.99, 39.98),
(3, 7, 1, 39.99, 39.99),
(3, 31, 5, 4.99, 24.95),
(3, 40, 3, 14.99, 44.97),

-- Order 4
(4, 14, 1, 129.99, 129.99),

-- Order 5
(5, 21, 1, 24.99, 24.99),
(5, 23, 2, 19.99, 39.98),

-- Order 6
(6, 5, 1, 399.99, 399.99),
(6, 4, 1, 89.99, 89.99),

-- Order 7
(7, 16, 1, 79.99, 79.99),
(7, 26, 2, 49.99, 99.98),

-- Order 9
(9, 15, 1, 14.99, 14.99),
(9, 28, 3, 24.99, 74.98),

-- Order 10
(10, 42, 1, 249.99, 249.99),
(10, 6, 1, 79.99, 79.99),
(10, 19, 1, 19.99, 19.99),

-- 추가 주문 항목들 (나머지 주문들)
(11, 8, 2, 49.99, 99.98),
(11, 9, 2, 59.99, 119.98),
(12, 25, 1, 39.99, 39.99),
(12, 35, 2, 19.99, 39.98),
(13, 1, 1, 1299.99, 1299.99),
(13, 43, 1, 349.99, 349.99),
(14, 17, 1, 149.99, 149.99),
(14, 19, 1, 19.99, 19.99),
(15, 22, 1, 59.99, 59.99),
(15, 24, 2, 79.99, 159.98),
(16, 12, 1, 49.99, 49.99),
(16, 11, 4, 19.99, 79.96),
(17, 5, 1, 399.99, 399.99),
(18, 30, 2, 24.99, 49.98),
(18, 35, 2, 19.99, 39.98),
(19, 42, 1, 249.99, 249.99),
(19, 2, 1, 29.99, 29.99),
(20, 16, 2, 79.99, 159.98),
(21, 7, 3, 39.99, 119.97),
(21, 8, 2, 49.99, 99.98),
(21, 9, 1, 59.99, 59.99),
(22, 17, 1, 149.99, 149.99),
(22, 18, 1, 34.99, 34.99),
(23, 1, 1, 1299.99, 1299.99),
(23, 43, 1, 349.99, 349.99),
(24, 14, 1, 129.99, 129.99),
(25, 21, 2, 24.99, 49.98),
(25, 22, 2, 59.99, 119.98),
(25, 23, 2, 19.99, 39.98),
(26, 5, 1, 399.99, 399.99),
(26, 4, 1, 89.99, 89.99),
(26, 6, 1, 79.99, 79.99),
(27, 30, 4, 24.99, 99.96),
(27, 35, 4, 19.99, 79.96),
(28, 42, 1, 249.99, 249.99),
(28, 13, 1, 89.99, 89.99),
(29, 5, 1, 399.99, 399.99),
(30, 11, 4, 19.99, 79.96);

-- 리뷰 데이터 (50개)
INSERT INTO reviews (product_id, customer_id, rating, comment, helpful_count) VALUES
(1, 1, 5, '환상적인 노트북입니다. 성능이 뛰어나요!', 15),
(1, 3, 4, '좋은 제품이지만 가격이 조금 비싸네요.', 8),
(2, 2, 5, '무선 마우스 정말 편합니다.', 12),
(3, 4, 4, 'USB 허브 잘 작동합니다.', 5),
(4, 5, 5, '기계식 키보드 타건감 최고!', 20),
(5, 6, 5, '4K 모니터 화질이 선명합니다.', 18),
(6, 7, 4, '이어폰 노이즈 캔슬링 기능이 좋아요.', 10),
(7, 8, 5, 'Python 입문서로 최고입니다.', 25),
(8, 9, 4, '데이터 사이언스 공부하기 좋은 책', 14),
(11, 10, 5, '티셔츠 품질이 좋습니다.', 7),
(12, 11, 4, '청바지 착용감이 편해요.', 9),
(13, 12, 5, '러닝화 가볍고 편합니다.', 16),
(14, 13, 5, '겨울 재킷 따뜻하고 방수도 잘 돼요.', 22),
(16, 14, 5, '커피 메이커 사용하기 쉽습니다.', 11),
(17, 15, 4, '진공 청소기 흡입력이 좋아요.', 13),
(21, 16, 5, '요가 매트 두께가 적당합니다.', 8),
(22, 17, 5, '덤벨 세트 가성비 최고!', 15),
(26, 18, 5, '레고 아이와 함께 조립하기 좋아요.', 19),
(27, 19, 4, 'RC 카 속도가 빠릅니다.', 6),
(31, 20, 5, '꿀 맛이 정말 좋습니다.', 10),
(32, 21, 4, '녹차 향이 좋아요.', 7),
(36, 22, 5, '클렌저 피부에 자극이 없어요.', 14),
(37, 23, 5, '보습 크림 효과가 좋습니다.', 17),
(1, 24, 5, '노트북 배송도 빠르고 만족합니다.', 12),
(5, 25, 4, '모니터 받침대가 있으면 더 좋을 것 같아요.', 5),
(13, 26, 5, '운동화 디자인도 예쁩니다.', 9),
(14, 27, 5, '재킷 사이즈 딱 맞아요.', 11),
(16, 28, 4, '커피 머신 청소가 조금 번거롭네요.', 4),
(21, 29, 5, '요가 매트 미끄럽지 않아요.', 8),
(26, 30, 5, '레고 조각 품질이 좋습니다.', 13),
(42, 1, 5, '스마트 워치 기능이 다양합니다.', 20),
(43, 2, 4, '태블릿 화면이 크고 선명해요.', 10),
(7, 3, 5, 'Python 책 설명이 상세합니다.', 18),
(11, 4, 5, '티셔츠 여러 벌 구매했어요.', 6),
(22, 5, 4, '덤벨 무게가 적당합니다.', 7),
(31, 6, 5, '유기농 꿀 건강에 좋을 것 같아요.', 9),
(36, 7, 5, '세안제 거품이 잘 나요.', 11),
(2, 8, 4, '마우스 배터리가 오래갑니다.', 8),
(4, 9, 5, '키보드 RGB 조명이 예쁩니다.', 15),
(6, 10, 5, '이어폰 착용감이 편합니다.', 12),
(17, 11, 4, '청소기 소음이 조금 있어요.', 5),
(18, 12, 5, '램프 밝기 조절이 편리합니다.', 9),
(24, 13, 5, '테니스 라켓 스윙이 가볍습니다.', 14),
(27, 14, 4, 'RC 카 충전 시간이 조금 길어요.', 4),
(35, 15, 5, '프로틴 바 맛있습니다.', 10),
(40, 16, 5, '보온병 보온 효과 좋아요.', 13),
(44, 17, 5, '백팩 수납공간이 많아요.', 11),
(45, 18, 4, '선글라스 디자인 마음에 듭니다.', 7),
(19, 19, 5, '공기 청정기 조용하고 효과적입니다.', 16),
(25, 20, 5, '헬멧 착용감이 편안합니다.', 8);

-- 통계 확인용 쿼리 (주석)
-- SELECT COUNT(*) FROM categories;     -- 8
-- SELECT COUNT(*) FROM products;       -- 50
-- SELECT COUNT(*) FROM customers;      -- 30
-- SELECT COUNT(*) FROM orders;         -- 30
-- SELECT COUNT(*) FROM order_items;    -- ~70
-- SELECT COUNT(*) FROM reviews;        -- 50

