from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import *
from ..models import *
from ..serializers import *

def portfolio_list(request, page_num=1):
    items_per_page = 10  # 페이지 당 항목 수

    # 페이지 번호를 이용해 해당 페이지의 포트폴리오 검색
    start_index = (page_num - 1) * items_per_page
    end_index = page_num * items_per_page

    post_portfolio = PostPortfolio.objects.order_by('-id')[start_index:end_index]
    portfolio_lists = []

    query = request.GET.get('search')
    search_type = request.GET.get('search_type')  # 검색 옵션을 가져옵니다

    for portfolio in post_portfolio:
        post = Post.objects.get(id=portfolio.post_id)
        author = UserProfile.objects.get(id=post.author_id)

        if query:
            # 검색 쿼리와 검색 옵션에 따라 검색 결과 필터링
            if search_type == "title_content" and ((query in post.title) or (query in post.content)):
                portfolio_lists.append({
                    'title': post.title,
                    'created_at': post.created_at,
                    'author_id': post.author_id,
                    'post_portfolio': portfolio.id,
                    'author': author.username,
                    'tech_stacks': portfolio.tech_stack,
                })
            elif search_type == "writer" and (query in author.username):
                portfolio_lists.append({
                    'title': post.title,
                    'created_at': post.created_at,
                    'author_id': post.author_id,
                    'post_portfolio': portfolio.id,
                    'author': author.username,
                    'tech_stacks': portfolio.tech_stack,
                })
        else:
            # 검색 쿼리가 없는 경우, 모든 포트폴리오 추가
            portfolio_lists.append({
                'title': post.title,
                'created_at': post.created_at,
                'author_id': post.author_id,
                'post_portfolio': portfolio.id,
                'author': author.username,
                'tech_stacks': portfolio.tech_stack,
            })

    context = {
        "post_lists": portfolio_lists,
        "board_name": "포트폴리오",
        "is_portfolio": True,
    }

    return render(request, 'project_list.html', context)



def portfolio(request, post_portfolio_id=None):
    if post_portfolio_id:
        post_portfolio = get_object_or_404(PostPortfolio, id=post_portfolio_id)
        post = get_object_or_404(Post, id=post_portfolio.post_id)
        author = get_object_or_404(UserProfile, id=post.author_id)
        context = {
            'title': post.title,
            'author': author.username,
            'author_id': author.id,
            'created_at': post.created_at,
            'start_date': post_portfolio.start_date,
            'end_date': post_portfolio.end_date,
            'members': post_portfolio.members,
            'tech_stacks': post_portfolio.tech_stack,
            'ext_link': post_portfolio.ext_link,
            'content': post.content,
            'post_portfolio_id' : post_portfolio_id,
            'post_id': post.id,
        }
        return render(request, 'portfolio.html', context)
    else:
        messages.info('올바르지 않은 접근입니다.')
        return redirect('hanwooplz_app:portfolio_list')

@login_required(login_url='login')
def write_portfolio(request, post_portfolio_id=None):
    if post_portfolio_id:
        post_portfolio = get_object_or_404(PostPortfolio, id=post_portfolio_id)
        post = get_object_or_404(Post, id=post_portfolio.post_id)
    else:
        post_portfolio = PostPortfolio()
        post = Post()
    
    if request.method == 'POST':
        if 'delete-button' in request.POST:
            post.delete()
            return redirect('hanwooplz_app:portfolio_list')
        if 'temp-save-button' in request.POST:
            messages.info(request, '임시저장은 현재 지원되지 않는 기능입니다.')
            context={
                'title': request.POST.get('title'),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'members': request.POST.get('members'),
                'tech_stack': request.POST.get('tech_stack'),
                'ext_link': request.POST.get('ext_link'),
                'content': request.POST.get('content'),
            }
            return render(request, 'write_portfolio.html', context)
        
        request.POST._mutable = True
        request.POST['tech_stack'] = request.POST.get('tech_stack').split()
        post_form = PostForm(request.POST, request.FILES, instance=post)
        post_portfolio_form = PostPortfolioForm(request.POST, request.FILES, instance=post_portfolio)

        if post_form.is_valid() and post_portfolio_form.is_valid():
            post = post_form.save(commit=False)
            post_portfolio = post_portfolio_form.save(commit=False)
            if not post_portfolio_id:
                post.author_id = request.user.id
                post.save()
                post_portfolio.post_id = post.id
                post_portfolio.save()
                post_portfolio_id = post_portfolio.id
            else:
                post.save()
                post_portfolio.save()

            return redirect('hanwooplz_app:portfolio', post_portfolio_id)
        else:
            messages.info(request, '질문을 등록하는데 실패했습니다. 다시 시도해주세요.')
            context={
                'title': request.POST.get('title'),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'members': request.POST.get('members'),
                'tech_stack': request.POST.get('tech_stack'),
                'ext_link': request.POST.get('ext_link'),
                'content': request.POST.get('content'),
            }
            return render(request, 'write_portfolio.html', context)
    else:
        if post_portfolio_id:
            if request.user.id == post.author_id:
                start_date = str(post_portfolio.start_date).replace('년 ','-').replace('월 ','-').replace('일','')
                end_date = str(post_portfolio.end_date).replace('년 ','-').replace('월 ','-').replace('일','')
                context = {
                    'post_portfolio_id': post_portfolio_id,
                    'title': post.title,
                    'start_date': start_date,
                    'end_date': end_date,
                    'members': post_portfolio.members,
                    'tech_stack': ' '.join(post_portfolio.tech_stack),
                    'ext_link': post_portfolio.ext_link,
                    'content': post.content,
                    'post_author_id': post.author_id,
                }
                return render(request, 'write_portfolio.html', context)
            else:
                messages.info('올바르지 않은 접근입니다.')
                return redirect('hanwooplz_app:portfolio', post_portfolio_id)
        else:
            return render(request, 'write_portfolio.html')
