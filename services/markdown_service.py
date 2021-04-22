import re
import os.path
import markdown
from utils import ApplicationUtil

class MarkdownService:
    @staticmethod
    def strip_markdown_tags(markdown_content):
        return re.sub(r'<.*?>', '', markdown.markdown(markdown_content))

    def __init__(self):
        exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
                'markdown.extensions.toc']
        self.markdown = markdown.Markdown(extensions=exts)
        self.html_template = None
        with open(os.path.join(ApplicationUtil.bundle_dir(), 'assets', 'markdown_template.html'), 'r') as tpl:
            self.html_template = tpl.read()

    def render(self, markdown_content):
        return self.html_template % self.markdown.convert(markdown_content)

