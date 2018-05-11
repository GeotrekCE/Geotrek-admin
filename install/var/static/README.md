Static files add here can be accessed in your extra templates with django static relative path

example with your logo.png :

```html
{% load static %}

<img src="{% static 'logo.png' %}"/>

```