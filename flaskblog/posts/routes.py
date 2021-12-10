from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog import db
from flaskblog.posts.forms import PostsForm
from flaskblog.posts.models import Post
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostsForm()

    # validate form
    if form.validate_on_submit():
        # add pst to db
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Succesful', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New post')


# Posts Route
@posts.route("/post/<int:post_id>")
def post(post_id):
    # Query db for post
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


# Update post
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # Query db
    post = Post.query.get_or_404(post_id)
    # Check if current user is author of the post
    if current_user != post.author:
        abort(403)
    # update post
    form = PostsForm()

    # Validate post after submit
    if form.validate_on_submit():
        #update title and content of post
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Post has been Updated successfully', 'info')
        return redirect(url_for('posts.post', post_id=post.id))
    # if get method render template with current post's data in fields
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='New Post', form=form, legend='Update Post')


# delete post
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # Query db for the post
    post = Post.query.get_or_404(post_id)
    # Check if current user is author of the post
    if current_user != post.author:
        abort(403)

    # Delete post
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted successfully', 'success')
    return redirect(url_for('main.home'))