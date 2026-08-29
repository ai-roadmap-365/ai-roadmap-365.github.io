# Refactor THIS file for readability without changing what it does.
# The numbered steps are in starter/refactor-worksheet.md. After every step,
# run  bash tests/run_tests.sh  and confirm the output is still identical.
# It works today; your job is to make it readable, not to change its behaviour.
import sys
def d(a):
    l=[]
    for i in a:
        l.append(float(i))
    if len(l)==0:
        print("no data")
        return 1
    t=0
    for i in l: t=t+i
    m=t/len(l)
    s=sorted(l)
    if len(l)%2==1:
        md=s[len(l)//2]
    else:
        md=(s[len(l)//2-1]+s[len(l)//2])/2
    v=0
    for i in l:
        v=v+(i-m)**2
    v=v/len(l)
    sd=v**0.5
    p=0
    for i in l:
        if i>=60: p=p+1
    print("count: "+str(len(l)))
    print("mean: "+format(m,".2f"))
    print("median: "+format(md,".2f"))
    print("min: "+format(s[0],".2f"))
    print("max: "+format(s[-1],".2f"))
    print("stdev: "+format(sd,".2f"))
    print("passing: "+format(100*p/len(l),".1f")+"%")
    return 0
if __name__=="__main__":
    sys.exit(d(sys.argv[1:]))
