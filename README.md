# Library Service API Project

## Overview

The Library Service API is designed to modernize and optimize the management of book borrowings in a library. This system 
replaces the outdated manual tracking of books, borrowings, users, and payments with an online solution. The main goal is 
to make the service user-friendly and efficient for both library administrators and users.

## Features
### Functional:
- Web-based
- Manage books inventory
- Manage books borrowing
- Manage customers
- Display notifications
- Handle payments

### Non-functional:
- 5 concurrent users
- Up to 1000 books
- 50k borrowings/year
- ~30MB/year

## Components:
Books Service:
Managing books amount (CRUD for Books)
API:
```
POST:            books/           - add new 
GET:             books/           - get a list of books
GET:             books/<id>/      - get book's detail info 
PUT/PATCH:       books/<id>/      - update book (also manage inventory)
DELETE:          books/<id>/      - delete book
```

Users Service:
Managing authentication & user registration
API:
```
POST:           users/                   - register a new user 
POST:           users/token/             - get JWT tokens 
POST:           users/token/refresh/     - refresh JWT token 
GET:            users/me/                - get my profile info 
PUT/PATCH:      users/me/                - update profile info 
```

Borrowings Service:
Managing users' borrowings of books
API:
```
POST:             borrowings/   		                 - add new borrowing 
                                                           (when borrow book - inventory should be made -= 1) 
GET:              borrowings/?user_id=...&is_active=...  - get borrowings by user id and whether is borrowing 
                                                           still active or not.
GET:              borrowings/<id>/  			         - get specific borrowing 
POST: 	          borrowings/<id>/return/ 		         - set actual return date (inventory should be made += 1)
```

Notifications Service (Telegram):
- Notifications about new borrowing created, borrowings overdue & successful payment
- In parallel cluster/process (Django Q package or Django Celery will be used)
- Other services interact with it to send notifications to library administrators.
- Usage of Telegram API, Telegram Chats & Bots.

Payments Service (Stripe):
Perform payments for book borrowings through the platform.
Interact with Stripe API using the `stripe` package.
API:
```
GET:		success/	- check successful stripe payment
GET:		cancel/ 	- return payment paused message 
```
