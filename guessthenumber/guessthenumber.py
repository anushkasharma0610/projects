import random
print ("Hello there!")
r = input ("Enter a number: ")
if r.isdigit():
    r = int(r)
else: 
    print("Enter a digit next time")
range = random.randint(0,r)
guesses=0
while True:
    a = input("Your guess: ")
    guesses+=1

    if a.isdigit():
        a = int(a)
    else: 
        print("Enter a digit next time")
        continue
    if range == a:
        print("You got it! In ",guesses,"guesses")
        break
    else:
        print("guess again")



