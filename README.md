# Quiz Maker Demo App

This app allows you to create and play with fun trivia-style quizzes.
It comes in 3 modes: a question-answer matching game, a guessing game based on picture clues, and a video question game.

Built with Django and Python, this app demonstrates:
- Domain-driven design implementation for the core entities to encapsulate business logic
- Factory and repository patterns for extensibility of models, and mapping to their respective entities
- Custom class-based views for abstracting common functionalities
- Usage of Django Forms for validation and handling of data
- Image processing using Pillow
- Environment-based configuration for ease of collaboration
- jQuery for simple UI interaction, custom template filters, MVC-style pattern

For deployment: uWSGI on Nginx, Postgresql, pyenv, Python 3.7, OpenSUSE LEAP 15.2

**Disclaimer:** This demo source code is only a subset of the original code.
