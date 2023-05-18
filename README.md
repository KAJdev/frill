# frill

Hey there! My name is Frill, and I'm a multi-container docker application built with ❤️ by my creators. I'm designed to be both cheerful and intelligent, and I'm here to make your life easier!

My main components consist of a Discord bot, an executor API for interpreting and running jobs, and databases like Redis and Mongo to keep everything organized and efficient. Let's learn more about each part of my system below!

## Components  🏗️

### Discord bot

I'll be available on your server 24/7, always ready to help out with any task you need, from sending cute fox gifs to responding to various commands. My Discord bot uses the latest Discord API and a powerful Python library for seamless interaction with users. I'm ready to serve you in your favorite Discord channels!

### Executor API for Job Graphs

My executor API allows me to interpret and run job graphs in an efficient and organized way. This means that I can manage and perform tasks with ease, making sure everything runs smoothly, punctually, and according to your needs.

### Redis

Redis is an in-memory data store that helps me quickly access and manipulate data. This super-speedy data store perfectly complements my playful nature and ensures that I respond to your requests quickly and efficiently.

### MongoDB

MongoDB, a document-based database, stores my long-term data. Thanks to MongoDB, I can remember important information and access it whenever needed. This NoSQL database empowers me to store diverse data types and create a flexible, scalable storage system.

## Get Started  🚀

To enjoy the delightful company of a cheerful and intelligent frill on your Discord server, simply:

1. Clone this repository.
```
git clone https://github.com/kajdev/frill.git
```

2. Change to the project's directory.
```
cd frill
```

4. Configure the `.env` file with necessary credentials and settings.
```.env
DISCORD_TOKEN=
OPENAI_TOKEN=
TENOR_TOKEN=
```

5. Run the docker-compose command.
```
docker-compose up
```

Voilà! Now I'm ready to brighten your day with my wit and efficiency. 🧡

## Closing Thoughts 🧡

I hope my delightful persona, helpful nature, and efficient task management add that extra bit of spark to your daily life. If you have any questions or suggestions, please don't hesitate to open an issue or pull request. I'm constantly learning and growing, and I can't wait to become an even better version of myself!🌟
 
### TODO
- [x] executor parser
- [x] executor runtime engine
- [x] executor passthrough to bot
- [x] executor task queue
- [ ] vector DB