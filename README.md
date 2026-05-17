#  CakeHelper — Telegram Cake Order Bot
 
A Telegram bot that lets customers order custom cakes step by step, and gives admins a full management panel to track, update, and communicate on every order.
 
---
 
##  Project Description
 
CakeHelper is a Telegram-based ordering system for a custom cake bakery. Customers can choose a flavor, size, upload a design photo, and add special requests — all without leaving Telegram. Admins receive instant notifications for each new order and can manage the entire order lifecycle from a dedicated admin panel.
---
 
##  Features
 
**Customer Side:**
- Choose from preset cake flavors (Chocolate, Vanilla, Red Velvet, Honey, Berry) or enter a custom flavor
- Choose size (Small / Medium / Large / Custom)
- Upload a reference photo of the desired cake design
- Add extras (inscription, allergies, special wishes)
- Review an order summary before confirming
- Receive automatic status updates at every stage (In Progress → Ready → Delivered)

**Admin Side:**
- Instant notification on every new order with photo and details
- One-click Accept or Decline buttons on new orders
- Admin panel with order lists filtered by status (New / In Progress / Ready / All)
- Detailed order view with status advancement controls
- Cancel any active order from the detail view
- Direct "Message Customer" link in each order
- Statistics dashboard: counts by status, last 7 days, last 30 days
---
## Technologies Used
 
| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| pyTeleBot (telebot) | Telegram Bot API wrapper |
| PostgreSQL | Order database |
| psycopg2 | PostgreSQL driver for Python |
 
---
##  Installation
 
**Requirements:**
- Python 3.9 or higher
- PostgreSQL installed and running
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

---
##  Project Structure
 
```
cakebot/
├── main.py        # Entry point — starts the bot
├── config.py      # Token, admin IDs, DB credentials
├── database.py    # All database functions (save, get, update, stats)
├── handlers.py    # Customer-facing conversation flow
├── admin.py       # Admin panel, callbacks, status management
└── README.md
```
 
---
## Installation Instructions
# Step 1 — Clone the repository
git clone <repository_link>
cd Cake_Helper
# Step 2 — Install Python dependencies
pip install pyTelegramBotAPI psycopg2-binary
# Step 3 — Create the PostgreSQL database
CREATE DATABASE "Cake_Helper";
## Step 4 — Configure config.py
TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_IDS = [YOUR_TELEGRAM_USER_ID]

DB_NAME = "Cake_Helper"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
## How to Run
python main.py

After launch, the bot will:

1.Connect to the PostgreSQL database

2.Create the orders table if it does not exist

3.Register customer and admin handlers

4.Start polling Telegram messages

### Open Telegram, find your bot, and send:

/start
## Example Workflow
User starts the bot
User chooses cake flavor
User selects cake size
User uploads a cake photo
Order is saved into the database
Admin manages the order status

## Screenshots
<img width="1280" height="988" alt="f2bfb444-1557-4a24-b3c3-90213dfcc454" src="https://github.com/user-attachments/assets/ca71f417-2118-4fd5-9d8d-3f235423c910" />

## Main Menu
Main interface where users start ordering cakes.
<img width="1280" height="973" alt="5b75c3bf-877e-49ee-93b5-94932b0d0ad5" src="https://github.com/user-attachments/assets/97beff37-4074-4b0f-9118-394554ed9c8d" />

## Cake Selection
Users choose cake flavor, size, and extras.

<img width="1280" height="832" alt="68e89cfb-636b-4f81-ac20-e4d353ac0848" src="https://github.com/user-attachments/assets/cf2f5d50-bcab-404b-8712-845bce7e1e0c" />

## Admin Panel
Admin interface for managing customer orders and statuses.

<img width="1280" height="832" alt="02e282c4-b203-4f69-8780-a3881e5088ea" src="https://github.com/user-attachments/assets/b2d40b10-b2c8-41e2-a607-0f37f8de2459" />

## Database Table
PostgreSQL table storing all order information.


#  Team Member Roles

##  Aruzhan Manatova
- Admin panel development
- Bot design and interface
- Documentation and README preparation

##  Aisha Yerkinbek
- Customer flow development
- Telegram bot functionality
- Database integration

---

#  Testing and Debugging

Testing and debugging were completed collaboratively by all team members.

### Future Improvements
- Online payment system
- Delivery tracking
- More cake customization
- Multi-language support

