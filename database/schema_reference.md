# Schema from the uploaded project

marketplaces:
marketplace_id, marketplace_name, country, currency

categories:
category_id, category_name, parent_category

brands:
brand_id, brand_name, category_id, country

sellers:
seller_id, seller_name, seller_rating, marketplace_id, warehouse_id

customers:
customer_id, first_name, last_name, gender, age, city, state, country,
email, phone, registration_date

warehouses:
warehouse_id, warehouse_name, city, state, country

products:
product_id, product_name, brand_id, category_id, marketplace_id, seller_id,
selling_price, discount_percent, stock_quantity, rating, launch_date

inventory:
inventory_id, product_id, warehouse_id, available_stock, reorder_level,
last_updated

orders:
order_id, customer_id, order_date, order_status, payment_method, total_amount

order_items:
order_item_id, order_id, product_id, quantity, unit_price, total_price

reviews:
review_id, customer_id, product_id, rating, review_title, review_text,
review_date
