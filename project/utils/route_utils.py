#keep track of which blueprints have which routes
class Group:
    def __init__(self, **entries): self.__dict__.update(entries)

index = 'main.index'
login = 'auth.login'
logout = 'auth.logout'
register = 'auth.register'
profile = 'main.profile'

puzzle = Group(
    play = 'game.page_play_puzzle',
    create='game.page_create_puzzle',
    get='game.api_get_puzzle',
    rate='game.api_rate_puzzle',
    search = 'game.api_search_puzzle',
    solve = 'game.api_solve_puzzle'
)

user = Group(
    current = 'auth.api_current_user',
    get = 'auth.api_get_user',
    follow = 'auth.api_follow_user',
    unfollow = 'auth.api_unfollow_user'
)