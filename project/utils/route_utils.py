#keep track of which blueprints have which routes
class Group:
    def __init__(self, **entries): self.__dict__.update(entries)

index = 'main.index'
login = 'auth.login'
logout = 'auth.logout'
register = 'auth.register'
about_us = 'main.about_us'

puzzle = Group(
    info = 'game.page_puzzle_info',
    play = 'game.page_play_puzzle',
    create='game.page_create_puzzle',
    search='game.page_create_search',
    get='game.api_get_puzzle',
    rate='game.api_rate_puzzle',
    find = 'game.api_search_puzzle',
    solve = 'game.api_solve_puzzle',
    random = 'game.page_random_puzzle'
)

user = Group(
    current = 'auth.api_current_user',
    get = 'auth.api_get_user',
    follow = 'auth.api_follow_user',
    unfollow = 'auth.api_unfollow_user',
    profile = 'auth.page_user_profile'
)