Project Report — CakeHelper Telegram Bot
1. Problem Statement

Small bakeries need a simple and organized system to receive and manage cake orders. Manual order handling through Telegram messages often leads to confusion, lost orders, and lack of tracking.

2. Solution Overview

CakeHelper is a Telegram bot that automates the cake ordering process.

Users can place orders step-by-step (flavor, size, photo, extras), and all data is stored in a PostgreSQL database.

Admins can:

View and manage orders
Update order status (New → In Progress → Ready → Delivered)
Receive notifications for new orders
Track statistics

The system is built using Object-Oriented Programming (OOP) for better structure and maintainability.

3. System Design Overview

The system consists of:

main.py — bot entry point
handlers.py — customer order flow
admin.py — admin panel
database.py — database operations
models.py — OOP order classes

Flow:
User → Bot → Order creation → Database → Admin panel → Status update → User notification

4. Challenges Faced
Managing user states in Telegram conversation flow
Handling callback buttons correctly
Structuring database for order tracking
Integrating OOP design into bot logic
Debugging message flow between user and admin
5. Team Contributions

Aruzhan Manatova

Admin panel development
Documentation
OOP module participation
Bot interface design

Aisha Yerkinbek

Customer flow development
Database integration
OOP module participation
Testing and debugging
6. Conclusion

CakeHelper successfully automates cake ordering using Telegram bot technology, PostgreSQL database, and OOP architecture, improving order management efficiency and system structure.
