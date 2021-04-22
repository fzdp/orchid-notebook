let FontStyle = Quill.import('attributors/style/font');
FontStyle.whitelist = null;
Quill.register(FontStyle, true);

let SizeStyle = Quill.import('attributors/style/size');
SizeStyle.whitelist = null;
Quill.register(SizeStyle, true);

const Link = Quill.import('formats/link');
Link.PROTOCOL_WHITELIST.push('file');
Quill.register(Link,true);

// 时间戳
class TimeBlot extends Inline {}
TimeBlot.blotName = 'TimeBlot';
TimeBlot.className = 'time-item';
TimeBlot.tagName = 'strong';
Quill.register(TimeBlot);

document.addEventListener('click', (e) => {
   if (e.target && e.target.tagName === 'A') {
       e.preventDefault();
       pyOnLinkClicked(e.target.href);
   }
});

let quill = new Quill('#editor', {
    modules: {
        syntax: true,
        toolbar: false,
        magicUrl: true,
        history: {
            delay: 1500,
            maxStack: 500,
            userOnly: true
        }
    },
    theme: 'snow'
});
let editor = quill.container.firstChild;
let searcher = new Searcher(quill);
quill.isContentLoading = false;

function debounce(func, wait, immediate) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        var later = function() {
          timeout = null;
          if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

let notifyChanged = debounce(function(){
    pyNotifyContentChanged(editor.innerHTML);
}, 900);

quill.on('text-change', function(delta, oldDelta, source){
    if (source === 'api' || quill.isContentLoading) {
        return;
    }
    notifyChanged();
});

quill.on('selection-change', function(type, range){
    pyNotifyFormatChanged(quill.getFormat());
});

quill.findAll = function(keyword) {
    searcher.findAll(keyword);
};

quill.loadContent = function(value){
    quill.isContentLoading = true;
    quill.setContents([]);
    editor.innerHTML = value;
    setTimeout(function () {
        quill.history.clear();
        quill.isContentLoading = false;
    }, 0);
};

quill.insertTime = function(strTime) {
    quill.insertText(quill.getSelection(true), strTime, {'TimeBlot': true}, 'user');
};
