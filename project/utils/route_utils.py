#keep track of which blueprints have which routes
class Group:
    def __init__(self, **entries): self.__dict__.update(entries)

index = 'main.index'
login = 'auth.login'
logout = 'auth.logout'
register = 'auth.register'
profile = 'main.profile'
wordGame = 'game.wordGame'
solve = 'game.solve'

puzzle = Group(
    create='game.submitpuzzle',
    get='game.getpuzzle',
    rate='game.ratepuzzle'
)

user = Group(
    current = 'auth.currentuser',
    get = 'auth.getuser',
    follow = 'auth.followuser',
    unfollow = 'auth.unfollowuser'
)