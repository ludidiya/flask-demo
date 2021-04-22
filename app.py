import os
import sys
from flask import Flask, escape, url_for, render_template, request, flash, redirect
# 1）从 flask 包导入 Flask 类，通过实例化这个类，创建一个程序对象 app
# 2）escape() 函数可对用户恶意输入代码进行转义
# 3）Flask 提供了一个 url_for 函数来生成 URL，它接受的第一个参数就是端点值，默认为视图函数的名称
# 4）使用 render_template() 函数可以把模板渲染出来，必须传入的参数为模板文件名
# 5）request: Flask 会在请求触发后把请求信息放到 request 对象里，你可以从 flask 包导入它
#          它包含请求相关的所有信息
#          比如请求的路径（request.path）
#          请求的方法（request.method）
#          表单数据（request.form）
#          查询字符串（request.args）等等。
# 6）lash() 函数用来在视图函数里向模板传递提示消息，get_flashed_messages() 函数则用来在模板中获取提示消息。
# 7）redirect() ：重定向响应是一类特殊的响应，它会返回一个新的 URL，浏览器在接受到这样的响应后会向这个新 URL 再次发起一个新的请求。
#          Flask 提供了 redirect() 函数来快捷生成这种响应
#          传入重定向的目标 URL 作为参数，比如 redirect('http://helloflask.com')。

from flask_sqlalchemy import SQLAlchemy
# 导入扩展类:
# 借助 SQLAlchemy，你可以通过定义 Python 类来表示数据库里的一张表（类属性表示表中的字段 / 列）
# 通过对这个类进行各种操作来代替写 SQL 语句。这个类我们称之为模型类，类中的属性我们将称之为字段。

# 设置数据库URI
# 为了设置 Flask、扩展或是我们程序本身的一些行为，我们需要设置和定义一些配置变量。
# Flask 提供了一个统一的接口来写入和获取这些配置变量：Flask.config 字典。
# 配置变量的名称必须使用大写，写入配置的语句一般会放到扩展类实例化语句之前。


WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。
# session 用来在请求间存储数据,它会把数据签名后存储到浏览器的 Cookie 中
# 所以我们需要设置签名所需的密钥：
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里，在部署章节会详细介绍。
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请在命令行窗口查看输出的 URL）：
    print(url_for('index'))  # 输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'


# 创建数据库模型
class User(db.Model):
    # 模型类要声明继承 db.Model
    # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


# 在Flask内自定义命令
import click
# 创建数据库表和表内虚拟数据
@app.cli.command()  # 注册为命令
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


# 模板上下文处理函数
# 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用。
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}

# 用app.errorhandler() 装饰器注册一个错误处理函数
# 它的作用和视图函数类似，当 404 错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404   # 返回模板和状态码（404.html中user变量已通过‘模板上下文处理函数’传递）

# # 在主页试图读取数据库记录
# @app.route('/')
# def index():
#     movies = Movie.query.all()
#     return render_template('index.html', movies=movies) # user变量已通过‘模板上下文处理函数’传递

# 创建条目
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        # request.form 是一个特殊的字典，用表单字段的 name 属性值可以获取用户填入的对应数据
        year = request.form.get('year')
        # 验证数据
        # 通过在 <input> 元素内添加 required 属性实现的验证（客户端验证）并不完全可靠，我们还要在服务器端追加验证：
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

# 修改条目
# <int:movie_id>: int是将变量转换成整型的 URL 变量转换器
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    # get_or_404() 方法，它会返回对应主键的记录，如果没有找到，则返回 404 错误响应。
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页