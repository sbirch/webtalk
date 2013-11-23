# got this from stack overflow:
# http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums["len"] = len(sequential)
    return type('Enum', (), enums)
