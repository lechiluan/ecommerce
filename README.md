# E-Commerce-System
### Develop an e-commerce system for selling technology devices integrated a chatbot and data analysis.
- Link website on Heroku cloud: https://lclshop.herokuapp.com/
- Link backup: https://lclshop.up.railway.app/

#### Technology used in project 
- Frontend: HTML,CSS, JavaScript, Boostrap 4.
- Backend: Django framework
- Database: PostgresSQL
- Cloud: Heroku, AWS.
- Tools: Docker, GitHub, Postman.

### The LCL Shop system has two distinct roles: customers and administrators, each with its own set of functions.
#### The functions that customers can perform are:
- View list of products: Display a list of available products with their names, images, and prices.
- View about us: Show information about the store, its history, and mission.
- View terms and conditions and privacy policy: Provide the legal terms and policies that govern the use of the website.
- Send feedback to administrator: Allow customers to share their opinions, suggestions, and complaints with the website's administrator.
-	View related products: Show products that are related to the one being viewed.
-	View recommended products: Show products that the website recommends based on customer reviews.
-	View best-selling products: Display the most popular products based on the number of sales.
-	Login: Enable registered customers to access their accounts by entering their username and password.
-	Register (verified via email): Allow new customers to create an account and verify their email address.
-	Forgot password (verified via email): Allow customers to reset their password after verifying their email address.
-	Edit Profile: Allow customers to modify their personal information, such as name, email, address, and phone number.
-	Change Email (verified via email): Allow customers to change their email address after verifying their new email.
-	Change Password: Allow customers to change their password after verifying their current password.
-	Register newsletter: Allow customers to subscribe to the website's newsletter to receive updates and promotions.
-	Manage delivery address: Allow customers to manage their delivery addresses by adding, updating, deleting, and searching for addresses. They can also set a default address.
-	Captcha verified when login and register: Verify that the user is human and prevent spam and bots.
-	View product details: Show detailed information about a specific product, including its description, specifications, and reviews.
-	Search product: Allow customers to search for products by entering keywords.
-	Sort products by name, price, most viewed, best seller, newest: Allow customers to sort products based on different criteria.
-	Filter products by brand: Allow customers to filter products based on their brand.
-	Filter products by category: Allow customers to filter products based on their category.
-	Filter products by price range: Allow customers to filter products based on their price range.
-	Review product: Allow customers to add, update, and delete their reviews of products.
-	Pagination for list of products: Break the list of products into smaller pages to make it easier to navigate.
-	Manage cart: Allow customers to add products to their cart, view their cart, update the quantity of products, and remove products from their cart.
-	Manage wishlist: Allow customers to add products to their wishlist, delete products from their wishlist, and add all products from their wishlist to their cart.
-	Apply coupon for orders and remove coupon from orders: Allow customers to apply a coupon code to their order to receive a discount and remove the coupon code from their order.
-	Checkout: Guide customers through the process of selecting a delivery address, reviewing their cart, selecting a payment method, and placing their order.
-	Track orders: Allow customers to view the status and details of their orders, cancel orders that are still pending, and search for their orders.
-	Export invoice in PDF format: Allow customers to download a PDF version of their invoice.
-	Send email to customer and owner when customer order product: Notify the customer and the website owner via email when a customer places an order.
-	Chatbot: Provide an AI-powered chatbot that can answer common customer questions, provide product recommendations, and help customers navigate the website.
#### The function of administrator includes:
- Login: The administrator can log in to access the backend system.
- Forgot password (verified via email): The administrator can reset their password via email verification.
-	Edit Profile: The administrator can edit their profile information such as name and contact details.
-	Change Email (verified via email): The administrator can change their email address via email verification.
-	Change Password: The administrator can change their password.
-	Customer Management: The administrator can view details, search, add, update, update password, delete, delete selected, export data (with CSV, Excel, JSON format).
-	Category Management: The administrator can view, search, add, update, delete, delete selected, export data (with CSV, Excel, JSON format).
-	Brand Management: The administrator can view details, search, add, update, delete, delete selected, export data (with CSV, Excel, JSON format).
-	Product Management: The administrator can view details, search, add, update, delete, delete selected, export data (with CSV, Excel, JSON format), sort products by name, price, most viewed, best seller, newest, filter products by brand, filter products by category, filter products by price range.
-	Orders Management: The administrator can update order status, view order details, delete, search, delete selected, export data (CSV, Excel, JSON), export invoice with PDF format.
-	Payment Management: The administrator can update payment status, view details, search, export data (CSV, Excel, JSON).
-	Review Management: The administrator can change review status, view details, delete, search, delete selected, export data (CSV, Excel, JSON).
-	Coupon Management: The administrator can view, search, add, update, delete, delete selected, export data (with CSV, Excel, JSON format).
-	Feedback Management: The administrator can view details, delete, search, delete selected, export data (CSV, Excel, JSON).
-	Chatbot Management: The administrator can manage the chatbot, including chatting with the chatbot and managing it in Dialogflow.
-	Dashboard: The administrator can view sales statistics (total products, total views, total customers, total sold, total sales, total profit, total profit ratio, total discounts, total orders, totals feedbacks, total reviews, total payments), view recent orders, view recent customers.
-	Sales Statistic: The administrator can view sales statistics (total products, total views, total customers, total sold, total sales, total profit, total profit ratio, total discounts, total orders, totals feedbacks, total reviews, total payments) , chart sales and profit per monthly, statistics of the top 10 best-selling products, statistics of the top 10 profitable products, statistics of the top 10 most viewed products, statistics of the top 10 rated products, sales statistics by month or specific time period.
-	Forecast sales and profit next month: The administrator can predict sales and profit for the next month based on sales statistics.

## Installation
**1. Clone Repository & Install Packages**
```sh
git clone https://github.com/lechiluan/ecommerce.git
pip install virtualenv
```
**2. Setup Virtualenv**
```sh
virtualenv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
**3. Migrate & Start Server**
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Where to find Me
Like Me on [Facebook](https://www.facebook.com/chiluanit/), [GitHub](https://github.com/lechiluan).
