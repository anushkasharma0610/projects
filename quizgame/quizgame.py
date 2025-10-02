print("Decoding Slang abbreviations!")

play=input("Do you want to play(y/n): ")
if  play.lower()!="y":
    quit()

score = 0
outof = 5
print("Lets begin!")

answer=input("YOLO: ")
if answer.lower()=="you only live once":
    print("Correct")
    score+=1
else: 
    print("Incorrect:- you only live once")

answer=input("FOMO: ")
if answer.lower()=="fear of missing out":
    print("Correct")
    score+=1
else: 
    print("Incorrect:- fear of missing out")

answer=input("FYI: ")
if answer.lower()=="for your information":
    print("Correct")
    score+=1
else: 
    print("Incorrect:- for your information")

answer=input("TBH: ")
if answer.lower()=="to be honest":
    print("Correct")
    score+=1
else: 
    print("Incorrect:- to be honest")

answer=input("BRB: ")
if answer.lower()=="be right back":
    print("Correct")
    score+=1
else: 
    print("Incorrect:- be right back")

print ("Your score is "+str(score)+ " out of "+str(outof))