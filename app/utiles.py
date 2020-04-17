# 辅助函数utilities.py 叫 helpers.py也可以
# redirect_back() 重定向回上一个页面
# 比如用户登录后重定向到之前浏览页
# url_safe()验证url安全

# 获取上一个页面url方法
# ①从request.args.get('next')获得当前页面完整路径 默认next=request.full_path
# ②从request.referer 获得请求发源地HTTP首部字段
#  这个不靠谱会刷新 比如下一页下一页引导其刷新的时候 最开始的referer就没了o(╥﹏╥)o
# HTTP_REFERER记录用户所在原站点url 还是用来追踪用户都从哪里进来的你网站
# 可搭配使用




# 因为在当前页有骚操作不一定能
# 如果获取上一个页面成功就重定向到上一个页面
# 运气不好上一个页面找不到了
def admin_redirect_back(default="dashboard", **kwargs):
    target=request.args.get('next')
    if is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))


def redirect_back(default="home", **kwargs):
    target=request.args.get('next')
    if is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default, **kwargs))