from flask import Flask, render_template, request, redirect, url_for, session, flash
from services.user_service import UserService
from services.category_service import CategoryService
from services.project_service import ProjectService
from services.reward_tier_service import RewardTierService
from services.pledge_service import PledgeService

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_service = UserService()
        user = user_service.get_user(username)
        user_service.close()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Index: List projects
@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search = request.args.get('search', '')
    category_id = request.args.get('category', None)
    sort = request.args.get('sort', 'newest')
    project_service = ProjectService()
    projects = project_service.get_projects(search, category_id, sort)
    project_service.close()
    category_service = CategoryService()
    categories = category_service.get_categories()
    category_service.close()
    return render_template('index.html', projects=projects, categories=categories, search=search, category=category_id, sort=sort)

# Project detail
@app.route('/project/<project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    project_service = ProjectService()
    project = project_service.get_project(project_id)
    project_service.close()
    if not project:
        flash('Project not found')
        return redirect(url_for('index'))
    reward_tier_service = RewardTierService()
    tiers = reward_tier_service.get_reward_tiers(project_id)
    reward_tier_service.close()
    progress = (project['current_funded'] / project['goal']) * 100 if project['goal'] > 0 else 0

    if request.method == 'POST':
        amount = int(request.form['amount'])
        reward_tier_id = request.form.get('reward_tier_id', None)
        if reward_tier_id:
            reward_tier_id = int(reward_tier_id)
        pledge_service = PledgeService()
        status, reason = pledge_service.add_pledge(session['user_id'], project_id, amount, reward_tier_id)
        if status == 'success':
            flash('Pledge successful')
        else:
            pledge_service.add_rejected_pledge(session['user_id'], project_id, amount, reward_tier_id, reason)
            flash(f'Pledge rejected: {reason}')
        pledge_service.close()
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template('project_detail.html', project=project, tiers=tiers, progress=progress)

# Stats
@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pledge_service = PledgeService()
    success, rejected = pledge_service.get_stats(session['user_id'])
    pledge_service.close()
    return render_template('stats.html', success=success, rejected=rejected)

if __name__ == '__main__':
    app.run(debug=True)