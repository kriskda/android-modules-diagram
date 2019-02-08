# Android modules diagram generator
Script to visualize relationships between android modules

![alt text](https://raw.githubusercontent.com/kriskda/android-modules-diagram/master/modules_diagram.png)

## Dependencies
* python
* pygraphviz

## Getting started
```
python generator.py PATH_TO_PROJECT
```
It is possible to generate diagrams ith edges colored based on api/compile or implementation. See `should_draw_colors=True` inside `generator.py`
