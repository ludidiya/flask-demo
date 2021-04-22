# 静态文件夹
静态文件（static files）和我们的模板概念相反，指的是内容不需要动态生成的文件。比如图片、CSS 文件和 JavaScript 脚本等。
在 Flask 中，我们需要创建一个 static 文件夹来保存静态文件，它应该和程序模块、templates 文件夹在同一目录层级。

在 HTML 文件里，引入这些静态文件需要给出资源所在的 URL。为了更加灵活，这些文件的 URL 可以通过 Flask 提供的 `url_for()` 函数来生成。

`url_for()` 函数的用法，传入端点值（视图函数的名称）和参数，它会返回对应的 URL。对于静态文件，需要传入的端点值是 static，同时使用 filename 参数来传入相对于 static 文件夹的文件路径。

假如我们在 static 文件夹的根目录下面放了一个 foo.jpg 文件，下面的调用可以获取它的 URL：

```angular2html
<img src="{{ url_for('static', filename='foo.jpg') }}">
```

花括号部分的调用会返回 `/static/foo.jpg`。

> **提示** 在 Python 脚本里，url_for() 函数需要从 flask 包中导入，而在模板中则可以直接使用，因为 Flask 把一些常用的函数和对象添加到了模板上下文（环境）里。

