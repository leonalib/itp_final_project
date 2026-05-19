#  CakeHelper — Telegram Cake Order Bot (OOP Version)

A Telegram-based cake ordering bot with **Object-Oriented Architecture, PostgreSQL database, and admin management system**.

---

##  Project Description

CakeHelper is a Telegram bot that allows customers to order custom cakes step-by-step without leaving Telegram.

The project was redesigned using **OOP principles (Object-Oriented Programming)** to improve structure, scalability, and maintainability.

Customers can:

* choose cake options
* upload design photos
* add special requests
* confirm orders

Admins can:

* manage orders
* update order status
* view statistics
* communicate with customers

---

##  Features

###  Customer Side

* 🍰 Choose cake flavor (Chocolate, Vanilla, Red Velvet, Honey, Berry, Custom)
* 📏 Select size (Small / Medium / Large / Custom)
* 📸 Upload cake design image
* ✏️ Add extras (messages, allergies, notes)
* 📋 Order summary before confirmation
* 🔔 Automatic status updates

---

###  Admin Side

* 📩 Instant notifications for new orders
* ✅ Accept / ❌ Decline orders
* 🔧 Manage order status (New → In Progress → Ready → Delivered)
* 📊 Statistics dashboard
* 👤 View full order details
* 💬 Direct message to customer

---

##  OOP Architecture 

The system is built using Object-Oriented Programming.

###  Core Classes

**BaseOrder**

* Stores common order data
* Handles status management
* Provides serialization (to_dict / from_dict)

**CakeOrder (inherits BaseOrder)**

* Cake-specific fields:

  * flavor
  * size
  * photo_id
  * extras

**CustomOrder (inherits CakeOrder)**

* Extended order type
* Adds manual review flag

---

###  Design Patterns

**Factory Pattern**

* OrderFactory creates correct order type automatically

**Repository Pattern**

* OrderRepository handles:

  * JSON backup
  * CSV export/import

---

##  Database (PostgreSQL)

### Orders Table

* id
* chat_id
* username
* flavor
* size
* photo_id
* extras
* status
* created_at

---

##  System Workflow

1. User starts bot (/start)
2. User selects cake flavor
3. User selects size
4. User uploads image
5. User adds extras
6. System creates `CakeOrder` object (OOP layer)
7. Order is saved in PostgreSQL
8. (Optional) backup saved in JSON/CSV
9. Admin receives notification
10. Admin updates order status
11. User receives updates

---

##  Technologies Used

| Technology           | Purpose                   |
| -------------------- | ------------------------- |
| Python 3             | Core programming language |
| pyTelegramBotAPI     | Telegram bot framework    |
| PostgreSQL           | Database                  |
| psycopg2             | Database connection       |
| OOP (Python Classes) | System architecture       |
| JSON / CSV           | Backup & export system    |

---

##  Project Structure

```
Cake_Helper/
├── main.py              # Bot entry point
├── config.py            # Token + DB settings
├── handlers.py          # Customer interaction logic
├── admin.py             # Admin panel logic
├── database.py          # PostgreSQL functions
├── models.py            # OOP models (NEW)
│   ├── BaseOrder
│   ├── CakeOrder
│   ├── CustomOrder
│   ├── OrderFactory
│   └── OrderRepository
└── README.md
```

---

##  How to Run

### 1. Clone repository

```bash
git clone <repo_link>
cd Cake_Helper
```

### 2. Install dependencies

```bash
pip install pyTelegramBotAPI psycopg2-binary
```

### 3. Create database

```sql
CREATE DATABASE "Cake_Helper";
```

### 4. Configure config.py

```python
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [YOUR_TELEGRAM_ID]

DB_NAME = "Cake_Helper"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
```

### 5. Run bot

```bash
python main.py
```

---

##  Testing & Debugging

* Manual testing via Telegram bot
* Admin panel verification
* PostgreSQL database checks
* JSON/CSV backup validation

---

##  Future Improvements

* 💳 Payment system integration
* 📍 Delivery tracking
* 🌍 Multi-language support
* 📱 Web dashboard for admins
* 📊 Advanced analytics system

---
## Screenshots
<img width="1280" height="988" alt="5366cf82-2a3f-40b3-b79a-830603137b96" src="https://github.com/user-attachments/assets/79a5050f-f659-46cb-9e22-af211fe047d9" />

### Main Menu

This is the starting interface of the bot where users can begin the cake ordering process by selecting options from inline buttons.

<img width="1280" height="973" alt="ecd6937d-66e5-4ca2-981e-dcd391eb48b0" src="https://github.com/user-attachments/assets/2d2a67df-c742-4568-a632-64459decb336" />

### Order Flow

This section shows the step-by-step ordering process, including flavor selection, size selection, and additional preferences.

<img width="1280" height="832" alt="f06fe535-f111-4d65-82a2-78a8b02e6006" src="https://github.com/user-attachments/assets/fa5473b8-7879-4f99-a3d0-896f0fc53dad" />

### Admin Panel

This interface is used by administrators to manage orders, update statuses, and control the order workflow.

<img width="1280" height="832" alt="fc09ba6d-776b-4624-966e-0a375df56846" src="https://github.com/user-attachments/assets/b09a295c-6632-48ca-b535-5d199a4bf075" />

### Database

This screenshot shows the PostgreSQL orders table where all customer orders are stored and managed.

##  Team Members

###  Aruzhan Manatova
* Developed the admin panel for order management
* Worked on project documentation
* Participated in the OOP module implementation
* Contributed to bot design and interface development
###  Aisha Yerkinbek
* Developed the customer flow in the Telegram bot
* Worked with the database module
* Participated in the OOP module implementation
* Assisted in testing and debugging
---

##  Latest Update

The project was upgraded from a procedural bot to a **fully OOP-based system** with:

* Object-Oriented classes
* Factory Pattern
* Repository Pattern
* JSON/CSV persistence layer
* Improved architecture and scalability

