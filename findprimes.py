import math

def rem_composite_odds(c):
    comp= []
    for i in c:
        for j in c:
            if i %j ==0 and i!=j:
                # print('found mod')
                # print(i,j)
                if i > j:
                    comp.append(i)
                else:
                    c.append(j)
    return c


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


n = 112272535095293
# b = math.ceil(n/2)
# c = [d for d in range(3, b+1) if d%2!=0]
# c.insert(0,2)
# li = []
# rem_composite_odds(c)
# for i in c:
#     if n%i ==0:
#         li.append(i)
#         print('n is composite by {0}'.format(i))
# print(li)
print(is_prime(n))