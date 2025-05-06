from Agent.langChainConfig import chain
class agent:
    def __init__(self, chain=chain):
        self.__chain = chain
    def chain(self):
        return self.__chain

