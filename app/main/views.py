#coding:utf-8

from flask import render_template, redirect, url_for, abort, flash, \
    current_app, request, make_response, session
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from datetime import date
import calendar
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, \
    CommentForm, AccountForm, PlanForm
from .. import db
from ..models import User, Role, Permission, Post, Comment, Bill, \
    BillDetails
from ..decorators import admin_required, permission_required


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author = current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.uesrname.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    comment = Comment.query.filter_by(post=post).all()
    for c in comment:
        db.session.delete(c)
    db.session.delete(post)
    return redirect(url_for('.index'))

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
         page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

@main.route('/account/query', methods=['GET', 'POST'])
@login_required
def account_query():
    if request.method == 'POST':
        dstr = request.form['date']
        session['dstr'] = dstr
    return redirect(url_for('.account', username=current_user.username))

@main.route('/account/plan', methods=['GET', 'POST'])
@login_required
def account_plan():
    if request.method == 'POST':
        plan = request.form['plan']
        session['plan'] = plan
        print (plan)
    return redirect(url_for('.account', username=current_user.username))

@main.route('/account/delete')
@login_required
def account_delete():
    bdid = request.args.get('bdid')
    bd = BillDetails.query.filter_by(id=bdid).first()
    bill = Bill.query.filter(Bill.details.contains(bd)).first()
    bill.total -= bd.price
    db.session.delete(bd)
    db.session.add(bill)
    return redirect(url_for('.account', username=current_user.username))


@main.route('/account/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    # today 在此代表当天，不一定是今天
    date_today = date.today()
    # dstr = request.args.get('dstr')
    if session['dstr']:
        dstr = session['dstr']
        if dstr:
            ds = dstr.split('-')
            date_today = date(int(ds[0]),
                              int(ds[1]),
                              int(ds[2]))
    if not current_user.plan:
        current_user.plan = 1000
    # if session['plan']:
    #     plan = session['plan']
    #     if plan:
    #         current_user.plan = float(plan)
    #         print ('================>')
    #         print (current_user.plan)
    plform = PlanForm()
    acform = AccountForm()
    if plform.plsubmit.data and plform.validate_on_submit():
        current_user.plan = plform.plan.data
        return redirect(url_for('.account', username=current_user.username))
    elif acform.acsubmit.data and acform.validate_on_submit():
        bill_today = Bill.query.filter_by(date=date_today,
                                          owner=current_user._get_current_object()).first()
        if not bill_today:
            bill_today = Bill(total=0,
                              date=date_today,
                              owner=current_user._get_current_object())
        bill_details_today = BillDetails(goods=acform.goods.data,
                                         price=acform.price.data,
                                         use  =acform.use.data,
                                         owner=bill_today)
        bill_today.total += float(acform.price.data)
        db.session.add(bill_today)
        db.session.add(bill_details_today)
        return redirect(url_for('.account', username=current_user.username))
    bill_today = Bill.query.filter_by(date=date_today,
                                owner=current_user._get_current_object()).first()
    bill_all = Bill.query.filter_by(owner=current_user._get_current_object()).all()

    xAxisList = []
    yAxisList = []
    data = []
    total_month = 0
    for b in bill_all:
        data.append((b.date, b.total))
    data.sort()
    month_now = date.today().month
    for b in data[-31::]:
        xAxisList.append(b[0].day)
        yAxisList.append(b[1])
        if b[0].month == month_now:
            total_month += b[1]

    if len(yAxisList):
        average = round(float(sum(yAxisList)) / len(yAxisList),1)
    yAxisAverage = [average for i in range(len(yAxisList))]
    per_month_days = calendar.monthrange(date.today().year,
                                         date.today().month)[1]
    day_plan = round(current_user.plan / per_month_days, 1)
    yAxisPlan = [day_plan for i in range(len(yAxisList))]


    bd_today_all = []
    if bill_today:
        bd_today_all = BillDetails.query.filter_by(owner=bill_today).all()
        total_today = bill_today.total
    else:
        total_today = 0
    show_what = 'month'
    show_what = request.cookies.get('show_what')
    return render_template('account.html', acform=acform, plform=plform, show_what=show_what,
                           bill_all=bill_all, total_today=total_today, today=date.today(),
                           bd_today_all=bd_today_all, date_today=date_today,
                           xAxisList=xAxisList, yAxisList=yAxisList,
                           yAxisAverage=yAxisAverage, yAxisPlan=yAxisPlan,
                           total_month=total_month, user=current_user)

@main.route('/show_month')
@login_required
def show_month():
    resp = make_response(redirect(url_for('.account', username=current_user.username)))
    resp.set_cookie('show_what', 'month', max_age=30*24*60*60)
    return resp

@main.route('/show_year')
@login_required
def show_year():
    resp = make_response(redirect(url_for('.account', username=current_user.username)))
    resp.set_cookie('show_what', 'year', max_age=30*24*60*60)
    return resp
