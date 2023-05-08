# FoodAnalyzer

Many people are dealing with intolerances to food. However, it can be tricky to
figure out what one is reacting to. During the day, one consumes various foods
and there is a delay between eating the food and experiencing symptoms. Thus,
when one experience a reaction, it is can be challenging to figure out which of
the things one ate caused the reaction.

This application strives to:

- make it easy for the user to keep a diary of what he eats and his reactions
- help the user determine what in his diet he is reacting to

## Setup

```
pip install --requirement requirements.txt
python3 manage.py makemigrations foodapp
python3 manage.py migrate
python3 manage.py runserver
```
