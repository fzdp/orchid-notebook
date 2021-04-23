Simple note-taking app with task/todo management.

### Main window
![main window](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/main_window.png)
### New notebook
![new_notebook](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/new_notebook.png)
### New Task
![new_task](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/new_task.png)
### Task Panel
![task_panel](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/task_list.png)
### Text editor
![text_editor](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/text_editor.png)
### Text search
![text_search](https://raw.githubusercontent.com/fzdp/orchid-notebook/main/assets/demo/text_search.png)

# Features
* Basic note management
* Easy task management
* Multi-language support
* Fully configurable(currently via config.ini file)
* Note content is portable
* Cross platform
* And more...

# Main packages
* GUI framework: [wxPython](https://github.com/wxWidgets/Phoenix)
* ORM: [peewee](https://github.com/coleifer/peewee)
* Full text search: [whoosh](https://github.com/mchaput/whoosh)
* Text editor: [quill](https://github.com/quilljs/quill)
* Webview: [cefpython](https://github.com/cztomczak/cefpython)
* Messaging: [PyPubSub](https://github.com/schollii/pypubsub)
* i18n: [python-i18n](https://github.com/danhper/python-i18n)
* Chinese text segmentation: [jieba](https://github.com/fxsjy/jieba)
* ListView component: [ObjectListView](https://objectlistview-python-edition.readthedocs.io/en/latest/)

# Usage
make sure python version is 3.x, then setup virtual env, run following commands:
```
pip install -r requirements.txt
python main.py
```

config.ini file is in the app data folder

# Todo List
- [ ] Distribute as single App
- [ ] Make UI more beautiful
