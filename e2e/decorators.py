from functools import wraps

def logged(func):
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

def adder(a,b):
    return a+b

num = logged(adder)
print(num.__name__)
print(num(2,3))

@logged
def mult(a,b):
    return a*b

print(mult.__name__)
print(mult(5,6))

def loggedV1(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

@loggedV1
def div(a,b):
    return a/b

print(div.__name__)
print(div(5,10))


for i in range(3):
    print(i)



# pip3 install virtualenv
# pip install pyyaml
# pip install eks-auth
# virtualenv lambdaLayer
# source lambdaLayer/bin/activate                    boto3, datetime,kubernetes




