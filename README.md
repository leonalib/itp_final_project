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

