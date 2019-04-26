
#def run(arg):
def run(*args, **kwargs):
    print("---- Execute run ----")
    print("args: ", args)
    print("kwargs: ", kwargs)
    #krun(**vars(args))
    return 1

def krun(**kwargs):
    print("---- Execute run ----")
    print("Arguments: ", kwargs)
    return 12345
