-- E-Commerce 샘플 데이터베이스 스키마
-- 테스트용 데이터베이스 초기화

-- 기존 테이블 삭제 (재실행 대비)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;

-- 카테고리 테이블
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE categories IS '상품 카테고리';
COMMENT ON COLUMN categories.name IS '카테고리 이름';
COMMENT ON COLUMN categories.description IS '카테고리 설명';

-- 상품 테이블
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS '상품 정보';
COMMENT ON COLUMN products.name IS '상품명';
COMMENT ON COLUMN products.price IS '판매 가격';
COMMENT ON COLUMN products.stock_quantity IS '재고 수량';

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);

-- 고객 테이블
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    registration_date DATE DEFAULT CURRENT_DATE,
    is_premium BOOLEAN DEFAULT false,
    total_spent DECIMAL(12, 2) DEFAULT 0
);

COMMENT ON TABLE customers IS '고객 정보';
COMMENT ON COLUMN customers.email IS '이메일 주소';
COMMENT ON COLUMN customers.is_premium IS '프리미엄 회원 여부';
COMMENT ON COLUMN customers.total_spent IS '누적 구매 금액';

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_country ON customers(country);

-- 주문 테이블
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(12, 2) NOT NULL,
    shipping_address TEXT,
    payment_method VARCHAR(50),
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP
);

COMMENT ON TABLE orders IS '주문 내역';
COMMENT ON COLUMN orders.status IS '주문 상태 (pending, processing, shipped, delivered, cancelled)';
COMMENT ON COLUMN orders.total_amount IS '총 주문 금액';

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

-- 주문 상세 테이블
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL
);

COMMENT ON TABLE order_items IS '주문 상세 항목';
COMMENT ON COLUMN order_items.quantity IS '주문 수량';
COMMENT ON COLUMN order_items.subtotal IS '소계 (수량 × 단가)';

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- 리뷰 테이블
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    customer_id INTEGER REFERENCES customers(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    helpful_count INTEGER DEFAULT 0
);

COMMENT ON TABLE reviews IS '상품 리뷰';
COMMENT ON COLUMN reviews.rating IS '평점 (1-5)';
COMMENT ON COLUMN reviews.helpful_count IS '도움이 됨 수';

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_customer ON reviews(customer_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- 뷰: 카테고리별 매출 통계
CREATE VIEW category_sales AS
SELECT 
    c.id,
    c.name AS category_name,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(oi.id) AS item_count,
    SUM(oi.subtotal) AS total_sales,
    AVG(oi.subtotal) AS avg_order_value
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'cancelled' OR o.status IS NULL
GROUP BY c.id, c.name;

COMMENT ON VIEW category_sales IS '카테고리별 매출 통계';

-- 함수: 고객 총 구매 금액 업데이트
CREATE OR REPLACE FUNCTION update_customer_total_spent()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE customers
    SET total_spent = (
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE customer_id = NEW.customer_id
        AND status != 'cancelled'
    )
    WHERE id = NEW.customer_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거: 주문 생성/수정 시 고객 총 구매 금액 업데이트
CREATE TRIGGER trigger_update_customer_spent
AFTER INSERT OR UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_customer_total_spent();

-- 읽기 전용 사용자 생성 (API에서 사용)
CREATE USER readonly WITH PASSWORD 'readonly123';
GRANT CONNECT ON DATABASE testdb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;

