class Dog:
    def __init__(self, name):
        self.name = name

    def play(self):
        func_name = self.play.__name__
        print(func_name, type(func_name))


d = Dog("a")
d.play()
